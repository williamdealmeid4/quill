"""A queued Qt bridge around a dedicated asyncio execution thread."""

import asyncio
import threading
from collections.abc import Coroutine
from concurrent.futures import CancelledError, Future
from uuid import uuid4

from PySide6.QtCore import Property, QObject, Signal, Slot

from quill.core.models import JsonValue


class ExecutionWorker(QObject):
    """Own the asyncio loop; emit results without touching the UI from its thread."""

    resultReady = Signal(str, object)
    jobFailed = Signal(str, str)
    jobCancelled = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._loop = asyncio.new_event_loop()
        self._futures: dict[str, Future[JsonValue]] = {}
        self._lock = threading.Lock()
        self._closed = False
        self._thread = threading.Thread(target=self._run, name="quill-execution", daemon=False)
        self._thread.start()

    def _run(self) -> None:
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    @property
    def is_running(self) -> bool:
        return self._thread.is_alive()

    def submit(self, operation: Coroutine[object, object, JsonValue]) -> str:
        """Schedule a trusted application coroutine; never evaluate QML/model text."""
        if self._closed:
            operation.close()
            raise RuntimeError("Worker encerrado")
        identifier = str(uuid4())
        future = asyncio.run_coroutine_threadsafe(operation, self._loop)
        with self._lock:
            self._futures[identifier] = future

        def completed(result: Future[JsonValue]) -> None:
            with self._lock:
                self._futures.pop(identifier, None)
            try:
                value = result.result()
            except CancelledError:
                self.jobCancelled.emit(identifier)
            except Exception:
                # Boundary: never send raw exception text or tracebacks to QML.
                self.jobFailed.emit(identifier, "Não foi possível concluir a prévia.")
            else:
                self.resultReady.emit(identifier, value)

        future.add_done_callback(completed)
        return identifier

    def cancel(self, identifier: str) -> None:
        with self._lock:
            future = self._futures.get(identifier)
        if future is not None:
            future.cancel()

    def shutdown(self) -> None:
        """Cancel cooperative jobs and close the loop before releasing the UI."""
        if self._closed:
            return
        self._closed = True

        async def finish() -> None:
            current = asyncio.current_task()
            pending = [task for task in asyncio.all_tasks() if task is not current]
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            self._loop.stop()

        def begin_shutdown() -> None:
            self._loop.create_task(finish())

        self._loop.call_soon_threadsafe(begin_shutdown)
        self._thread.join(timeout=3)
        if self._thread.is_alive():
            raise RuntimeError("Worker não encerrou no prazo; operação não cooperativa")


class UiBridge(QObject):
    """Presentation intentions only; the real task executor is not connected yet."""

    statusChanged = Signal()
    busyChanged = Signal()
    showRequested = Signal()
    settingsRequested = Signal()
    exitRequested = Signal()

    def __init__(self, worker: ExecutionWorker) -> None:
        super().__init__()
        self.worker = worker
        self._status = "Esta é uma prévia local. Nenhuma tarefa será executada."
        self._busy = False
        self._active: str | None = None
        worker.resultReady.connect(self._completed)
        worker.jobFailed.connect(self._failed)
        worker.jobCancelled.connect(self._cancelled)

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    def _update(self, status: str, busy: bool) -> None:
        self._status, self._busy = status, busy
        self.statusChanged.emit()
        self.busyChanged.emit()

    @Slot()
    def preview(self) -> None:
        if self._busy:
            return
        self._update("Um instante…", True)

        async def respond() -> str:
            await asyncio.sleep(0.6)
            return "Estou por aqui. Pronto para a próxima etapa."

        self._active = self.worker.submit(respond())

    @Slot(str)
    def submit(self, text: str) -> None:
        self._update("O chat ainda não está conectado. Use a prévia para conhecer o Quill.", False)

    @Slot()
    def cancel(self) -> None:
        if self._active is not None:
            self.worker.cancel(self._active)
            self._active = None
        self._update("Prévia interrompida.", False)

    @Slot()
    def settings(self) -> None:
        self.settingsRequested.emit()

    @Slot()
    def requestExit(self) -> None:
        self.exitRequested.emit()

    @Slot(str, object)
    def _completed(self, identifier: str, result: object) -> None:
        if identifier == self._active:
            self._active = None
            self._update(str(result), False)

    @Slot(str, str)
    def _failed(self, identifier: str, message: str) -> None:
        if identifier == self._active:
            self._active = None
            self._update(message, False)

    @Slot(str)
    def _cancelled(self, identifier: str) -> None:
        if identifier == self._active:
            self._active = None
            self._update("Prévia interrompida.", False)
