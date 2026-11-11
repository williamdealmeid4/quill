"""Typed failures carrying safe, structured details."""

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quill.core.models import ErrorInfo


class ErrorCode(StrEnum):
    CONFIG_INVALID = "CONFIG_INVALID"
    CODEX_NOT_FOUND = "CODEX_NOT_FOUND"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    PROTOCOL_INCOMPATIBLE = "PROTOCOL_INCOMPATIBLE"
    SANDBOX_UNAVAILABLE = "SANDBOX_UNAVAILABLE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    PROCESS_FAILED = "PROCESS_FAILED"
    WORKSPACE_CONFLICT = "WORKSPACE_CONFLICT"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    STORAGE_FULL = "STORAGE_FULL"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class DomainError(Exception):
    """A domain failure with a user-facing message and safe details."""

    def __init__(self, info: "ErrorInfo") -> None:
        self.info = info
        super().__init__(f"{info.code}: {info.message}")
