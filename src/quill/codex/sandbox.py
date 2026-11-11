"""Beta permission profiles and disposable Linux isolation probes."""

import asyncio
import json
import os
import shutil
import signal
import socket
import tempfile
import tomllib
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from quill.core.errors import DomainError, ErrorCode
from quill.core.models import ErrorInfo, JsonValue, PermissionMode, SandboxCapabilities

_DISABLED_FEATURES = (
    "hooks",
    "plugins",
    "remote_plugin",
    "apps",
    "browser_use",
    "computer_use",
    "multi_agent",
    "multi_agent_v2",
    "use_legacy_landlock",
    "daemon_auto_start",
)
_ENVIRONMENT = frozenset(
    {
        "PATH",
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "CODEX_HOME",
        "SYSTEMROOT",
        "WINDIR",
        "TEMP",
        "TMP",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
    }
)


def _failure(message: str) -> DomainError:
    return DomainError(
        ErrorInfo(
            code=ErrorCode.SANDBOX_UNAVAILABLE, message=message, retryable=False, safe_details={}
        )
    )


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """Only test-fixture output is returned by this native probe harness."""

    exit_code: int
    stdout: str
    stderr: str


def _mcp_inventory(workspace: Path) -> tuple[str, ...]:
    paths = {
        Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml",
        Path("/etc/codex/config.toml"),
    }
    paths.update(parent / ".codex/config.toml" for parent in (workspace, *workspace.parents))
    names: set[str] = set()
    for path in paths:
        if path.is_file():
            try:
                config = tomllib.loads(path.read_text())
            except (OSError, ValueError) as error:
                raise _failure("Inventário de ferramentas herdadas indisponível") from error
            servers = config.get("mcp_servers", {})
            if not isinstance(servers, dict):
                raise _failure("Configuração MCP herdada inválida")
            names.update(servers)
    return tuple(sorted(names))


def build_policy(
    mode: PermissionMode,
    workspace: Path,
    runtime_roots: tuple[Path, ...],
) -> dict[str, JsonValue]:
    """Build a uniquely named, network-off profile without inherited roots."""
    if not isinstance(mode, PermissionMode) or not workspace.is_dir() or workspace.is_symlink():
        raise _failure("Workspace de probe inválido")
    workspace = workspace.resolve()
    home = Path.home().resolve()
    if workspace == Path(workspace.anchor) or home.is_relative_to(workspace):
        raise _failure("Raiz ampla não permitida como workspace")
    filesystem: dict[str, JsonValue] = {":minimal": "read"}
    for root in runtime_roots:
        root = root.resolve()
        if not root.is_dir() or home.is_relative_to(root):
            raise _failure("Raiz de runtime ampla/inválida")
        filesystem[str(root)] = "read"
    filesystem[str(workspace)] = "read" if mode is PermissionMode.READ else "write"
    return {
        "profile_id": "quill_" + uuid4().hex,
        "filesystem": filesystem,
        "network": {"enabled": False},
        "workspace": str(workspace),
        "mode": mode.value,
    }


def _arguments(policy: dict[str, JsonValue]) -> list[str]:
    identifier = policy.get("profile_id")
    filesystem = policy.get("filesystem")
    if not isinstance(identifier, str) or not identifier.startswith("quill_"):
        raise _failure("Perfil inválido")
    if not isinstance(filesystem, dict) or policy.get("network") != {"enabled": False}:
        raise _failure("Política de probe inválida")
    if not all(
        isinstance(key, str) and value in ("read", "write", "deny")
        for key, value in filesystem.items()
    ):
        raise _failure("Regras de filesystem inválidas")
    inline = (
        "{"
        + ",".join(json.dumps(key) + "=" + json.dumps(value) for key, value in filesystem.items())
        + "}"
    )
    result = [
        "-c",
        f"default_permissions={json.dumps(identifier)}",
        "-c",
        f"permissions.{identifier}.filesystem={inline}",
        "-c",
        f"permissions.{identifier}.network.enabled=false",
        "-c",
        'web_search="disabled"',
    ]
    for name in _mcp_inventory(Path(str(policy["workspace"]))):
        result.extend(("-c", f"mcp_servers.{json.dumps(name)}.enabled=false"))
    for feature in _DISABLED_FEATURES:
        result.extend(("--disable", feature))
    return result


def _binary() -> str:
    value = shutil.which("codex")
    if value is None:
        raise _failure("Codex não encontrado")
    return str(Path(value).resolve())


def _environment(extra: dict[str, str] | None = None) -> dict[str, str]:
    values = dict(os.environ)
    if extra:
        values.update(extra)
    return {key: value for key, value in values.items() if key in _ENVIRONMENT}


async def _stop(process: asyncio.subprocess.Process) -> None:
    if process.returncode is None:
        with suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        await process.wait()


async def run_probe(
    policy: dict[str, JsonValue],
    script: str,
    *arguments: str,
    environment: dict[str, str] | None = None,
) -> ProbeResult:
    """Execute only a caller-owned test script under the explicit CLI profile."""
    if os.name != "posix":
        raise _failure("Este harness exige Linux nativo")
    command = [
        _binary(),
        "sandbox",
        "-P",
        str(policy["profile_id"]),
        "--include-managed-config",
        "-C",
        str(policy["workspace"]),
        *_arguments(policy),
        "--",
        "/usr/bin/python",
        "-I",
        "-c",
        script,
        *arguments,
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=_environment(environment),
        start_new_session=True,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20)
        return ProbeResult(
            process.returncode or 0,
            stdout.decode(errors="replace"),
            stderr.decode(errors="replace"),
        )
    finally:
        await _stop(process)


