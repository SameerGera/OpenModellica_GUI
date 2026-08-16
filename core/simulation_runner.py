"""Simulation runner that wraps a compiled OpenModelica executable via QProcess.

This module has no knowledge of any GUI widget. It only owns a :class:`QProcess`
and exposes Qt signals that a front-end (``gui.main_window``) connects to.
"""

from __future__ import annotations

import locale
import os

from PyQt6.QtCore import QObject, QProcess, pyqtSignal


class SimulationRunner(QObject):
    """Launch and monitor a compiled OpenModelica simulation executable.

    The runner sets the process working directory to the executable's own
    folder so that sibling OpenModelica runtime DLLs and ``*_init.xml`` are
    resolved correctly on Windows, and so that result files are written next
    to the executable.

    Signals:
        output_received: emitted with a decoded line of stdout/stderr text.
        finished: emitted with ``(exit_code, status_message)`` when the
            process ends.

    Security note:
        The executable path is expected to originate from a read-only
        ``QLineEdit`` populated exclusively via ``QFileDialog``, and
        arguments are passed as a list (no shell expansion).  These
        constraints prevent path-traversal and shell-injection attacks.
    """

    output_received = pyqtSignal(str)
    finished = pyqtSignal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Create a runner with no active process."""
        super().__init__(parent)
        self._process: QProcess | None = None

    def is_running(self) -> bool:
        """Return ``True`` while a simulation process is active."""
        return self._process is not None and self._process.state() != (
            QProcess.ProcessState.NotRunning
        )

    def start(
        self,
        executable_path: str,
        start_time: int,
        stop_time: int,
    ) -> bool:
        """Start the simulation executable.

        Args:
            executable_path: Absolute/relative path to the ``.exe`` file.
            start_time: Simulation start time (integer seconds).
            stop_time: Simulation stop time (integer seconds).

        Returns:
            ``True`` if the process was started successfully, ``False`` if a
            process is already running.
        """
        if self.is_running():
            return False

        self._process = QProcess(self)
        # Resolve to an absolute path *before* extracting the directory so
        # that bare filenames (e.g. "TwoConnectedTanks.exe") don't produce
        # an empty string from os.path.dirname.
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
        """Terminate a running process, if any."""
        if self._process is not None:
            self._process.terminate()
            if not self._process.waitForFinished(3000):
                self._process.kill()

    def _decode(self, data: bytes) -> str:
        """Decode raw process bytes using the preferred locale encoding."""
        encoding = locale.getpreferredencoding(False) or "utf-8"
        return data.decode(encoding, errors="replace")

    def _on_stdout(self) -> None:
        """Emit decoded standard output lines."""
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
        """Re-emit process termination as a friendly status message."""
        status = (
            "Simulation completed"
            if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0
            else "Simulation failed"
        )
        self.finished.emit(exit_code, f"{status} (exit code {exit_code}).")
        self._process = None
