

from __future__ import annotations

import locale
import os

from PyQt6.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal


# Windows exit code for STATUS_DLL_NOT_FOUND (0xC0000135).
_DLL_NOT_FOUND_CODE: int = -1073741515


class SimulationRunner(QObject):
    """Asynchronous wrapper around ``QProcess`` for a single simulation run."""

    #: Emitted whenever new text arrives from the process (stdout or stderr).
    output_received = pyqtSignal(str)

    #: Emitted when the process exits.  Arguments: exit_code, status_message.
    finished = pyqtSignal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Create a runner with no active process."""
        super().__init__(parent)
        self._process: QProcess | None = None
        self._collected_stderr: list[str] = []

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
        
        if self.is_running():
            return False

        self._collected_stderr.clear()
        self._process = QProcess(self)

        exe_dir = os.path.dirname(os.path.abspath(executable_path))
        self._process.setWorkingDirectory(exe_dir)

        # Build an environment with the packaged runtime/ on PATH.
        env = self._build_environment(exe_dir)
        self._process.setProcessEnvironment(env)

        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        # OpenModelica compiled executables accept -startTime=N -stopTime=N
        # as dedicated flags (NOT via -override, which is for model params).
        arguments = [
            f"-startTime={start_time}",
            f"-stopTime={stop_time}",
        ]

        self._process.start(executable_path, arguments)
        return self._process.waitForStarted(5000)

    def stop(self) -> None:
        """Terminate a running simulation."""
        if self._process is not None:
            self._process.terminate()
            if not self._process.waitForFinished(3000):
                self._process.kill()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_environment(exe_dir: str) -> QProcessEnvironment:
       
        env = QProcessEnvironment.systemEnvironment()
        runtime_dir = os.path.join(exe_dir, "runtime")

        if os.path.isdir(runtime_dir):
            current_path = env.value("PATH", "")
            env.insert("PATH", runtime_dir + os.pathsep + current_path)

        return env

    def _decode(self, data: bytes) -> str:
        """Decode raw process bytes using the platform's preferred encoding."""
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
        self._collected_stderr.append(text)
        self.output_received.emit(f"[stderr] {text}")

    def _on_finished(
        self,
        exit_code: int,
        exit_status: QProcess.ExitStatus,
    ) -> None:
        """Interpret the exit code and emit a user-friendly message."""
        message = self._interpret_exit(exit_code, exit_status)
        self.finished.emit(exit_code, message)
        self._process = None

    def _interpret_exit(
        self,
        exit_code: int,
        exit_status: QProcess.ExitStatus,
    ) -> str:
        """Return a human-readable description of how the process ended."""
        if exit_status == QProcess.ExitStatus.CrashExit:
            return "Process crashed unexpectedly."

        if exit_code == 0:
            return "Simulation completed successfully (exit code 0)."

        # STATUS_DLL_NOT_FOUND — the runtime DLLs could not be loaded.
        if exit_code == _DLL_NOT_FOUND_CODE:
            return (
                "Missing runtime DLLs (0xC0000135). "
                "Verify that the 'runtime/' folder next to the .exe "
                "contains the required OpenModelica libraries."
            )

        # Check stderr for a known model assertion.
        stderr_text = "".join(self._collected_stderr)
        if "LOG_ASSERT" in stderr_text:
            return (
                f"Simulation terminated by a model assertion (exit code {exit_code}). "
                "See console output above for details."
            )

        return f"Simulation failed (exit code {exit_code})."