async def run_rpc_probe(
    policy: dict[str, JsonValue],
    script: str,
    *arguments: str,
) -> ProbeResult:
    """Exercise command/exec with a profile, without creating a model turn."""
    process = await asyncio.create_subprocess_exec(
        _binary(),
        "app-server",
        "--listen",
        "stdio://",
        *_arguments(policy),
        cwd=str(policy["workspace"]),
        env=_environment(),
        start_new_session=True,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
        limit=8 * 1024 * 1024,
    )
    assert process.stdin is not None and process.stdout is not None

    async def request(
        identifier: int, method: str, params: dict[str, JsonValue]
    ) -> dict[str, JsonValue]:
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(
            (json.dumps({"id": identifier, "method": method, "params": params}) + "\n").encode()
        )
        await process.stdin.drain()
        for _ in range(100):
            raw = await asyncio.wait_for(process.stdout.readline(), timeout=20)
            if not raw:
                raise _failure("RPC de probe encerrado")
            message = json.loads(raw)
            if not isinstance(message, dict):
                raise _failure("RPC de probe inválido")
            if message.get("id") == identifier:
                result = message.get("result")
                if "error" in message or not isinstance(result, dict):
                    raise _failure("Comando de probe recusado")
                return result
            if "id" in message:
                raise _failure("Pedido inesperado: probe não concede aprovações")
        raise _failure("Limite RPC de probe excedido")

    try:
        await request(
            1,
            "initialize",
            {
                "clientInfo": {"name": "quill_probe", "version": "0.1.0"},
                "capabilities": {"experimentalApi": True},
            },
        )
        process.stdin.write(b'{"method":"initialized"}\n')
        await process.stdin.drain()
        result = await request(
            2,
            "command/exec",
            {
                "command": ["/usr/bin/python", "-I", "-c", script, *arguments],
                "cwd": policy["workspace"],
                "permissionProfile": policy["profile_id"],
                "timeoutMs": 10000,
            },
        )
        code, stdout, stderr = result.get("exitCode"), result.get("stdout"), result.get("stderr")
        if type(code) is not int or not isinstance(stdout, str) or not isinstance(stderr, str):
            raise _failure("Resultado de probe inválido")
        assert isinstance(code, int)
        return ProbeResult(code, stdout, stderr)
    finally:
        process.stdin.close()
        await _stop(process)


async def probe_sandbox() -> SandboxCapabilities:
    """Certify command read/write/network bounds and the alternate RPC route."""
    try:
        with (
            tempfile.TemporaryDirectory(prefix="quill-sandbox-") as directory,
            tempfile.TemporaryDirectory(prefix="quill-sentinel-", dir=Path.home()) as protected,
            socket.socket() as listener,
        ):
            workspace = Path(directory) / "workspace"
            workspace.mkdir()
            outside = Path(protected) / "outside.txt"
            outside.write_text("fixture-only")
            policy = build_policy(PermissionMode.ASSISTED, workspace, (Path(_binary()).parent,))
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            port = listener.getsockname()[1]
            script = (
                "from pathlib import Path; import socket,sys,json; result={}; "
                "Path('inside.txt').write_text('ok')\n"
                "try: Path(sys.argv[1]).read_text(); result['read']=False\n"
                "except OSError: result['read']=True\n"
                "try: Path(sys.argv[1]).write_text('bad'); result['write']=False\n"
                "except OSError: result['write']=True\n"
                "try: socket.create_connection(('127.0.0.1',int(sys.argv[2])),timeout=1); "
                "result['network']=False\n"
                "except OSError: result['network']=True\n"
                "print(json.dumps(result))"
            )
            result = await run_probe(policy, script, str(outside), str(port))
            checks = json.loads(result.stdout) if result.exit_code == 0 else {}
            rpc = await run_rpc_probe(
                policy,
                "from pathlib import Path; import sys;\n"
                "try: Path(sys.argv[1]).read_text(); print('ALLOWED')\n"
                "except OSError: print('DENIED')",
                str(outside),
            )
            listener.settimeout(0.05)
            try:
                connection, _ = listener.accept()
                connection.close()
                network = False
            except TimeoutError:
                network = checks.get("network") is True
            read = (
                checks.get("read") is True and rpc.exit_code == 0 and rpc.stdout.strip() == "DENIED"
            )
            write = (
                checks.get("write") is True
                and outside.read_text() == "fixture-only"
                and (workspace / "inside.txt").read_text() == "ok"
            )
            passed = read and write and network
        return SandboxCapabilities(
            available=passed,
            restricted_read=read,
            bounded_write=write,
            command_network_block=network,
            backend="linux-beta-probe",
            reason=None if passed else "Limites nativos não foram comprovados",
        )
    except (DomainError, OSError, TimeoutError, ValueError):
        return SandboxCapabilities(
            available=False,
            restricted_read=False,
            bounded_write=False,
            command_network_block=False,
            backend="unavailable",
            reason="Sandbox não pôde ser comprovado",
        )
