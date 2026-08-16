"""Main application window for the TwoConnectedTanks GUI launcher.

Builds the Qt UI, wires signals, and connects to :class:`SimulationRunner`
without itself owning any simulation logic (that lives in ``core``).
"""

from __future__ import annotations

import sys

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.simulation_runner import SimulationRunner
from core.validators import validate_executable, validate_time_range


class MainWindow(QMainWindow):
    """Desktop launcher for the compiled TwoConnectedTanks simulation.

    The window exposes an executable picker, start/stop time spin boxes, a
    Run button, a live status bar, and a streaming console panel.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Construct the window and wire all widgets/signals."""
        super().__init__(parent)
        self.setWindowTitle("TwoConnectedTanks Launcher")
        self.resize(640, 480)

        self._runner = SimulationRunner(self)

        self._exe_path_edit: QLineEdit = QLineEdit()
        self._exe_path_edit.setReadOnly(True)
        self._exe_path_edit.setPlaceholderText(
            "Click Browse to select TwoConnectedTanks.exe"
        )

        self._browse_button: QPushButton = QPushButton("Browse")

        # Max start is 3 because the smallest valid stop is start + 1 and
        # stop max is 4, so start can be at most 3.
        self._start_spin: QSpinBox = QSpinBox()
        self._start_spin.setRange(0, 3)
        self._start_spin.setValue(0)

        self._stop_spin: QSpinBox = QSpinBox()
        self._stop_spin.setRange(1, 4)
        self._stop_spin.setValue(4)

        self._run_button: QPushButton = QPushButton("Run")
        self._error_label: QLabel = QLabel("")
        self._error_label.setStyleSheet("color: #c0392b;")
        self._console: QTextEdit = QTextEdit()
        self._console.setReadOnly(True)
        self._console.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self._build_layout()
        self._wire_signals()
        self.statusBar().showMessage("Idle")
        self._refresh_validation()

    def _build_layout(self) -> None:
        """Assemble the widget hierarchy and top-level layout."""
        central = QWidget()
        self.setCentralWidget(central)

        form = QFormLayout()
        form.addRow("Executable path", self._exe_path_edit)
        form.addRow("", self._browse_button)
        form.addRow("Start time (s)", self._start_spin)
        form.addRow("Stop time (s)", self._stop_spin)
        form.addRow("", self._run_button)
        form.addRow("", self._error_label)

        layout = QVBoxLayout(central)
        layout.addLayout(form)
        layout.addWidget(QLabel("Console output:"))
        layout.addWidget(self._console)

    def _wire_signals(self) -> None:
        """Connect widget and runner signals."""
        self._browse_button.clicked.connect(self._on_browse)
        self._run_button.clicked.connect(self._on_run)
        self._exe_path_edit.textChanged.connect(self._refresh_validation)
        self._start_spin.valueChanged.connect(self._refresh_validation)
        self._stop_spin.valueChanged.connect(self._refresh_validation)

        self._runner.output_received.connect(self._append_output)
        self._runner.finished.connect(self._on_finished)

    def _on_browse(self) -> None:
        """Open a file picker restricted to Windows executables."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TwoConnectedTanks executable",
            "",
            "Windows Executable (*.exe);;All Files (*)",
        )
        if path:
            self._exe_path_edit.setText(path)

    def _refresh_validation(self) -> None:
        """Re-validate inputs and toggle the Run button / error label."""
        exe_ok, exe_msg = validate_executable(self._exe_path_edit.text())
        time_ok, time_msg = validate_time_range(
            self._start_spin.value(), self._stop_spin.value()
        )

        if not exe_ok:
            self._error_label.setText(exe_msg or "")
            self._run_button.setEnabled(False)
            return
        if not time_ok:
            self._error_label.setText(time_msg or "")
            self._run_button.setEnabled(False)
            return

        self._error_label.setText("")
        self._run_button.setEnabled(not self._runner.is_running())

    def _on_run(self) -> None:
        """Launch the simulation using the validated inputs."""
        if self._runner.is_running():
            return

        self._console.clear()
        self.statusBar().showMessage("Running\u2026")
        self._run_button.setEnabled(False)

        started = self._runner.start(
            self._exe_path_edit.text(),
            self._start_spin.value(),
            self._stop_spin.value(),
        )
        if not started:
            self.statusBar().showMessage("Failed to start process.")
            self._run_button.setEnabled(True)

    def _append_output(self, text: str) -> None:
        """Append a line of process output to the console panel."""
        self._console.append(text.rstrip("\n"))

    def _on_finished(self, exit_code: int, message: str) -> None:
        """Update status and re-validate inputs before re-enabling Run."""
        self.statusBar().showMessage(message)
        self._refresh_validation()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Stop any running simulation before closing."""
        self._runner.stop()
        super().closeEvent(event)


def run_application() -> int:
    """Create the QApplication and show the main window.

    Returns:
        The application exit code.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_application())
