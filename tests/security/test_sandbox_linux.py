"""Native sandbox sentinels; live tests require explicit pytest opt-in."""

import asyncio
import shutil
import socket
from pathlib import Path

import pytest

from quill.codex.sandbox import build_policy, probe_sandbox, run_probe, run_rpc_probe
from quill.core.errors import DomainError
from quill.core.models import JsonValue, PermissionMode

pytestmark = pytest.mark.security


@pytest.fixture
def setup(tmp_path: Path) -> tuple[dict[str, JsonValue], Path, Path]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("fixture-only")
    binary = Path(shutil.which("codex") or "missing").resolve()
    policy = build_policy(PermissionMode.ASSISTED, workspace, (binary.parent,))
    return policy, workspace, outside


def test_broad_roots_rejected(tmp_path: Path) -> None:
    with pytest.raises(DomainError):
        build_policy(PermissionMode.ASSISTED, Path.home(), (tmp_path,))


@pytest.mark.live_codex
def test_read_sentinel_denied(setup: tuple[dict[str, JsonValue], Path, Path]) -> None:
    policy, _, outside = setup
    result = asyncio.run(
        run_probe(
            policy,
            (
                "from pathlib import Path; import sys;\ntry: Path(sys.argv[1]).read"
                "_text(); print('ALLOWED')\nexcept OSError: print('DENIED')"
            ),
            str(outside),
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "DENIED"


@pytest.mark.live_codex
def test_write_sentinel_unchanged(setup: tuple[dict[str, JsonValue], Path, Path]) -> None:
    policy, workspace, outside = setup
    result = asyncio.run(
        run_probe(
            policy,
            (
                "from pathlib import Path; import sys; Path('inside.txt').write_te"
                "xt('ok');\ntry: Path(sys.argv[1]).write_text('bad'); print('ALLOWE"
                "D')\nexcept OSError: print('DENIED')"
            ),
            str(outside),
        )
    )
    assert result.exit_code == 0
    assert result.stdout.strip() in ("DENIED", "ALLOWED")
    # /tmp may be a private mount: only host state establishes whether an effect escaped.
    assert (workspace / "inside.txt").read_text() == "ok"
    assert outside.read_text() == "fixture-only"


@pytest.mark.live_codex
def test_command_network_denied(setup: tuple[dict[str, JsonValue], Path, Path]) -> None:
    policy, _, _ = setup
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        result = asyncio.run(
            run_probe(
                policy,
                (
                    "import socket,sys;\ntry: socket.create_connection(('127.0.0.1',int"
                    "(sys.argv[1])),timeout=1); print('ALLOWED')\nexcept OSError: print"
                    "('DENIED')"
                ),
                str(port),
            )
        )
        assert result.exit_code == 0 and result.stdout.strip() == "DENIED"
        listener.settimeout(0.05)
        with pytest.raises(TimeoutError):
            listener.accept()


@pytest.mark.live_codex
def test_alternate_tool_cannot_read_origin(setup: tuple[dict[str, JsonValue], Path, Path]) -> None:
    policy, _, outside = setup
    result = asyncio.run(
        run_rpc_probe(
            policy,
            (
                "from pathlib import Path; import sys;\ntry: Path(sys.argv[1]).read"
                "_text(); print('ALLOWED')\nexcept OSError: print('DENIED')"
            ),
            str(outside),
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "DENIED"


@pytest.mark.live_codex
def test_inherited_hook_not_run(
    setup: tuple[dict[str, JsonValue], Path, Path], tmp_path: Path
) -> None:
    policy, workspace, _ = setup
    hook = tmp_path / "hook.sh"
    marker = workspace / "hook-ran"
    hook.write_text(f'touch "{marker}"\n')
    result = asyncio.run(
        run_probe(
            policy,
            "import os; assert 'BASH_ENV' not in os.environ; print('OK')",
            environment={"BASH_ENV": str(hook)},
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "OK"
    assert not marker.exists()


@pytest.mark.live_codex
def test_recursive_executor_blocked(setup: tuple[dict[str, JsonValue], Path, Path]) -> None:
    policy, _, _ = setup
    binary = str(Path(shutil.which("codex") or "missing").resolve())
    script = (
        "import subprocess,sys;\n"
        "try:\n"
        " p=subprocess.run([sys.argv[1],'exec','--ephemeral','--ignore-user-config',"
        "'--skip-git-repo-check','-'],input='Do nothing',text=True,capture_output=True,"
        "env={'HOME':'/quill-no-auth','CODEX_HOME':'/quill-no-auth','PATH':'/usr/bin'},timeout=3);"
        " print('BLOCKED' if p.returncode != 0 else 'ALLOWED')\n"
        "except subprocess.TimeoutExpired: print('BLOCKED')"
    )
    result = asyncio.run(run_probe(policy, script, binary))
    assert result.exit_code == 0 and result.stdout.strip() == "BLOCKED"


@pytest.mark.live_codex
def test_read_mode_cannot_write(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    binary = Path(shutil.which("codex") or "missing").resolve()
    policy = build_policy(PermissionMode.READ, workspace, (binary.parent,))
    result = asyncio.run(
        run_probe(
            policy,
            (
                "from pathlib import Path;\ntry: Path('forbidden.txt').write_text('"
                "bad'); print('ALLOWED')\nexcept OSError: print('DENIED')"
            ),
        )
    )
    assert result.exit_code == 0 and result.stdout.strip() == "DENIED"
    assert not (workspace / "forbidden.txt").exists()


@pytest.mark.live_codex
def test_home_sentinel_write_denied(setup: tuple[dict[str, JsonValue], Path, Path]) -> None:
    import tempfile

    policy, _, _ = setup
    with tempfile.TemporaryDirectory(prefix="quill-test-sentinel-", dir=Path.home()) as directory:
        outside = Path(directory) / "sentinel.txt"
        outside.write_text("fixture-only")
        script = (
            "from pathlib import Path; import sys;\n"
            "try: Path(sys.argv[1]).write_text('bad'); print('ALLOWED')\n"
            "except OSError: print('DENIED')"
        )
        result = asyncio.run(run_probe(policy, script, str(outside)))
        assert result.exit_code == 0 and result.stdout.strip() == "DENIED"
        assert outside.read_text() == "fixture-only"


@pytest.mark.live_codex
def test_probe_reports_native_certification() -> None:
    result = asyncio.run(probe_sandbox())
    assert result.available
    assert result.restricted_read and result.bounded_write and result.command_network_block
