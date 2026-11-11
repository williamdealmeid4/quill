"""Inspect captured schemas and fail closed on missing safety capabilities."""

import asyncio
import hashlib
import json
import os
import re
from pathlib import Path

from quill.core.errors import DomainError, ErrorCode
from quill.core.models import ErrorInfo, ExecutorCapabilities, ModelCapability, SandboxCapabilities

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
    """Verify capture integrity and required stable read-access policy fields."""
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
        schema = json.loads((path.parent / "v2/TurnStartParams.json").read_text())
        variants = schema["definitions"]["SandboxPolicy"]["oneOf"]
        properties = {
            item["properties"]["type"]["enum"][0]: item["properties"] for item in variants
        }
        if (
            "access" not in properties.get("readOnly", {})
            or "readOnlyAccess" not in properties.get("workspaceWrite", {})
            or "readableRoots" not in json.dumps(schema)
        ):
            raise _failure("Controle obrigatório de leitura restrita ausente no schema instalado")
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
    # Successful schema verification still does not prove the operating-system probes.
    return ExecutorCapabilities(
        cli_version=version,
        schema_digest=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        authenticated=auth_code == 0,
        available_models=(),
        supported_methods=_REQUIRED_METHODS,
        sandbox=SandboxCapabilities(
            available=False,
            restricted_read=True,
            bounded_write=False,
            command_network_block=False,
            backend="unverified",
            reason="Probes nativos pendentes",
        ),
    )
