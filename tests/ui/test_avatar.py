"""Approved artwork is shown without silently swapping character identity."""

from pathlib import Path

import pytest
from PySide6.QtQuick import QQuickItem
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from quill.bootstrap import create_desktop

pytestmark = pytest.mark.ui


@pytest.fixture
def desktop(qapp: QApplication, tmp_path: Path):
    runtime = create_desktop(tmp_path / "data")
    assert runtime is not None
    yield runtime
    runtime.shutdown()


def test_avatar_frame_source(desktop) -> None:
    data = desktop.bridge.avatar
    assert data["width"] == 1536 and data["height"] == 1024
    assert str(data["source"]).endswith("assets/avatars/quill/atlas-0.png")


def test_size_bounds(desktop) -> None:
    desktop.bridge.setAvatarSize(192)
    assert desktop.bridge.avatarSize == 192
    desktop.bridge.setAvatarSize(2)
    assert desktop.bridge.avatarSize == 192


def test_hidden_timer_stops(desktop, qtbot: QtBot) -> None:
    desktop.window.hide()
    desktop.bridge.hideAvatar()
    qtbot.waitUntil(lambda: not desktop.bridge.animation_active)
    avatar = desktop.window.findChild(QQuickItem, "panelAvatar")
    assert avatar is not None
    assert not avatar.property("animationRunning")


def test_menu_intents(desktop) -> None:
    desktop.bridge.hideAvatar()
    assert not desktop.bridge.avatarVisible
    desktop.bridge.showAvatar()
    assert desktop.bridge.avatarVisible


def test_panel_opens_without_new_task(desktop, qtbot: QtBot) -> None:
    desktop.window.hide()
    desktop.bridge.showPanel()
    qtbot.waitUntil(desktop.window.isVisible)
    assert not desktop.bridge.busy


def test_reduced_motion_stops_breathing(desktop, qtbot: QtBot) -> None:
    desktop.bridge.setReducedMotion(True)
    qtbot.waitUntil(lambda: not desktop.bridge.animation_active)
    avatar = desktop.window.findChild(QQuickItem, "panelAvatar")
    assert avatar is not None
    assert not avatar.property("animationRunning")
