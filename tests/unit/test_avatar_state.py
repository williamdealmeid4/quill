"""Presentation reacts to domain facts, not to text or a finished animation."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from quill.avatar.state import AvatarState, AvatarStateManager
from quill.core.models import DomainEvent, EventKind

pytestmark = pytest.mark.unit


class FakeClock:
    value = 0.0

    def monotonic(self) -> float:
        return self.value

    def now_utc(self) -> datetime:
        return datetime.now(UTC)


class FixedRandom:
    def uniform(self, lower: float, upper: float) -> float:
        return lower


def event(kind: EventKind, task_id: UUID, state: str | None = None) -> DomainEvent:
    payload = {"schema_version": 1}
    if state is not None:
        payload["state"] = state
    return DomainEvent(
        id=uuid4(),
        aggregate_id=task_id,
        sequence=0,
        kind=kind,
        occurred_at=datetime.now(UTC),
        payload=payload,
    )


def test_approval_overrides_working() -> None:
    manager = AvatarStateManager()
    task_id = uuid4()
    manager.on_event(event(EventKind.EXECUTION_STARTED, task_id))
    assert (
        manager.on_event(event(EventKind.APPROVAL_REQUESTED, task_id)).state
        is AvatarState.AWAITING_APPROVAL
    )
    assert (
        manager.on_event(event(EventKind.APPROVAL_RESOLVED, task_id)).state is AvatarState.WORKING
    )


def test_error_persists() -> None:
    clock = FakeClock()
    manager = AvatarStateManager(clock=clock)
    manager.on_event(event(EventKind.EXECUTION_FAILED, uuid4()))
    clock.value = 100
    assert manager.tick().state is AvatarState.ERROR


def test_success_returns_to_current_state() -> None:
    clock = FakeClock()
    manager = AvatarStateManager(clock=clock)
    manager.on_event(event(EventKind.TASK_STATE_CHANGED, uuid4(), "succeeded"))
    assert manager.tick().state is AvatarState.SUCCESS
    clock.value = 1.01
    assert manager.tick().state is AvatarState.IDLE


def test_blink_interval_with_fake_clock() -> None:
    clock = FakeClock()
    manager = AvatarStateManager(clock=clock, rng=FixedRandom())
    clock.value = 2.9
    assert not manager.tick().blinking
    clock.value = 3
    assert manager.tick().blinking
    clock.value = 3.2
    assert not manager.tick().blinking


def test_hidden_has_no_frame_ticks() -> None:
    clock = FakeClock()
    manager = AvatarStateManager(clock=clock)
    manager.set_visible(False)
    before = manager.presentation
    clock.value = 100
    assert manager.tick() == before


def test_reduced_motion_static() -> None:
    clock = FakeClock()
    manager = AvatarStateManager(clock=clock)
    manager.set_reduced_motion(True)
    before = manager.presentation
    clock.value = 100
    assert manager.tick() == before
    assert not manager.presentation.blinking


def test_turn_completed_is_verification_not_success() -> None:
    manager = AvatarStateManager()
    assert (
        manager.on_event(event(EventKind.EXECUTION_COMPLETED, uuid4())).state
        is AvatarState.THINKING
    )
