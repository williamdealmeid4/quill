"""Configuration values and validation independent of desktop services."""

from dataclasses import dataclass, fields
from pathlib import Path


class ConfigError(ValueError):
    """An invalid configuration must be preserved for user correction."""


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Version-one user preferences; grants never belong in this object."""

    schema_version: int = 1
    default_mode: str = "read"
    theme: str = "system"
    avatar_size: int = 160
    avatar_visible: bool = True
    reduced_motion: bool = False
    task_timeout_s: int = 1200
    log_retention_days: int = 14
    history_retention_days: int = 90
    workspace_retention_days: int = 7
    voice_enabled: bool = False
    autostart: bool = False
    model_id: str | None = None
    reasoning_effort: str = "low"

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            for expected in (int, bool, str):
                if field.type is expected and type(value) is not expected:
                    raise ConfigError(f"CONFIG_INVALID: tipo inválido em {field.name}")
        choices = {
            "schema_version": (1,),
            "default_mode": ("read", "assisted", "restricted_auto"),
            "theme": ("system", "light", "dark"),
            "reasoning_effort": ("low",),
        }
        for name, allowed in choices.items():
            if getattr(self, name) not in allowed:
                raise ConfigError(f"CONFIG_INVALID: valor inválido em {name}")
        for name, lower, upper in (
            ("avatar_size", 96, 256),
            ("task_timeout_s", 60, 3600),
            ("log_retention_days", 1, None),
            ("history_retention_days", 1, None),
            ("workspace_retention_days", 1, None),
        ):
            value = getattr(self, name)
            if value < lower or (upper is not None and value > upper):
                raise ConfigError(f"CONFIG_INVALID: limite inválido em {name}")
        if self.model_id is not None and (
            not isinstance(self.model_id, str) or not self.model_id.strip()
        ):
            raise ConfigError("CONFIG_INVALID: model_id deve ser texto não vazio")


@dataclass(frozen=True, slots=True)
class AppPaths:
    """Platform-specific locations, resolved without creating directories."""

    config: Path
    data: Path
    cache: Path
    log: Path
