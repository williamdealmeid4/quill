"""Inspect captured schemas and fail closed on missing safety capabilities."""

import asyncio
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import cast

from quill.core.errors import DomainError, ErrorCode
from quill.core.models import (
    ErrorInfo,
    ExecutorCapabilities,
    JsonValue,
    ModelCapability,
    SandboxCapabilities,
)

_KNOWN_VERSIONS = frozenset({"0.167.1"})
_REQUIRED_METHODS = frozenset(
    {
        "initialize",
        "thread/start",
        "thread/resume",
        "turn/start",
        "turn/interrupt",
        "model/list",
    }
)


def _failure(message: str, code: ErrorCode = ErrorCode.PROTOCOL_INCOMPATIBLE) -> DomainError:
    return DomainError(ErrorInfo(code=code, message=message, retryable=False, safe_details={}))


def validate_schema_manifest(path: Path) -> None:
    """Verify integrity and the narrowly authorized permission-profile beta contract."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("cli_version") not in _KNOWN_VERSIONS:
            raise _failure("Versão de protocolo não certificada")
        files = value.get("files")
        if not isinstance(files, dict) or not files:
            raise _failure("Manifesto de schema vazio/inválido")
        for relative, digest in files.items():
            if not isinstance(relative, str) or not isinstance(digest, str):
                raise _failure("Entrada de hash inválida")
            candidate = (path.parent / relative).resolve()
            if not candidate.is_relative_to(path.parent.resolve()):
                raise _failure("Path de schema fora do diretório")
            if hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
                raise _failure("Divergência de hash do schema")
        if not _REQUIRED_METHODS.issubset(value.get("supported_methods", [])):
            raise _failure("Métodos obrigatórios ausentes")
        beta = value.get("beta_contract", {})
        if not isinstance(beta, dict) or beta.get("approved") is not True:
            raise _failure("Perfis beta de leitura ainda não autorizados")
        if beta.get("scope") != "permission_profiles_only":
            raise _failure("Escopo beta não certificado")
        required_fields = {
            "v2/ThreadStartParams.json": "permissions",
            "v2/ThreadResumeParams.json": "permissions",
            "v2/TurnStartParams.json": "permissions",
            "v2/CommandExecParams.json": "permissionProfile",
        }
        for filename, field in required_fields.items():
            relative = "permissions-beta/" + filename
            if relative not in files:
                raise _failure("Schema beta obrigatório sem hash")
            schema = json.loads((path.parent / relative).read_text())
            if field not in schema.get("properties", {}):
                raise _failure("Seleção explícita de perfil beta ausente")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise _failure("Captura de schema inválida ou indisponível") from error


def choose_model(
    catalog: tuple[ModelCapability, ...],
    selected_id: str | None,
) -> ModelCapability:
    """Select only an available Sol supporting low; ambiguity requires user selection."""
    candidates = [
        model
        for model in catalog
        if re.search(r"\bsol\b", model.display_name, re.IGNORECASE) and "low" in model.efforts
    ]
    if selected_id is not None:
        candidates = [model for model in candidates if model.id == selected_id]
    if len(candidates) != 1:
        raise _failure(
            "Selecione um modelo Sol disponível com esforço low", ErrorCode.MODEL_UNAVAILABLE
        )
    return candidates[0]


async def _probe(executable: Path, *arguments: str) -> tuple[int, str]:
    allowed = {
        "PATH",
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "CODEX_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "SYSTEMROOT",
        "WINDIR",
        "TEMP",
        "TMP",
    }
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    process = await asyncio.create_subprocess_exec(
        str(executable),
        *arguments,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=environment,
    )
    try:
        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=15)
        return process.returncode or 0, stdout.decode("utf-8", errors="replace")
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()


async def inspect_cli(
    executable: Path,
    *,
    schema_root: Path | None = None,
) -> ExecutorCapabilities:
    """Inspect version/auth only; never start a turn or inherit agent tools."""
    try:
        code, output = await _probe(executable, "--version")
        match = re.fullmatch(r"codex-cli (\d+\.\d+\.\d+)\s*", output)
        if code != 0 or match is None:
            raise _failure("Versão do Codex não reconhecida")
        version = match.group(1)
        auth_code, _ = await _probe(executable, "login", "status")
    except (OSError, TimeoutError) as error:
        raise _failure("Codex indisponível para inspeção", ErrorCode.CODEX_NOT_FOUND) from error
    root = schema_root or Path(__file__).resolve().parents[3] / "schemas/codex"
    manifest = root / version / "manifest.json"
    try:
        validate_schema_manifest(manifest)
    except DomainError as error:
        # No live model catalog is queried while mandatory isolation is unavailable.
        return ExecutorCapabilities(
            cli_version=version,
            schema_digest="",
            authenticated=auth_code == 0,
            available_models=(),
            supported_methods=frozenset(),
            sandbox=SandboxCapabilities(
                available=False,
                restricted_read=False,
                bounded_write=False,
                command_network_block=False,
                backend="blocked",
                reason=error.info.message,
            ),
        )
    catalog = await _read_catalog(executable) if auth_code == 0 else ()
    # Successful schema verification still does not prove the operating-system probes.
    return ExecutorCapabilities(
        cli_version=version,
        schema_digest=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        authenticated=auth_code == 0,
        available_models=catalog,
        supported_methods=_REQUIRED_METHODS,
        sandbox=SandboxCapabilities(
            available=False,
            restricted_read=False,
            bounded_write=False,
            command_network_block=False,
            backend="unverified",
            reason="Contrato beta validado; probes nativos pendentes",
        ),
    )


def parse_catalog(value: JsonValue) -> tuple[ModelCapability, ...]:
    """Validate the external model catalog before creating typed capabilities."""
    if not isinstance(value, dict) or not isinstance(value.get("data"), list):
        raise _failure("Catálogo de modelos inválido")
    result: list[ModelCapability] = []
    data = value["data"]
    assert isinstance(data, list)
    for item in data:
        if not isinstance(item, dict):
            raise _failure("Modelo inválido no catálogo")
        identifier = item.get("model", item.get("id"))
        name = item.get("displayName")
        options = item.get("supportedReasoningEfforts")
        if (
            not isinstance(identifier, str)
            or not isinstance(name, str)
            or not isinstance(options, list)
        ):
            raise _failure("Campos de modelo inválidos")
        efforts: list[str] = []
        for option in options:
            if not isinstance(option, dict) or not isinstance(option.get("reasoningEffort"), str):
                raise _failure("Esforço de modelo inválido")
            effort = option["reasoningEffort"]
            assert isinstance(effort, str)
            efforts.append(effort)
        result.append(ModelCapability(id=identifier, display_name=name, efforts=tuple(efforts)))
    return tuple(result)


async def _read_catalog(executable: Path) -> tuple[ModelCapability, ...]:
    """Read metadata only; no thread, tool call or model turn is created."""
    allowed = {
        "PATH",
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "CODEX_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "SYSTEMROOT",
        "WINDIR",
        "TEMP",
        "TMP",
    }
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    with tempfile.TemporaryDirectory(prefix="quill-inspector-") as directory:
        process = await asyncio.create_subprocess_exec(
            str(executable),
            "app-server",
            "--listen",
            "stdio://",
            "-c",
            'web_search="disabled"',
            "-c",
            "apps._default.enabled=false",
            "-c",
            'approval_policy="on-request"',
            "-c",
            'approvals_reviewer="user"',
            cwd=directory,
            env=environment,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            limit=8 * 1024 * 1024,
        )
        assert process.stdin is not None and process.stdout is not None

        async def request(identifier: int, method: str, params: dict[str, JsonValue]) -> JsonValue:
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(
                (json.dumps({"id": identifier, "method": method, "params": params}) + "\n").encode()
            )
            await process.stdin.drain()
            for _ in range(100):
                line = await asyncio.wait_for(process.stdout.readline(), timeout=15)
                if not line:
                    raise _failure("Conexão de inspeção encerrada")
                message = json.loads(line)
                if not isinstance(message, dict):
                    raise _failure("Resposta de inspeção inválida")
                if message.get("id") == identifier:
                    if "error" in message:
                        raise _failure("Codex recusou consulta de metadados")
                    return cast(JsonValue, message.get("result"))
                if "id" in message:
                    raise _failure("Request inesperado na inspeção sem ferramentas")
            raise _failure("Limite de mensagens da inspeção excedido")

        try:
            await request(
                1, "initialize", {"clientInfo": {"name": "quill_inspector", "version": "0.1.0"}}
            )
            process.stdin.write(b'{"method":"initialized"}\n')
            await process.stdin.drain()
            models = await request(2, "model/list", {"limit": 100, "includeHidden": False})
            if isinstance(models, dict) and models.get("nextCursor") is not None:
                raise _failure("Catálogo paginado exige inspeção completa antes da seleção")
            return parse_catalog(models)
        except (ValueError, TimeoutError, OSError) as error:
            raise _failure("Inspeção de metadados indisponível") from error
        finally:
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            except TimeoutError:
                process.kill()
                await process.wait()
