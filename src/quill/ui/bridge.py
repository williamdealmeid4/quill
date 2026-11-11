"""A queued Qt bridge around a dedicated asyncio execution thread."""

import asyncio
import threading
from collections.abc import Coroutine
from concurrent.futures import CancelledError, Future
from uuid import uuid4

from PySide6.QtCore import Property, QObject, Qt, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QBitmap, QDesktopServices, QImage, QRegion, QWindow

from quill.avatar.assets import RESOURCE_ROOT, load_avatar
from quill.avatar.state import AvatarState, AvatarStateManager
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

    avatarChanged = Signal()
    avatarVisibleChanged = Signal()
    avatarSizeChanged = Signal()
    reducedMotionChanged = Signal()
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
        self._manifest = load_avatar(RESOURCE_ROOT / "assets/avatars/quill")
        self._avatar_state = AvatarStateManager()
        self._avatar_visible = True
        self._surfaces: dict[str, bool] = {}
        self._mask_image = QImage(str(next(iter(self._manifest.atlases.values())).path))
        self._animation = QTimer(self)
        self._animation.setInterval(50)
        self._animation.timeout.connect(self._tick_avatar)
        self._reset = QTimer(self)
        self._reset.setSingleShot(True)
        self._reset.timeout.connect(self._idle_avatar)
        worker.resultReady.connect(self._completed)
        worker.jobFailed.connect(self._failed)
        worker.jobCancelled.connect(self._cancelled)

    @Property(dict, notify=avatarChanged)
    def avatar(self) -> dict[str, JsonValue]:
        presentation = self._avatar_state.presentation
        animation = self._manifest.states[presentation.state.value]
        first = animation.frames[0]
        atlas = self._manifest.atlases[first.atlas]
        frames: list[JsonValue] = [
            {"x": frame.x, "y": frame.y, "width": frame.width, "height": frame.height}
            for frame in animation.frames
        ]
        return {
            "source": atlas.path.as_uri(),
            "width": first.width,
            "height": first.height,
            "atlasWidth": atlas.width,
            "atlasHeight": atlas.height,
            "frames": frames,
            "fps": animation.fps,
            "loop": animation.loop,
            "state": presentation.state.value,
            "blinking": presentation.blinking,
            "reducedMotion": presentation.reduced_motion,
        }

    @Property(bool, notify=avatarVisibleChanged)
    def avatarVisible(self) -> bool:
        return self._avatar_visible

    @Property(int, notify=avatarSizeChanged)
    def avatarSize(self) -> int:
        return self._avatar_state.presentation.size_px

    @Property(bool, notify=reducedMotionChanged)
    def reducedMotion(self) -> bool:
        return self._avatar_state.presentation.reduced_motion

    @property
    def animation_active(self) -> bool:
        return self._animation.isActive()

    @Slot()
    def _tick_avatar(self) -> None:
        before = self._avatar_state.presentation
        if self._avatar_state.tick() != before:
            self.avatarChanged.emit()

    @Slot()
    def _idle_avatar(self) -> None:
        self._avatar_state.preview(AvatarState.IDLE)
        self.avatarChanged.emit()

    @Slot(str, bool)
    def setSurfaceActive(self, name: str, active: bool) -> None:
        if name not in ("panel", "floating"):
            return
        self._surfaces[name] = active
        visible = any(self._surfaces.values())
        self._avatar_state.set_visible(visible)
        if visible and not self.reducedMotion:
            self._animation.start()
        else:
            self._animation.stop()

    @Slot(int)
    def setAvatarSize(self, size: int) -> None:
        if not 96 <= size <= 256:
            return
        self._avatar_state.set_size(size)
        self.avatarSizeChanged.emit()
        self.avatarChanged.emit()

    @Slot(bool)
    def setReducedMotion(self, reduced: bool) -> None:
        self._avatar_state.set_reduced_motion(reduced)
        self.reducedMotionChanged.emit()
        self.avatarChanged.emit()
        if reduced:
            self._animation.stop()
        elif any(self._surfaces.values()):
            self._animation.start()

    @Slot()
    def hideAvatar(self) -> None:
        self._avatar_visible = False
        self.avatarVisibleChanged.emit()
        self.setSurfaceActive("floating", False)

    @Slot()
    def showAvatar(self) -> None:
        self._avatar_visible = True
        self.avatarVisibleChanged.emit()

    @Slot()
    def showPanel(self) -> None:
        self.showRequested.emit()

    @Slot()
    def openArtwork(self) -> None:
        path = next(iter(self._manifest.atlases.values())).path
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            self._update("Não foi possível abrir a imagem original.", False)

    @Slot(QObject, int, int)
    def applyAvatarMask(self, window: QObject, width: int, height: int) -> None:
        if not isinstance(window, QWindow) or width < 1 or height < 1:
            return
        scaled = self._mask_image.scaled(
            width,
            height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        window.setMask(QRegion(QBitmap.fromImage(scaled.createAlphaMask())))

    def dispose(self) -> None:
        self._animation.stop()
        self._reset.stop()

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
        self._update("Testando a resposta local do Quill…", True)
        self._avatar_state.preview(AvatarState.WORKING)
        self.avatarChanged.emit()

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
        self._idle_avatar()

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
            self._avatar_state.preview(AvatarState.SUCCESS)
            self.avatarChanged.emit()
            self._reset.start(800)

    @Slot(str, str)
    def _failed(self, identifier: str, message: str) -> None:
        if identifier == self._active:
            self._active = None
            self._update(message, False)
            self._avatar_state.preview(AvatarState.ERROR)
            self.avatarChanged.emit()

    @Slot(str)
    def _cancelled(self, identifier: str) -> None:
        if identifier == self._active:
            self._active = None
            self._update("Prévia interrompida.", False)
