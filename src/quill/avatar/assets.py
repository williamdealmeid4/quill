"""Validate an avatar manifest and PNG bounds before any presentation uses it."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Never, cast

from jsonschema import Draft202012Validator, ValidationError
from PySide6.QtGui import QImageReader

from quill.core.errors import DomainError, ErrorCode
from quill.core.models import ErrorInfo, JsonValue

AVATAR_STATES = frozenset(
    {
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
)
RESOURCE_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class Atlas:
    path: Path
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class AvatarFrame:
    atlas: str
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class AvatarAnimation:
    frames: tuple[AvatarFrame, ...]
    fps: int
    loop: bool
    next_state: str | None


@dataclass(frozen=True, slots=True)
class AvatarManifest:
    id: str
    display_name: str
    anchor: tuple[int, int]
    hit_region: tuple[tuple[int, int], ...]
    atlases: Mapping[str, Atlas]
    states: Mapping[str, AvatarAnimation]


def _failure(message: str) -> DomainError:
    return DomainError(
        ErrorInfo(
            code=ErrorCode.VALIDATION_FAILED, message=message, retryable=False, safe_details={}
        )
    )


def _reject_constant(value: str) -> Never:
    raise ValueError("Constante JSON não finita")


def _object(value: JsonValue) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise _failure("Objeto de avatar inválido")
    return value


def _list(value: JsonValue) -> list[JsonValue]:
    if not isinstance(value, list):
        raise _failure("Lista de avatar inválida")
    return value


def _text(value: JsonValue) -> str:
    if not isinstance(value, str):
        raise _failure("Texto de avatar inválido")
    return value


def _number(value: JsonValue) -> int:
    if type(value) is not int:
        raise _failure("Coordenada de avatar inválida")
    return value


def _asset_path(root: Path, name: str) -> Path:
    if any(character in name for character in ("\\", ":", "\0")):
        raise _failure("Caminho de atlas inválido")
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise _failure("Atlas fora do diretório autorizado")
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise _failure("Atlas ausente ou fora do diretório autorizado")
    return path


def validate_manifest(value: JsonValue, root: Path) -> AvatarManifest:
    """Validate schema, containment, actual decoded dimensions and memory budget."""
    root = root.resolve()
    schema = json.loads((RESOURCE_ROOT / "schemas/avatar.schema.json").read_text())
    try:
        Draft202012Validator(schema).validate(value)
    except ValidationError as error:
        raise _failure(f"Manifesto de avatar inválido em {error.json_path}") from error
    raw = _object(value)
    atlases: dict[str, Atlas] = {}
    decoded_bytes = 0
    for entry in _list(raw["atlases"]):
        item = _object(entry)
        name = _text(item["file"])
        path = _asset_path(root, name)
        width, height = _number(item["width"]), _number(item["height"])
        if name in atlases:
            raise _failure("Atlas duplicado")
        decoded_bytes += width * height * 4
        if decoded_bytes > 64 * 1024 * 1024:
            raise _failure("Orçamento de textura excedido")
        reader = QImageReader(str(path))
        dimensions = reader.size()
        if bytes(reader.format().data()).lower() != b"png" or (
            dimensions.width(),
            dimensions.height(),
        ) != (width, height):
            raise _failure("Dimensões/formato reais do atlas divergem do manifesto")
        image = reader.read()
        if image.isNull() or not image.hasAlphaChannel():
            raise _failure("Atlas precisa ser PNG RGBA válido")
        atlases[name] = Atlas(path=path, width=width, height=height)
    states: dict[str, AvatarAnimation] = {}
    for name, data in _object(raw["states"]).items():
        animation = _object(data)
        frames: list[AvatarFrame] = []
        for frame_data in _list(animation["frames"]):
            frame = _object(frame_data)
            atlas_name = _text(frame["atlas"])
            atlas = atlases.get(atlas_name)
            if atlas is None:
                raise _failure("Frame referencia atlas desconhecido")
            x, y = _number(frame["x"]), _number(frame["y"])
            width, height = _number(frame["width"]), _number(frame["height"])
            if x + width > atlas.width or y + height > atlas.height:
                raise _failure("Frame fora dos limites do atlas")
            frames.append(AvatarFrame(atlas=atlas_name, x=x, y=y, width=width, height=height))
        states[name] = AvatarAnimation(
            frames=tuple(frames),
            fps=_number(animation["fps"]),
            loop=cast(bool, animation["loop"]),
            next_state=cast(str | None, animation["next_state"]),
        )
    anchor = _list(raw["anchor"])
    region = tuple(
        (_number(_list(point)[0]), _number(_list(point)[1])) for point in _list(raw["hit_region"])
    )
    return AvatarManifest(
        id=_text(raw["id"]),
        display_name=_text(raw["display_name"]),
        anchor=(_number(anchor[0]), _number(anchor[1])),
        hit_region=region,
        atlases=MappingProxyType(atlases),
        states=MappingProxyType(states),
    )


def load_avatar(root: Path) -> AvatarManifest:
    """Load only a manifest inside the chosen avatar directory, with bounded input."""
    try:
        root = root.resolve()
        manifest = (root / "manifest.json").resolve()
        if not manifest.is_relative_to(root) or manifest.stat().st_size > 512 * 1024:
            raise _failure("Manifesto fora do escopo ou acima do limite")
        value = json.loads(manifest.read_text(encoding="utf-8"), parse_constant=_reject_constant)
        return validate_manifest(cast(JsonValue, value), root)
    except (OSError, ValueError) as error:
        raise _failure("Não foi possível carregar o manifesto de avatar") from error
