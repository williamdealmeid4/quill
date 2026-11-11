"""Framework-independent service interfaces."""

from collections.abc import AsyncIterator
from typing import Protocol
from uuid import UUID

from quill.core.models import (
    ActionRequest,
    ApplyResult,
    ChangeSet,
    DesktopCapabilities,
    DomainEvent,
    ExecutionEvent,
    ExecutionRequest,
    ExecutorCapabilities,
    LaunchResult,
    Notification,
    Page,
    PermissionDecision,
    SnapshotRequest,
    TaskQuery,
    TaskRecord,
    ToolContext,
    ToolRequest,
    ToolResult,
    ToolSpec,
    WorkspaceSnapshot,
)


class CodexExecutor(Protocol):
    async def inspect(self) -> ExecutorCapabilities: ...
    def run(self, request: ExecutionRequest) -> AsyncIterator[ExecutionEvent]: ...
    async def cancel(self, execution_id: UUID) -> None: ...


class PermissionService(Protocol):
    async def evaluate(self, action: ActionRequest) -> PermissionDecision: ...
    async def resolve(self, approval_id: UUID, approved: bool) -> None: ...


class Tool(Protocol):
    def describe(self) -> ToolSpec: ...
    async def execute(self, request: ToolRequest, context: ToolContext) -> ToolResult: ...


class WorkspaceService(Protocol):
    async def snapshot(self, request: SnapshotRequest) -> WorkspaceSnapshot: ...
    async def compare(self, workspace_id: UUID) -> ChangeSet: ...
    async def apply(self, changeset_id: UUID, approval_id: UUID) -> ApplyResult: ...


class DesktopAdapter(Protocol):
    def capabilities(self) -> DesktopCapabilities: ...
    async def open_application(self, application_id: str) -> LaunchResult: ...
    async def notify(self, notification: Notification) -> None: ...


class MemoryStore(Protocol):
    async def append_event(self, event: DomainEvent) -> None: ...
    async def save_task(self, task: TaskRecord) -> None: ...
    async def list_tasks(self, query: TaskQuery) -> Page[TaskRecord]: ...
