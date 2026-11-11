"""Configuration validation and atomic persistence."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from quill.config.models import AppConfig, ConfigError
from quill.config.service import ConfigService

pytestmark = pytest.mark.unit


def test_missing_uses_defaults(tmp_path: Path) -> None:
    service = ConfigService(tmp_path / "config")
    assert service.load() == AppConfig()
    assert not service.path.parent.exists()


def test_invalid_toml_preserved(tmp_path: Path) -> None:
    service = ConfigService(tmp_path)
    service.path.write_text("broken = [", encoding="utf-8")
    with pytest.raises(ConfigError, match="CONFIG_INVALID"):
        service.load()
    assert service.path.read_text() == "broken = ["


def test_unknown_key_rejected(tmp_path: Path) -> None:
    service = ConfigService(tmp_path)
    service.path.write_text("unknown = true", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown"):
        service.load()


def test_roundtrip_unicode(tmp_path: Path) -> None:
    service = ConfigService(tmp_path)
    config = replace(AppConfig(), model_id='sol-ação-"teste"', theme="dark")
    service.save(config)
    assert service.load() == config


def test_atomic_save_failure_preserves_original(tmp_path: Path) -> None:
    service = ConfigService(tmp_path)
    service.save(AppConfig())
    before = service.path.read_bytes()
    with (
        patch("quill.config.service.os.replace", side_effect=OSError("fixture")),
        pytest.raises(OSError, match="fixture"),
    ):
        service.save(replace(AppConfig(), theme="dark"))
    assert service.path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [service.path]


@pytest.mark.parametrize(
    "text",
    [
        "avatar_size = true",
        "avatar_visible = 0",
        "voice_enabled = 'yes'",
        "avatar_size = 95",
        "theme = 'pink'",
        "schema_version = 2",
        "task_timeout_s = 59",
        "log_retention_days = 0",
    ],
)
def test_invalid_values_rejected(tmp_path: Path, text: str) -> None:
    service = ConfigService(tmp_path)
    service.path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError):
        service.load()


def test_platform_directory_is_injected(tmp_path: Path) -> None:
    with patch("quill.config.service.platformdirs.user_config_path", return_value=tmp_path):
        assert ConfigService().path == tmp_path / "config.toml"


def test_all_platform_paths_without_creation(tmp_path: Path) -> None:
    with (
        patch(
            "quill.config.service.platformdirs.user_config_path", return_value=tmp_path / "config"
        ),
        patch("quill.config.service.platformdirs.user_data_path", return_value=tmp_path / "data"),
        patch("quill.config.service.platformdirs.user_cache_path", return_value=tmp_path / "cache"),
        patch("quill.config.service.platformdirs.user_log_path", return_value=tmp_path / "log"),
    ):
        service = ConfigService()
        assert service.paths.config == tmp_path / "config"
        assert service.paths.data == tmp_path / "data"
        assert service.paths.cache == tmp_path / "cache"
        assert service.paths.log == tmp_path / "log"
    assert list(tmp_path.iterdir()) == []
