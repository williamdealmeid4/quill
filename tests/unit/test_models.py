"""Core contracts reject invalid data and impossible task transitions."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from quill.core.errors import DomainError, ErrorCode
from quill.core.events import validate_event, validate_transition
from quill.core.models import DomainEvent, ErrorInfo, EventKind, TaskState

pytestmark = pytest.mark.unit


def event(**changes: object) -> DomainEvent:
    values = dict(
        id=uuid4(),
        aggregate_id=uuid4(),
        sequence=0,
        kind=EventKind.TASK_QUEUED,
        occurred_at=datetime.now(UTC),
        payload={"schema_version": 1},
    )
    values.update(changes)
    return DomainEvent(**values)  # type: ignore[arg-type]


def test_reject_naive_datetime() -> None:
    with pytest.raises(DomainError, match="VALIDATION_FAILED"):
        event(occurred_at=datetime(2026, 1, 1))


def test_json_reject_nan() -> None:
    with pytest.raises(DomainError):
        event(payload={"schema_version": 1, "value": float("nan")})


@pytest.mark.parametrize(
    "state",
    [
        TaskState.SUCCEEDED,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.INTERRUPTED,
        TaskState.BLOCKED,
    ],
)
def test_terminal_cannot_restart(state: TaskState) -> None:
    with pytest.raises(DomainError):
        validate_transition(state, TaskState.RUNNING)


def test_approval_cycle_allowed() -> None:
    validate_transition(TaskState.RUNNING, TaskState.AWAITING_APPROVAL)
    validate_transition(TaskState.AWAITING_APPROVAL, TaskState.RUNNING)


def test_dto_immutable() -> None:
    value = event()
    with pytest.raises(FrozenInstanceError):
        value.sequence = 4  # type: ignore[misc]


def test_error_has_safe_details() -> None:
    value = ErrorInfo(
        code=ErrorCode.PERMISSION_DENIED,
        message="Acesso negado",
        retryable=False,
        safe_details={"scope": "fixture"},
    )
    assert DomainError(value).info == value
    with pytest.raises(DomainError):
        ErrorInfo(
            code=ErrorCode.INTERNAL_ERROR,
            message="Falha",
            retryable=False,
            safe_details={"raw": ValueError("sensitive")},
        )  # type: ignore[dict-item]


def test_validate_event_requires_version() -> None:
    with pytest.raises(DomainError):
        validate_event(event(payload={"schema_version": 2}))
    validate_event(event())


def test_invalid_uuid_rejected() -> None:
    with pytest.raises(DomainError):
        event(id="not-a-uuid")
