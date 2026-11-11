"""Compose the Qt application and enforce one desktop instance per user data path."""

import hashlib
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QLockFile, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QWindow
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from quill.config.service import ConfigService
from quill.ui.bridge import ExecutionWorker, UiBridge


class InstanceGuard(QObject):
    """An exclusive lock owns the local socket; second launches only request show."""

    showRequested = Signal()

    def __init__(self, data_dir: Path) -> None:
        super().__init__()
        data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        digest = hashlib.sha256(str(data_dir.resolve()).encode()).hexdigest()[:24]
        self._name = "quill-" + digest
        self._lock = QLockFile(str(data_dir / "quill.lock"))
        self._lock.setStaleLockTime(0)
        self._server = QLocalServer(self)
        self._server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        self._server.newConnection.connect(self._receive)
        self._owned = False

    def acquire(self) -> bool:
        if not self._lock.tryLock(0):
            return False
        self._owned = True
        if not self._server.listen(self._name):
            # Only the exclusive lock owner can remove a stale socket, never another live lock.
            QLocalServer.removeServer(self._name)
            if not self._server.listen(self._name):
                self.close()
                raise RuntimeError("Não foi possível abrir o canal local do Quill")
        return True

    def notify_existing(self) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(self._name)
        if not socket.waitForConnected(300):
            return False
        socket.write(b"show\n")
        written = socket.waitForBytesWritten(300)
        socket.disconnectFromServer()
        return written

    @Slot()
    def _receive(self) -> None:
        while self._server.hasPendingConnections():
            socket = self._server.nextPendingConnection()
            if socket is None:
                continue

            def read_message(connection: QLocalSocket = socket) -> None:
                message = connection.readAll().data()
                if message == b"show\n":
                    self.showRequested.emit()
                connection.disconnectFromServer()
                connection.deleteLater()

            socket.readyRead.connect(read_message)
            if socket.bytesAvailable():
                read_message()

    def close(self) -> None:
        if self._owned:
            self._server.close()
            self._lock.unlock()
            self._owned = False


class DesktopRuntime:
    """Own all desktop resources so shutdown has one explicit entry point."""

    def __init__(self, guard: InstanceGuard) -> None:
        self.guard = guard
        self.worker = ExecutionWorker()
        self.bridge = UiBridge(self.worker)
        self.engine = QQmlApplicationEngine()
        self.engine.rootContext().setContextProperty("quillBridge", self.bridge)
        self._closed = False
        self.engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "ui/qml/Main.qml")))
        roots = self.engine.rootObjects()
        if not roots or not isinstance(roots[0], QWindow):
            self.worker.shutdown()
            self.guard.close()
            raise RuntimeError("A interface do Quill não pôde ser carregada")
        self.window: QWindow = roots[0]
        self.guard.showRequested.connect(self.show)
        self.bridge.showRequested.connect(self.show)

    @Slot()
    def show(self) -> None:
        self.window.showNormal()
        self.window.raise_()
        self.window.requestActivate()

    def shutdown(self) -> None:
        if not self._closed:
            self._closed = True
            self.bridge.dispose()
            self.worker.shutdown()
            self.window.close()
            self.guard.close()
            self.engine.deleteLater()
            QCoreApplication.sendPostedEvents(self.engine, QEvent.Type.DeferredDelete)


def create_desktop(data_dir: Path) -> DesktopRuntime | None:
    """Return None for a second launch, before creating any execution worker."""
    application = QApplication.instance()
    if not isinstance(application, QApplication):
        raise RuntimeError("Crie QApplication antes de inicializar o desktop")
    application.setQuitOnLastWindowClosed(False)
    guard = InstanceGuard(data_dir)
    if not guard.acquire():
        if not guard.notify_existing():
            raise RuntimeError("Outra instância está iniciando; tente novamente em instantes")
        return None
    try:
        return DesktopRuntime(guard)
    except Exception:
        guard.close()
        raise


def main() -> int:
    """Run the local preview; Codex and computer tools are intentionally disconnected."""
    QQuickStyle.setStyle("Fusion")
    application = QApplication(sys.argv)
    application.setApplicationName("Quill")
    application.setOrganizationName("Quill")
    runtime = create_desktop(ConfigService().paths.data)
    if runtime is None:
        return 0
    runtime.bridge.exitRequested.connect(application.quit)
    try:
        return application.exec()
    finally:
        runtime.shutdown()
