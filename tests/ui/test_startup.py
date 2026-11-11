"""Desktop lifecycle and real event-loop responsiveness."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from quill.bootstrap import create_desktop

pytestmark = pytest.mark.ui


@pytest.fixture
def desktop(qapp: QApplication, tmp_path: Path):
    instance = create_desktop(tmp_path / "data")
    assert instance is not None
    yield instance
    instance.shutdown()


def test_window_opens_and_closes(desktop, qtbot: QtBot) -> None:
    qtbot.waitUntil(desktop.window.isVisible)
    desktop.window.close()
    assert not desktop.window.isVisible()


def test_slow_fake_does_not_freeze_ui(desktop, qtbot: QtBot) -> None:
    completed: list[object] = []
    ticks: list[int] = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(10)
    desktop.worker.resultReady.connect(lambda _id, result: completed.append(result))

    async def slow() -> str:
        await asyncio.sleep(0.4)
        return "finished"

    desktop.worker.submit(slow())
    qtbot.waitUntil(lambda: len(ticks) >= 3)
    assert completed == []
    qtbot.waitUntil(lambda: completed == ["finished"])
    timer.stop()


def test_shutdown_stops_worker(desktop) -> None:
    desktop.shutdown()
    assert not desktop.worker.is_running


def test_version_still_headless(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "does-not-exist"
    result = subprocess.run(
        [sys.executable, "-m", "quill", "--version"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0 and result.stdout == "0.1.0\n"


def test_second_instance_reopens_first_without_worker(
    desktop, qtbot: QtBot, tmp_path: Path
) -> None:
    desktop.window.hide()
    assert create_desktop(tmp_path / "data") is None
    qtbot.waitUntil(desktop.window.isVisible)
    assert desktop.worker.is_running
