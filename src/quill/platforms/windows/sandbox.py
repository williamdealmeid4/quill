"""Fail-closed Windows 11 permission-profile probe, without automatic setup."""

import asyncio
import json
import platform
import shutil
import socket
import sys
import tempfile
from pathlib import Path

from quill.codex.sandbox import ProbeResult, _arguments, _environment, build_policy
from quill.core.errors import DomainError, ErrorCode
from quill.core.models import ErrorInfo, JsonValue, PermissionMode, SandboxCapabilities


def _failure(message: str) -> DomainError:
    return DomainError(
        ErrorInfo(
            code=ErrorCode.SANDBOX_UNAVAILABLE, message=message, retryable=False, safe_details={}
        )
    )


class WindowsSandboxAdapter:
    """Only native .exe binaries and ready backends are accepted; no WSL fallback."""

    def __init__(self, executable: Path | None = None) -> None:
        discovered = shutil.which("codex.exe")
        self.executable = executable or (Path(discovered).resolve() if discovered else None)

    def _ensure_native(self) -> Path:
        if sys.platform != "win32":
            raise _failure("Validação exige Windows 11 nativo")
        if sys.getwindowsversion().build < 22000:
            raise _failure("Build do Windows anterior ao baseline Windows 11")
        if platform.machine().lower() not in ("amd64", "x86_64"):
            raise _failure("Arquitetura Windows fora do MVP x86_64")
        if (
            self.executable is None
            or not self.executable.is_file()
            or self.executable.suffix.lower() != ".exe"
        ):
            raise _failure("Codex standalone .exe não encontrado; não usar shim .cmd")
        return self.executable.resolve()

    async def _rpc(
        self, policy: dict[str, JsonValue], method: str, parameters: dict[str, JsonValue]
    ) -> dict[str, JsonValue]:
        executable = self._ensure_native()
        process = await asyncio.create_subprocess_exec(
            str(executable),
            "app-server",
            "--listen",
            "stdio://",
            *_arguments(policy),
            cwd=str(policy["workspace"]),
            env=_environment(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            limit=8 * 1024 * 1024,
        )
        assert process.stdin is not None and process.stdout is not None

        async def request(
            identifier: int, operation: str, params: dict[str, JsonValue]
        ) -> dict[str, JsonValue]:
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(
                (
                    json.dumps({"id": identifier, "method": operation, "params": params}) + "\n"
                ).encode()
            )
            await process.stdin.drain()
            for _ in range(100):
                line = await asyncio.wait_for(process.stdout.readline(), timeout=20)
                if not line:
                    raise _failure("Conexão Windows de probe encerrada")
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise _failure("RPC Windows de probe inválido")
                if value.get("id") == identifier:
                    result = value.get("result")
                    if "error" in value or not isinstance(result, dict):
                        raise _failure("Backend Windows recusou o probe")
                    return result
                if "id" in value:
                    raise _failure("Probe Windows não concede aprovações")
            raise _failure("Limite de mensagens do probe Windows excedido")

        try:
            await request(
                1,
                "initialize",
                {
                    "clientInfo": {"name": "quill_windows_probe", "version": "0.1.0"},
                    "capabilities": {"experimentalApi": True},
                },
            )
            process.stdin.write(b'{"method":"initialized"}\n')
            await process.stdin.drain()
            return await request(2, method, parameters)
        finally:
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            except TimeoutError:
                process.kill()
                await process.wait()

    async def execute_probe(
        self,
        workspace: Path,
        script: str,
        arguments: tuple[str, ...] = (),
        *,
        mode: PermissionMode = PermissionMode.ASSISTED,
    ) -> ProbeResult:
        """Run a caller-owned fixture only after version and native readiness checks."""
        executable = self._ensure_native()
        version_process = await asyncio.create_subprocess_exec(
            str(executable),
            "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            env=_environment(),
        )
        try:
            version, _ = await asyncio.wait_for(version_process.communicate(), timeout=10)
            if version_process.returncode != 0 or version.decode().strip() != "codex-cli 0.167.1":
                raise _failure("CLI Windows não corresponde ao contrato capturado 0.167.1")
        finally:
            if version_process.returncode is None:
                version_process.kill()
                await version_process.wait()
        policy = build_policy(
            mode, workspace, (executable.parent, Path(sys.prefix), Path(sys.base_prefix))
        )
        readiness = await self._rpc(policy, "windowsSandbox/readiness", {})
        if readiness.get("status") != "ready":
            raise _failure("Sandbox Windows não está ready; setup/update deve ser explícito")
        result = await self._rpc(
            policy,
            "command/exec",
            {
                "command": [sys.executable, "-I", "-c", script, *arguments],
                "cwd": str(workspace.resolve()),
                "permissionProfile": policy["profile_id"],
                "timeoutMs": 10000,
            },
        )
        code, stdout, stderr = result.get("exitCode"), result.get("stdout"), result.get("stderr")
        if type(code) is not int or not isinstance(stdout, str) or not isinstance(stderr, str):
            raise _failure("Resultado Windows não corresponde ao contrato")
        assert isinstance(code, int)
        return ProbeResult(code, stdout, stderr)

    async def probe(self) -> SandboxCapabilities:
        """Report unavailable unless native read, write and network limits pass."""
        try:
            self._ensure_native()
            with (
                tempfile.TemporaryDirectory(prefix="quill-win-workspace-") as directory,
                tempfile.TemporaryDirectory(
                    prefix="quill-win-sentinel-", dir=Path.home()
                ) as protected,
                socket.socket() as listener,
            ):
                workspace = Path(directory)
                outside = Path(protected) / "sentinel.txt"
                outside.write_text("fixture-only")
                listener.bind(("127.0.0.1", 0))
                listener.listen()
                script = (
                    "from pathlib import Path; import socket,sys,json; result={}; "
                    "Path('inside.txt').write_text('ok')\n"
                    "try: Path(sys.argv[1]).read_text(); result['read']=False\n"
                    "except OSError: result['read']=True\n"
                    "try: Path(sys.argv[1]).write_text('bad'); result['write']=False\n"
                    "except OSError: result['write']=True\n"
                    "try: socket.create_connection(('127.0.0.1',int(sys.argv[2])),timeout=1); "
                    "result['network']=False\n"
                    "except OSError: result['network']=True\nprint(json.dumps(result))"
                )
                result = await self.execute_probe(
                    workspace, script, (str(outside), str(listener.getsockname()[1]))
                )
                checks = json.loads(result.stdout) if result.exit_code == 0 else {}
                read = checks.get("read") is True
                write = (
                    checks.get("write") is True
                    and outside.read_text() == "fixture-only"
                    and (workspace / "inside.txt").read_text() == "ok"
                )
                network = checks.get("network") is True
                listener.settimeout(0.05)
                try:
                    connection, _ = listener.accept()
                    connection.close()
                    network = False
                except TimeoutError:
                    pass
            return SandboxCapabilities(
                available=read and write and network,
                restricted_read=read,
                bounded_write=write,
                command_network_block=network,
                backend="windows-native-probe",
                reason=None if read and write and network else "Isolamento Windows não comprovado",
            )
        except (DomainError, OSError, ValueError, TimeoutError) as error:
            reason = (
                error.info.message
                if isinstance(error, DomainError)
                else "Falha no probe nativo Windows"
            )
            return SandboxCapabilities(
                available=False,
                restricted_read=False,
                bounded_write=False,
                command_network_block=False,
                backend="unavailable",
                reason=reason,
            )
