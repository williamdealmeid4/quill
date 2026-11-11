"""Pure avatar state selection; animations never decide task success or permissions."""

import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from quill.core.events import validate_event
from quill.core.models import Clock, DomainEvent, EventKind, TaskState


class AvatarState(StrEnum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    WORKING = "working"
    AWAITING_APPROVAL = "awaiting_approval"
    SUCCESS = "success"
    CONFUSED = "confused"
    ERROR = "error"
    SPEAKING = "speaking"


class RandomSource(Protocol):
    def uniform(self, lower: float, upper: float) -> float: ...


class SystemClock:
    def now_utc(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return time.monotonic()


@dataclass(frozen=True, slots=True)
class AvatarPresentation:
    state: AvatarState = AvatarState.IDLE
    visible: bool = True
    size_px: int = 256
    bubble: str | None = None
    reduced_motion: bool = False
    revision: int = 0
    blinking: bool = False


class AvatarStateManager:
    """Prioritize domain facts and keep timing deterministic under an injected clock."""

    def __init__(self, *, clock: Clock | None = None, rng: RandomSource | None = None) -> None:
        self._clock = clock or SystemClock()
        self._rng = rng or random.Random()
        self._tasks: dict[UUID, TaskState] = {}
        self._approvals: set[UUID] = set()
        self._error = False
        self._transient: tuple[AvatarState, float] | None = None
        self._preview: AvatarState | None = None
        self._visible = True
        self._reduced = False
        self._size = 256
        self._blink_until = 0.0
        self._next_blink = self._clock.monotonic() + self._rng.uniform(3, 7)
        self._presentation = AvatarPresentation()

    @property
    def presentation(self) -> AvatarPresentation:
        return self._presentation

    def _select(self, now: float) -> AvatarState:
        if self._preview is not None:
            return self._preview
        if self._error:
            return AvatarState.ERROR
        if self._approvals:
            return AvatarState.AWAITING_APPROVAL
        if any(state in (TaskState.RUNNING, TaskState.APPLYING) for state in self._tasks.values()):
            return AvatarState.WORKING
        if any(
            state in (TaskState.PREPARING, TaskState.VERIFYING) for state in self._tasks.values()
        ):
            return AvatarState.THINKING
        if self._transient is not None and now < self._transient[1]:
            return self._transient[0]
        return AvatarState.IDLE

    def _publish(self, now: float) -> AvatarPresentation:
        state = self._select(now)
        blinking = self._visible and not self._reduced and now < self._blink_until
        current = self._presentation
        values = (state, self._visible, self._size, self._reduced, blinking)
        previous = (
            current.state,
            current.visible,
            current.size_px,
            current.reduced_motion,
            current.blinking,
        )
        if values != previous:
            self._presentation = AvatarPresentation(
                state=state,
                visible=self._visible,
                size_px=self._size,
                reduced_motion=self._reduced,
                blinking=blinking,
                revision=current.revision + 1,
            )
        return self._presentation

    def tick(self) -> AvatarPresentation:
        if not self._visible:
            return self._presentation
        now = self._clock.monotonic()
        if not self._reduced and now >= self._next_blink:
            self._blink_until = now + 0.15
            self._next_blink = now + self._rng.uniform(3, 7)
        return self._publish(now)

    def set_visible(self, visible: bool) -> None:
        if self._visible != visible:
            self._visible = visible
            self._blink_until = 0
            self._next_blink = self._clock.monotonic() + self._rng.uniform(3, 7)
            self._publish(self._clock.monotonic())

    def set_reduced_motion(self, reduced: bool) -> None:
        self._reduced = reduced
        self._blink_until = 0
        self._next_blink = self._clock.monotonic() + self._rng.uniform(3, 7)
        self._publish(self._clock.monotonic())

    def set_size(self, size: int) -> None:
        if type(size) is not int or not 96 <= size <= 512:
            raise ValueError("Tamanho do avatar deve estar entre 96 e 512")
        self._size = size
        self._publish(self._clock.monotonic())

    def preview(self, state: AvatarState) -> AvatarPresentation:
        """Set a presentation-only demo; the next domain event restores factual state."""
        self._preview = state
        return self._publish(self._clock.monotonic())

    def on_event(self, event: DomainEvent) -> AvatarPresentation:
        validate_event(event)
        self._preview = None
        now = self._clock.monotonic()
        task = event.aggregate_id
        if event.kind is EventKind.EXECUTION_STARTED:
            self._tasks[task] = TaskState.RUNNING
        elif event.kind is EventKind.EXECUTION_COMPLETED:
            self._tasks[task] = TaskState.VERIFYING
        elif event.kind is EventKind.APPROVAL_REQUESTED:
            self._approvals.add(task)
        elif event.kind is EventKind.APPROVAL_RESOLVED:
            self._approvals.discard(task)
        elif event.kind is EventKind.EXECUTION_FAILED:
            self._error = True
            self._tasks.pop(task, None)
        elif event.kind is EventKind.TASK_STATE_CHANGED:
            value = event.payload.get("state")
            if not isinstance(value, str):
                raise ValueError("Evento de estado precisa de state")
            state = TaskState(value)
            if state in (
                TaskState.SUCCEEDED,
                TaskState.FAILED,
                TaskState.CANCELLED,
                TaskState.INTERRUPTED,
                TaskState.BLOCKED,
            ):
                self._tasks.pop(task, None)
                self._approvals.discard(task)
                if state is TaskState.FAILED:
                    self._error = True
                elif state is TaskState.SUCCEEDED:
                    self._transient = (AvatarState.SUCCESS, now + 0.8)
                else:
                    self._transient = (AvatarState.CONFUSED, now + 0.8)
            else:
                self._tasks[task] = state
        return self._publish(now)
