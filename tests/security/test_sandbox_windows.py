"""Windows native probes; Linux cannot certify their results."""

import asyncio
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from quill.core.models import PermissionMode
from quill.platforms.windows.sandbox import WindowsSandboxAdapter

pytestmark = pytest.mark.security
native = pytest.mark.skipif(sys.platform != "win32", reason="Exige Windows 11 nativo")


def test_unavailable_blocks(tmp_path: Path) -> None:
    result = asyncio.run(WindowsSandboxAdapter(executable=tmp_path / "missing.exe").probe())
    assert not result.available
    assert not result.restricted_read


@pytest.fixture
def adapter() -> WindowsSandboxAdapter:
    return WindowsSandboxAdapter()


@native
@pytest.mark.live_codex
def test_windows_read_denied(adapter: WindowsSandboxAdapter, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("fixture-only")
    result = asyncio.run(
        adapter.execute_probe(
            workspace,
            "from pathlib import Path; import sys;\n"
            "try: Path(sys.argv[1]).read_text(); print('ALLOWED')\n"
            "except OSError: print('DENIED')",
            (str(outside),),
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "DENIED"


@native
@pytest.mark.live_codex
def test_windows_write_denied(adapter: WindowsSandboxAdapter, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with tempfile.TemporaryDirectory(prefix="quill-sentinel-", dir=Path.home()) as directory:
        outside = Path(directory) / "outside.txt"
        outside.write_text("fixture-only")
        result = asyncio.run(
            adapter.execute_probe(
                workspace,
                "from pathlib import Path; import sys; Path('inside.txt').write_text('ok');\n"
                "try: Path(sys.argv[1]).write_text('bad'); print('ALLOWED')\n"
                "except OSError: print('DENIED')",
                (str(outside),),
            )
        )
        assert result.exit_code == 0 and result.stdout.strip() == "DENIED"
        assert outside.read_text() == "fixture-only"
        assert (workspace / "inside.txt").read_text() == "ok"


@native
@pytest.mark.live_codex
def test_windows_network_denied(adapter: WindowsSandboxAdapter, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        result = asyncio.run(
            adapter.execute_probe(
                workspace,
                "import socket,sys;\n"
                "try: socket.create_connection(('127.0.0.1',int(sys.argv[1])),timeout=1); "
                "print('ALLOWED')\n"
                "except OSError: print('DENIED')",
                (str(listener.getsockname()[1]),),
            )
        )
        assert result.exit_code == 0 and result.stdout.strip() == "DENIED"
        listener.settimeout(0.05)
        with pytest.raises(TimeoutError):
            listener.accept()


@native
@pytest.mark.live_codex
def test_windows_reparse_escape_denied(adapter: WindowsSandboxAdapter, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "sentinel.txt").write_text("fixture-only")
    link = workspace / "junction"
    # Only generated paths without command-expansion characters enter this test-only command.
    for path in (link, outside):
        assert not any(c in str(path) for c in '%!&|<>^"\r\n')
    result = subprocess.run(
        ["cmd.exe", "/d", "/c", f'mklink /J "{link}" "{outside}"'],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, "Fixture de junction não pôde ser criada"
    try:
        probe = asyncio.run(
            adapter.execute_probe(
                workspace,
                "from pathlib import Path;\n"
                "try: Path('junction/sentinel.txt').read_text(); print('ALLOWED')\n"
                "except OSError: print('DENIED')",
            )
        )
        assert probe.exit_code == 0 and probe.stdout.strip() == "DENIED"
    finally:
        os.rmdir(link)


@native
@pytest.mark.live_codex
def test_windows_recursive_executor_blocked(adapter: WindowsSandboxAdapter, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    script = (
        "import subprocess,sys;\n"
        "try:\n"
        " p=subprocess.run([sys.argv[1],'exec','--ephemeral','--ignore-user-config',"
        "'--skip-git-repo-check','-'],input='Do nothing',capture_output=True,text=True,"
        "env={'HOME':sys.argv[2],'USERPROFILE':sys.argv[2],'CODEX_HOME':sys.argv[2]},timeout=3);"
        " print('BLOCKED' if p.returncode else 'ALLOWED')\n"
        "except (OSError,subprocess.TimeoutExpired): print('BLOCKED')"
    )
    result = asyncio.run(
        adapter.execute_probe(
            workspace, script, (str(adapter.executable), str(tmp_path / "unavailable-auth"))
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "BLOCKED"


@native
@pytest.mark.live_codex
def test_windows_read_mode_cannot_write(adapter: WindowsSandboxAdapter, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = asyncio.run(
        adapter.execute_probe(
            workspace,
            "from pathlib import Path;\n"
            "try: Path('forbidden.txt').write_text('bad'); print('ALLOWED')\n"
            "except OSError: print('DENIED')",
            mode=PermissionMode.READ,
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "DENIED"
    assert not (workspace / "forbidden.txt").exists()


@native
@pytest.mark.live_codex
def test_windows_native_probe_certifies(adapter: WindowsSandboxAdapter) -> None:
    result = asyncio.run(adapter.probe())
    assert result.available, result.reason
    assert result.restricted_read and result.bounded_write and result.command_network_block
