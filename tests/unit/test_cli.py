"""Exercise the CLI as an installed package from an unrelated directory."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def run_cli(tmp_path: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    for name in (
        "HOME",
        "USERPROFILE",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_CACHE_HOME",
        "XDG_STATE_HOME",
        "APPDATA",
        "LOCALAPPDATA",
    ):
        env[name] = str(tmp_path / name.lower())
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "quill", *arguments],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_version_subprocess(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "--version")
    assert result.returncode == 0
    assert result.stdout == "0.1.0\n"
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []


def test_help_without_side_effects(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "--help")
    assert result.returncode == 0
    assert "--version" in result.stdout
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []


def test_unknown_argument(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "--unknown-option")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "--unknown-option" in result.stderr
    assert list(tmp_path.iterdir()) == []
