"""Avatar loading validates file bounds before any rendering."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from quill.avatar.assets import load_avatar, validate_manifest
from quill.core.errors import DomainError

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2] / "assets/avatars/quill"


@pytest.fixture
def avatar(tmp_path: Path) -> Path:
    target = tmp_path / "avatar"
    shutil.copytree(ROOT, target)
    return target


def test_all_required_states() -> None:
    manifest = load_avatar(ROOT)
    assert set(manifest.states) == {
        "idle",
        "listening",
        "thinking",
        "working",
        "awaiting_approval",
        "success",
        "confused",
        "error",
        "speaking",
    }
    assert all(animation.frames for animation in manifest.states.values())


def test_missing_frame_rejected(avatar: Path) -> None:
    value = json.loads((avatar / "manifest.json").read_text())
    value["states"]["idle"]["frames"] = []
    with pytest.raises(DomainError):
        validate_manifest(value, avatar)


def test_out_of_bounds_rejected(avatar: Path) -> None:
    value = json.loads((avatar / "manifest.json").read_text())
    value["states"]["idle"]["frames"][0]["x"] = 2048
    with pytest.raises(DomainError):
        validate_manifest(value, avatar)


def test_path_escape_rejected(avatar: Path) -> None:
    value = json.loads((avatar / "manifest.json").read_text())
    value["atlases"][0]["file"] = "../outside.png"
    with pytest.raises(DomainError):
        validate_manifest(value, avatar)


def test_atlas_budget_rejected(avatar: Path) -> None:
    value = json.loads((avatar / "manifest.json").read_text())
    value["atlases"][0]["width"] = 8192
    with pytest.raises(DomainError):
        validate_manifest(value, avatar)


def test_png_alpha_present() -> None:
    manifest = load_avatar(ROOT)
    atlas = next(iter(manifest.atlases.values()))
    image = QImage(str(atlas.path))
    assert image.hasAlphaChannel()
    assert image.pixelColor(0, 0).alpha() == 0


def test_atlas_symlink_outside_rejected(avatar: Path, tmp_path: Path) -> None:
    source = avatar / "atlas-0.png"
    outside = tmp_path / "outside.png"
    source.replace(outside)
    source.symlink_to(outside)
    with pytest.raises(DomainError):
        load_avatar(avatar)


def test_user_selected_art_is_preserved_exactly() -> None:
    assert (
        hashlib.sha256((ROOT / "atlas-0.png").read_bytes()).hexdigest()
        == "2abc06b7e30a5aa5570fbece377b3e8d8132d6bb4692bd0d0e37ef28cd514541"
    )


def test_selected_art_uses_native_frame_dimensions() -> None:
    manifest = load_avatar(ROOT)
    assert manifest.frame_size == (1536, 1024)
    assert manifest.states["idle"].frames[0].width == 1536
