"""On-disk storage integrity, recovery and pagination."""

import asyncio
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from quill.core.errors import DomainError, ErrorCode
from quill.core.models import (
    DomainEvent,
    EventKind,
    PermissionMode,
    TaskQuery,
    TaskRecord,
    TaskState,
)
from quill.memory.store import SqliteMemoryStore

pytestmark = pytest.mark.integration


def task(conversation_id: object, **changes: object) -> TaskRecord:
    now = datetime.now(UTC)
    values = dict(
        id=uuid4(),
        conversation_id=conversation_id,
        submission_id=uuid4(),
        state=TaskState.QUEUED,
        mode=PermissionMode.READ,
        project=None,
        created_at=now,
        updated_at=now,
        error=None,
    )
    values.update(changes)
    return TaskRecord(**values)  # type: ignore[arg-type]


def test_migration_restart(tmp_path: Path) -> None:
    async def scenario() -> None:
        path = tmp_path / "memory.db"
        conversation = uuid4()
        first = SqliteMemoryStore(path)
        await first.migrate()
        await first.create_conversation(conversation, "fixture")
        record = task(conversation)
        await first.save_task(record)
        await first.close()
        second = SqliteMemoryStore(path)
        try:
            await second.migrate()
            assert (await second.list_tasks(TaskQuery())).items == (record,)
        finally:
            await second.close()
        with sqlite3.connect(path) as connection:
            assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
            assert connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 1

    asyncio.run(scenario())


def test_failed_migration_rolls_back(tmp_path: Path) -> None:
    async def scenario() -> None:
        migration = tmp_path / "bad.sql"
        migration.write_text("CREATE TABLE partial (id INTEGER); INVALID SQL;")
        store = SqliteMemoryStore(tmp_path / "memory.db", migration_path=migration)
        try:
            with pytest.raises(DomainError):
                await store.migrate()
        finally:
            await store.close()
        with sqlite3.connect(tmp_path / "memory.db") as connection:
            assert (
                connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                == []
            )

    asyncio.run(scenario())


def test_fk_enforced(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = SqliteMemoryStore(tmp_path / "memory.db")
        try:
            await store.migrate()
            with pytest.raises(DomainError):
                await store.save_task(task(uuid4()))
            assert (await store.list_tasks(TaskQuery())).items == ()
        finally:
            await store.close()

    asyncio.run(scenario())


def test_state_event_atomic(tmp_path: Path) -> None:
    async def scenario() -> None:
        path = tmp_path / "memory.db"
        store = SqliteMemoryStore(path)
        try:
            await store.migrate()
            conversation = uuid4()
            await store.create_conversation(conversation, "fixture")
            record = task(conversation)
            await store.save_task(record)
            event = DomainEvent(
                id=uuid4(),
                aggregate_id=record.id,
                sequence=1,
                kind=EventKind.TASK_STATE_CHANGED,
                occurred_at=datetime.now(UTC),
                payload={"schema_version": 1},
            )
            await store.transition(record.id, TaskState.QUEUED, TaskState.PREPARING, event)
            with pytest.raises(DomainError):
                await store.transition(record.id, TaskState.PREPARING, TaskState.RUNNING, event)
            assert (await store.list_tasks(TaskQuery())).items[0].state is TaskState.PREPARING
            with sqlite3.connect(path) as connection:
                assert connection.execute("SELECT COUNT(*) FROM task_events").fetchone()[0] == 2
        finally:
            await store.close()

    asyncio.run(scenario())


def test_duplicate_submission_rejected(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = SqliteMemoryStore(tmp_path / "memory.db")
        try:
            await store.migrate()
            conversation = uuid4()
            await store.create_conversation(conversation, "fixture")
            first = task(conversation)
            await store.save_task(first)
            with pytest.raises(DomainError):
                await store.save_task(task(conversation, submission_id=first.submission_id))
        finally:
            await store.close()

    asyncio.run(scenario())


def test_page_cursor_no_duplicates(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = SqliteMemoryStore(tmp_path / "memory.db")
        try:
            await store.migrate()
            conversation = uuid4()
            await store.create_conversation(conversation, "fixture")
            timestamp = datetime.now(UTC)
            for _ in range(5):
                await store.save_task(task(conversation, created_at=timestamp))
            seen = []
            cursor = None
            while True:
                page = await store.list_tasks(TaskQuery(limit=2, cursor=cursor))
                seen.extend(item.id for item in page.items)
                cursor = page.next_cursor
                if cursor is None:
                    break
            assert len(seen) == len(set(seen)) == 5
        finally:
            await store.close()

    asyncio.run(scenario())


def test_disk_full_reports_storage_error(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = SqliteMemoryStore(tmp_path / "memory.db")
        try:
            with (
                patch(
                    "quill.memory.store.sqlite3.connect",
                    side_effect=sqlite3.OperationalError("database or disk is full"),
                ),
                pytest.raises(DomainError) as raised,
            ):
                await store.migrate()
            assert raised.value.info.code is ErrorCode.STORAGE_FULL
        finally:
            await store.close()

    asyncio.run(scenario())


def test_worker_owns_connection(tmp_path: Path) -> None:
    import threading

    async def scenario() -> None:
        original = sqlite3.connect
        owners: list[int] = []

        def connect(path: Path, *, isolation_level: None) -> sqlite3.Connection:
            owners.append(threading.get_ident())
            return original(path, isolation_level=isolation_level)

        store = SqliteMemoryStore(tmp_path / "memory.db")
        try:
            with patch("quill.memory.store.sqlite3.connect", side_effect=connect):
                await store.migrate()
            assert owners and all(owner != threading.get_ident() for owner in owners)
        finally:
            await store.close()

    asyncio.run(scenario())


def test_out_of_order_event_rejected(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = SqliteMemoryStore(tmp_path / "memory.db")
        try:
            await store.migrate()
            conversation = uuid4()
            await store.create_conversation(conversation, "fixture")
            record = task(conversation)
            await store.save_task(record)
            event = DomainEvent(
                id=uuid4(),
                aggregate_id=record.id,
                sequence=2,
                kind=EventKind.EXECUTION_PROGRESS,
                occurred_at=datetime.now(UTC),
                payload={"schema_version": 1},
            )
            with pytest.raises(DomainError):
                await store.append_event(event)
        finally:
            await store.close()

    asyncio.run(scenario())
