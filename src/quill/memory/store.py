"""Single-worker SQLite access, transactional migrations and task transitions."""

import asyncio
import base64
import binascii
import errno
import hashlib
import json
import sqlite3
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from quill.core.errors import DomainError, ErrorCode
from quill.core.events import validate_event, validate_transition
from quill.core.models import (
    DomainEvent,
    ErrorInfo,
    EventKind,
    Page,
    PermissionMode,
    TaskQuery,
    TaskRecord,
    TaskState,
)


def _error(code: ErrorCode, message: str) -> DomainError:
    return DomainError(ErrorInfo(code=code, message=message, retryable=False, safe_details={}))


class SqliteMemoryStore:
    """Own a connection exclusively on one persistence worker thread."""

    def __init__(self, path: Path, *, migration_path: Path | None = None) -> None:
        self.path = path
        self._migration = migration_path or Path(__file__).parent / "migrations/001_initial.sql"
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="quill-storage")
        self._connection: sqlite3.Connection | None = None
        self._closed = False

    async def _run[T](self, operation: Callable[[], T]) -> T:
        if self._closed:
            raise _error(ErrorCode.INTERNAL_ERROR, "Armazenamento encerrado")
        return await asyncio.wrap_future(self._pool.submit(self._guard, operation))

    def _guard[T](self, operation: Callable[[], T]) -> T:
        try:
            return operation()
        except sqlite3.Error as error:
            full = getattr(error, "sqlite_errorcode", None) == sqlite3.SQLITE_FULL
            if full or "disk is full" in str(error):
                raise _error(
                    ErrorCode.STORAGE_FULL, "Espaço insuficiente no armazenamento"
                ) from error
            if isinstance(error, sqlite3.IntegrityError):
                raise _error(
                    ErrorCode.VALIDATION_FAILED, "Conflito de integridade dos dados"
                ) from error
            raise _error(ErrorCode.INTERNAL_ERROR, "Falha no armazenamento SQLite") from error

        except OSError as error:
            code = (
                ErrorCode.STORAGE_FULL if error.errno == errno.ENOSPC else ErrorCode.INTERNAL_ERROR
            )
            raise _error(code, "Falha no acesso ao armazenamento") from error

    def _db(self) -> sqlite3.Connection:
        if self._connection is None:
            raise _error(ErrorCode.INTERNAL_ERROR, "Migração necessária antes da operação")
        return self._connection

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._db()
        connection.execute("BEGIN IMMEDIATE")
        try:
            yield connection
            connection.execute("COMMIT")
        except BaseException:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise

    async def migrate(self) -> None:
        """Apply version one atomically and verify the installed checksum."""
        await self._run(self._migrate)

    def _migrate(self) -> None:
        if self._connection is None:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            self._connection = sqlite3.connect(self.path, isolation_level=None)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA busy_timeout=5000")
        script = self._migration.read_text(encoding="utf-8")
        checksum = hashlib.sha256(script.encode()).hexdigest()
        with self._transaction() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, "
                "checksum TEXT NOT NULL)"
            )
            previous = connection.execute(
                "SELECT version, checksum FROM schema_migrations"
            ).fetchall()
            if previous:
                if (
                    len(previous) != 1
                    or previous[0]["version"] != 1
                    or previous[0]["checksum"] != checksum
                ):
                    raise _error(
                        ErrorCode.VALIDATION_FAILED, "Versão/checksum de migração incompatível"
                    )
                return
            # This controlled migration contains no triggers or semicolons inside literals.
            for statement in script.split(";"):
                if statement.strip():
                    connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations VALUES (?, ?, ?)",
                (1, datetime.now(UTC).isoformat(), checksum),
            )

    async def create_conversation(self, conversation_id: UUID, title: str) -> None:
        """Create the conversation required by a task's foreign key."""

        def operation() -> None:
            now = datetime.now(UTC).isoformat()
            with self._transaction() as connection:
                connection.execute(
                    "INSERT INTO conversations VALUES (?, ?, ?, ?)",
                    (str(conversation_id), title, now, now),
                )

        await self._run(operation)

    def _insert_event(self, event: DomainEvent) -> None:
        validate_event(event)
        previous = (
            self._db()
            .execute(
                "SELECT MAX(sequence) FROM task_events WHERE task_id=?", (str(event.aggregate_id),)
            )
            .fetchone()[0]
        )
        expected = 0 if previous is None else previous + 1
        if event.sequence != expected:
            raise _error(ErrorCode.VALIDATION_FAILED, "Sequência de evento inválida")
        self._db().execute(
            "INSERT INTO task_events VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(event.id),
                str(event.aggregate_id),
                event.sequence,
                event.kind.value,
                json.dumps(event.payload, ensure_ascii=False, allow_nan=False),
                event.occurred_at.isoformat(),
            ),
        )

    async def append_event(self, event: DomainEvent) -> None:
        """Append a non-transition event without bypassing state invariants."""
        if event.kind in (EventKind.TASK_STATE_CHANGED, EventKind.TASK_QUEUED):
            raise _error(ErrorCode.VALIDATION_FAILED, "Use a operação transacional da tarefa")

        def operation() -> None:
            with self._transaction():
                self._insert_event(event)

        await self._run(operation)

    async def save_task(self, task: TaskRecord) -> None:
        """Insert a queued task and its initial event; never overwrite its state."""
        if task.state is not TaskState.QUEUED or task.error is not None:
            raise _error(ErrorCode.VALIDATION_FAILED, "Nova tarefa deve estar na fila, sem erro")

        def operation() -> None:
            with self._transaction() as connection:
                connection.execute(
                    "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(task.id),
                        str(task.conversation_id),
                        str(task.submission_id),
                        task.state.value,
                        task.mode.value,
                        str(task.project) if task.project is not None else None,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat(),
                        None,
                    ),
                )
                self._insert_event(
                    DomainEvent(
                        id=uuid4(),
                        aggregate_id=task.id,
                        sequence=0,
                        kind=EventKind.TASK_QUEUED,
                        occurred_at=task.created_at,
                        payload={"schema_version": 1},
                    )
                )

        await self._run(operation)

    async def transition(
        self, task_id: UUID, expected_state: TaskState, next_state: TaskState, event: DomainEvent
    ) -> None:
        """Compare-and-set state together with the associated event."""
        validate_transition(expected_state, next_state)
        validate_event(event)
        if event.aggregate_id != task_id or event.kind is not EventKind.TASK_STATE_CHANGED:
            raise _error(ErrorCode.VALIDATION_FAILED, "Evento não corresponde à transição")

        def operation() -> None:
            with self._transaction() as connection:
                changed = connection.execute(
                    "UPDATE tasks SET state=?,updated_at=? WHERE id=? AND state=?",
                    (
                        next_state.value,
                        event.occurred_at.isoformat(),
                        str(task_id),
                        expected_state.value,
                    ),
                )
                if changed.rowcount != 1:
                    raise _error(ErrorCode.VALIDATION_FAILED, "Estado atual diverge da transição")
                self._insert_event(event)

        await self._run(operation)

    async def list_tasks(self, query: TaskQuery) -> Page[TaskRecord]:
        """Page consistently by creation timestamp and UUID."""

        def operation() -> Page[TaskRecord]:
            conditions: list[str] = []
            values: list[str | int] = []
            if query.state is not None:
                conditions.append("state=?")
                values.append(query.state.value)
            if query.cursor is not None:
                try:
                    cursor = json.loads(
                        base64.b64decode(query.cursor, altchars=b"-_", validate=True)
                    )
                except (ValueError, binascii.Error, UnicodeError) as error:
                    raise _error(ErrorCode.VALIDATION_FAILED, "Cursor inválido") from error
                if (
                    not isinstance(cursor, list)
                    or len(cursor) != 2
                    or not all(isinstance(x, str) for x in cursor)
                ):
                    raise _error(ErrorCode.VALIDATION_FAILED, "Cursor inválido")
                conditions.append("(created_at,id) > (?,?)")
                values.extend(cursor)
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            values.append(query.limit + 1)
            rows = (
                self._db()
                .execute("SELECT * FROM tasks" + where + " ORDER BY created_at,id LIMIT ?", values)
                .fetchall()
            )
            items = tuple(self._task(row) for row in rows[: query.limit])
            next_cursor = None
            if len(rows) > query.limit:
                last = items[-1]
                next_cursor = base64.urlsafe_b64encode(
                    json.dumps([last.created_at.isoformat(), str(last.id)]).encode()
                ).decode()
            return Page(items=items, next_cursor=next_cursor)

        return await self._run(operation)

    @staticmethod
    def _task(row: sqlite3.Row) -> TaskRecord:
        error = None
        if row["error_json"] is not None:
            value = json.loads(row["error_json"])
            error = ErrorInfo(
                code=ErrorCode(value["code"]),
                message=value["message"],
                retryable=value["retryable"],
                safe_details=value["safe_details"],
            )
        return TaskRecord(
            id=UUID(row["id"]),
            conversation_id=UUID(row["conversation_id"]),
            submission_id=UUID(row["submission_id"]),
            state=TaskState(row["state"]),
            mode=PermissionMode(row["mode"]),
            project=Path(row["project_path"]) if row["project_path"] is not None else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            error=error,
        )

    async def close(self) -> None:
        """Close the connection on its owner thread before stopping the worker."""
        if self._closed:
            return

        def operation() -> None:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

        await self._run(operation)
        self._closed = True
        await asyncio.to_thread(self._pool.shutdown, wait=True)
