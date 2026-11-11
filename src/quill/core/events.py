"""Closed state transitions and event validation."""

from quill.core.errors import DomainError, ErrorCode
from quill.core.models import DomainEvent, ErrorInfo, TaskState

_TRANSITIONS: dict[TaskState, frozenset[TaskState]] = {
    TaskState.QUEUED: frozenset(
        [TaskState.PREPARING, TaskState.CANCELLED, TaskState.INTERRUPTED, TaskState.BLOCKED]
    ),
    TaskState.PREPARING: frozenset(
        [
            TaskState.RUNNING,
            TaskState.FAILED,
            TaskState.CANCELLED,
            TaskState.INTERRUPTED,
            TaskState.BLOCKED,
        ]
    ),
    TaskState.RUNNING: frozenset(
        [
            TaskState.AWAITING_APPROVAL,
            TaskState.VERIFYING,
            TaskState.FAILED,
            TaskState.CANCELLED,
            TaskState.INTERRUPTED,
            TaskState.BLOCKED,
        ]
    ),
    TaskState.AWAITING_APPROVAL: frozenset(
        [
            TaskState.RUNNING,
            TaskState.FAILED,
            TaskState.CANCELLED,
            TaskState.INTERRUPTED,
            TaskState.BLOCKED,
        ]
    ),
    TaskState.VERIFYING: frozenset(
        [
            TaskState.RUNNING,
            TaskState.SUCCEEDED,
            TaskState.AWAITING_REVIEW,
            TaskState.FAILED,
            TaskState.CANCELLED,
            TaskState.INTERRUPTED,
            TaskState.BLOCKED,
        ]
    ),
    TaskState.AWAITING_REVIEW: frozenset(
        [TaskState.APPLYING, TaskState.CANCELLED, TaskState.INTERRUPTED, TaskState.BLOCKED]
    ),
    TaskState.APPLYING: frozenset(
        [TaskState.SUCCEEDED, TaskState.FAILED, TaskState.INTERRUPTED, TaskState.BLOCKED]
    ),
}


def validate_transition(old: TaskState, new: TaskState) -> None:
    """Reject transitions not explicitly supported by the task lifecycle."""
    if new not in _TRANSITIONS.get(old, frozenset()):
        raise DomainError(
            ErrorInfo(
                code=ErrorCode.VALIDATION_FAILED,
                message=f"Transição inválida: {old} → {new}",
                retryable=False,
                safe_details={},
            )
        )


def validate_event(event: DomainEvent) -> None:
    """Only version-one payloads enter the domain event log."""
    version = event.payload.get("schema_version")
    if type(version) is not int or version != 1:
        raise DomainError(
            ErrorInfo(
                code=ErrorCode.VALIDATION_FAILED,
                message="Versão de evento inválida",
                retryable=False,
                safe_details={},
            )
        )
