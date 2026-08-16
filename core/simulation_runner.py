

from __future__ import annotations

import locale
import os

from PyQt6.QtCore import QObject, QProcess, pyqtSignal


class SimulationRunner(QObject):
   

    output_received = pyqtSignal(str)
    finished = pyqtSignal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        #Create a runner with no active process.
        super().__init__(parent)
        self._process: QProcess | None = None

    def is_running(self) -> bool:
        #Return True while a simulation process is active.
        return self._process is not None and self._process.state() != (
            QProcess.ProcessState.NotRunning
        )

    def start(
        self,
        executable_path: str,
        start_time: int,
        stop_time: int,
    ) -> bool:
       
        if self.is_running():
            return False

        self._process = QProcess(self)
        exe_dir = os.path.dirname(os.path.abspath(executable_path))
        self._process.setWorkingDirectory(exe_dir)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        arguments = [
            "-override",
            f"startTime={start_time},stopTime={stop_time}",
        ]
        self._process.start(executable_path, arguments)
        return self._process.waitForStarted(3000)

    def stop(self) -> None:
        
        if self._process is not None:
            self._process.terminate()
            if not self._process.waitForFinished(3000):
                self._process.kill()

    def _decode(self, data: bytes) -> str:
        
        encoding = locale.getpreferredencoding(False) or "utf-8"
        return data.decode(encoding, errors="replace")

    def _on_stdout(self) -> None:
        
        if self._process is None:
            return
        self.output_received.emit(
            self._decode(self._process.readAllStandardOutput().data())
        )

    def _on_stderr(self) -> None:
        """Emit decoded standard error lines, tagged for the console."""
        if self._process is None:
            return
        text = self._decode(self._process.readAllStandardError().data())
        self.output_received.emit(f"[stderr] {text}")

    def _on_finished(
        self,
        exit_code: int,
        exit_status: QProcess.ExitStatus,
    ) -> None:
        
        status = (
            "Simulation completed"
            if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0
            else "Simulation failed"
        )
        self.finished.emit(exit_code, f"{status} (exit code {exit_code}).")
        self._process = None
