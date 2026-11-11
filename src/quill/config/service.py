"""Read TOML and replace generated configuration atomically."""

import json
import os
import tempfile
import tomllib
from dataclasses import asdict, fields
from pathlib import Path

import platformdirs

from quill.config.models import AppConfig, AppPaths, ConfigError


class ConfigService:
    """Configuration I/O, injectable to avoid user files in tests."""

    def __init__(self, config_dir: Path | None = None) -> None:
        directory = (
            config_dir
            if config_dir is not None
            else platformdirs.user_config_path("quill", appauthor=False)
        )
        self.paths = AppPaths(
            config=directory,
            data=platformdirs.user_data_path("quill", appauthor=False),
            cache=platformdirs.user_cache_path("quill", appauthor=False),
            log=platformdirs.user_log_path("quill", appauthor=False),
        )
        self.path = self.paths.config / "config.toml"

    def load(self) -> AppConfig:
        """Return defaults for a missing file and reject invalid content."""
        try:
            with self.path.open("rb") as stream:
                values = tomllib.load(stream)
        except FileNotFoundError:
            return AppConfig()
        except tomllib.TOMLDecodeError as error:
            raise ConfigError(f"CONFIG_INVALID: TOML inválido em {self.path}") from error
        known = {field.name for field in fields(AppConfig)}
        unknown = values.keys() - known
        if unknown:
            raise ConfigError(f"CONFIG_INVALID: chave desconhecida: {', '.join(sorted(unknown))}")
        return AppConfig(**values)

    def save(self, config: AppConfig) -> None:
        """Keep the old file intact if staging or replacement fails."""
        content: list[str] = []
        for name, value in asdict(config).items():
            if value is None:
                continue
            if isinstance(value, bool):
                encoded = str(value).lower()
            elif isinstance(value, str):
                encoded = json.dumps(value, ensure_ascii=False)
            else:
                encoded = str(value)
            content.append(f"{name} = {encoded}\n")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        staged: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".config-",
                suffix=".tmp",
                delete=False,
            ) as stream:
                staged = Path(stream.name)
                stream.write("".join(content))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(staged, self.path)
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)
