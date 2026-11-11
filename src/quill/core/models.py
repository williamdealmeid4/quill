"""Immutable typed DTOs shared by the application modules."""

from __future__ import annotations

import math
import types
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Protocol, TypeVar, get_args, get_origin, get_type_hints
from uuid import UUID

from quill.core.errors import DomainError, ErrorCode

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]


class PermissionMode(StrEnum):
    READ = "read"
    ASSISTED = "assisted"
    RESTRICTED_AUTO = "restricted_auto"


class DecisionOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    PENDING = "pending"


class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Effect(StrEnum):
    READ = "read"
    CREATE = "create"
    MODIFY = "modify"
    MOVE = "move"
    LAUNCH = "launch"
    EXECUTE = "execute"
    EXTERNAL = "external"


class ResourceKind(StrEnum):
    PATH = "path"
    APPLICATION = "application"
    COMMAND = "command"
    NETWORK = "network"


class ChangeKind(StrEnum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"


class ApplyStatus(StrEnum):
    APPLIED = "applied"
    CONFLICT = "conflict"
    ROLLED_BACK = "rolled_back"
    RECOVERY_REQUIRED = "recovery_required"


class TaskState(StrEnum):
    QUEUED = "queued"
    PREPARING = "preparing"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    VERIFYING = "verifying"
    AWAITING_REVIEW = "awaiting_review"
    APPLYING = "applying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"
    BLOCKED = "blocked"


class EventKind(StrEnum):
    TASK_QUEUED = "task.queued"
    TASK_STATE_CHANGED = "task.state_changed"
    EXECUTION_STARTED = "execution.started"
    EXECUTION_PROGRESS = "execution.progress"
    EXECUTION_OUTPUT = "execution.output"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_RESOLVED = "approval.resolved"
    TOOL_COMPLETED = "tool.completed"
    VERIFICATION_COMPLETED = "verification.completed"
    CHANGESET_READY = "changeset.ready"
    APPLICATION_COMPLETED = "application.completed"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"
    TASK_INTERRUPTED = "task.interrupted"


def _invalid(message: str) -> DomainError:
    return DomainError(
        ErrorInfo(
            code=ErrorCode.VALIDATION_FAILED, message=message, retryable=False, safe_details={}
        )
    )


def _valid_json(value: object) -> bool:
    if value is None or type(value) in (bool, int, str):
        return True
    if type(value) is float:
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_valid_json(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _valid_json(item) for key, item in value.items())
    return False


def _matches(value: object, expected: object) -> bool:
    if expected is JsonValue:
        return _valid_json(value)
    if isinstance(expected, TypeVar):
        return True  # Generic result pages are typed at their producer boundary.
    origin = get_origin(expected)
    arguments = get_args(expected)
    if origin is types.UnionType:
        return any(_matches(value, member) for member in arguments)
    if origin in (list, tuple, frozenset, dict):
        if not isinstance(value, origin):
            return False
        if origin is dict:
            assert isinstance(value, dict)
            return all(
                _matches(key, arguments[0]) and _matches(item, arguments[1])
                for key, item in value.items()
            )
        assert isinstance(value, (list, tuple, frozenset))
        return all(_matches(item, arguments[0]) for item in value)
    if expected is datetime:
        return isinstance(value, datetime) and value.utcoffset() == timedelta(0)
    if expected in (bool, int, float, str):
        return type(value) is expected and (not isinstance(value, float) or math.isfinite(value))
    return isinstance(expected, type) and isinstance(value, expected)


def _hints(cls: type[object]) -> dict[str, object]:
    return get_type_hints(cls)


@dataclass(frozen=True, slots=True, kw_only=True)
class _Validated:
    def __post_init__(self) -> None:
        hints = _hints(type(self))
        for field in fields(self):
            value = getattr(self, field.name)
            if not _matches(value, hints[field.name]):
                raise _invalid(f"Tipo/valor inválido em {field.name}")
            if field.name in ("sequence", "size", "schema_version", "timeout_s") and value < 0:
                raise _invalid(f"Limite inválido em {field.name}")
        if isinstance(self, TaskQuery) and not 1 <= self.limit <= 100:
            raise _invalid("limit deve estar entre 1 e 100")


@dataclass(frozen=True, slots=True, kw_only=True)
class ExecutorCapabilities(_Validated):
    cli_version: str
    schema_digest: str
    authenticated: bool
    available_models: tuple[ModelCapability, ...]
    sandbox: SandboxCapabilities
    supported_methods: frozenset[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelCapability(_Validated):
    id: str
    display_name: str
    efforts: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class SandboxCapabilities(_Validated):
    available: bool
    restricted_read: bool
    bounded_write: bool
    command_network_block: bool
    backend: str
    reason: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ExecutionRequest(_Validated):
    task_id: UUID
    execution_id: UUID
    workspace_id: UUID | None = None
    cwd: Path
    prompt: str
    mode: PermissionMode
    model: str
    effort: str
    thread_id: str | None = None
    deadline_utc: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ExecutionEvent(_Validated):
    id: UUID
    execution_id: UUID
    sequence: int
    occurred_at: datetime
    kind: EventKind
    payload: dict[str, JsonValue]


@dataclass(frozen=True, slots=True, kw_only=True)
class ActionRequest(_Validated):
    id: UUID
    task_id: UUID
    tool_name: str
    arguments: dict[str, JsonValue]
    resources: tuple[ResourceRef, ...]
    risk: Risk
    effect: Effect
    scope_id: UUID | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResourceRef(_Validated):
    kind: ResourceKind
    canonical_value: str
    fingerprint: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PermissionDecision(_Validated):
    outcome: DecisionOutcome
    reason: str
    grant_id: UUID | None = None
    approval_id: UUID | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolSpec(_Validated):
    name: str
    schema_version: int
    input_schema: dict[str, JsonValue]
    output_schema: dict[str, JsonValue]
    risk: Risk
    effect: Effect
    timeout_s: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolRequest(_Validated):
    id: UUID
    task_id: UUID
    name: str
    arguments: dict[str, JsonValue]


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolContext(_Validated):
    mode: PermissionMode
    granted_resources: tuple[ResourceRef, ...]
    deadline_utc: datetime
    execution_id: UUID
    workspace_id: UUID | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolResult(_Validated):
    request_id: UUID
    success: bool
    output: dict[str, JsonValue]
    error: ErrorInfo | None = None
    observed_effects: tuple[ResourceRef, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class SnapshotRequest(_Validated):
    task_id: UUID
    source: Path
    selected_untracked: tuple[Path, ...]
    scope_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkspaceSnapshot(_Validated):
    id: UUID
    task_id: UUID
    source: Path
    root: Path
    files: tuple[FileFingerprint, ...]
    excluded: tuple[ExcludedFile, ...]
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class FileFingerprint(_Validated):
    relative_path: str
    sha256: str
    size: int
    executable: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class ExcludedFile(_Validated):
    relative_path: str
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeSet(_Validated):
    id: UUID
    workspace_id: UUID
    files: tuple[FileChange, ...]
    diff_artifact: Path
    digest: str
    verification: tuple[VerificationEvidence, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class FileChange(_Validated):
    relative_path: str
    kind: ChangeKind
    before_sha256: str | None = None
    after_sha256: str | None = None
    binary: bool
    executable_before: bool | None = None
    executable_after: bool | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationEvidence(_Validated):
    argv: tuple[str, ...]
    cwd: Path
    exit_code: int | None = None
    started_at: datetime
    finished_at: datetime
    result: str
    artifact: Path | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplyResult(_Validated):
    changeset_id: UUID
    status: ApplyStatus
    applied: tuple[str, ...]
    restored: tuple[str, ...]
    conflicts: tuple[str, ...]
    journal_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class DesktopCapabilities(_Validated):
    backend: str
    absolute_position: bool
    topmost: bool
    notifications: bool
    global_shortcuts: bool
    gui_automation: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Notification(_Validated):
    id: UUID
    title: str
    body: str
    task_id: UUID | None = None
    urgency: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LaunchResult(_Validated):
    application_id: str
    accepted: bool
    process_id: int | None = None
    error: ErrorInfo | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent(_Validated):
    id: UUID
    aggregate_id: UUID
    sequence: int
    kind: EventKind
    occurred_at: datetime
    payload: dict[str, JsonValue]


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskRecord(_Validated):
    id: UUID
    conversation_id: UUID
    submission_id: UUID
    state: TaskState
    mode: PermissionMode
    project: Path | None = None
    created_at: datetime
    updated_at: datetime
    error: ErrorInfo | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskQuery(_Validated):
    limit: int = 50
    cursor: str | None = None
    state: TaskState | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Page[T](_Validated):
    items: tuple[T, ...]
    next_cursor: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ErrorInfo(_Validated):
    code: ErrorCode
    message: str
    retryable: bool
    safe_details: dict[str, JsonValue]


class Clock(Protocol):
    def now_utc(self) -> datetime: ...
    def monotonic(self) -> float: ...


class CancellationToken:
    """Cooperative cancellation for operations between atomic effects."""

    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True
