

from __future__ import annotations

import sys

from PyQt6.QtGui import QCloseEvent, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
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
    """Primary application window for the TwoConnectedTanks launcher."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise widgets, layout, and signal/slot wiring."""
        super().__init__(parent)
        self.setWindowTitle("TwoConnectedTanks Launcher")
        self.resize(700, 520)

        self._runner = SimulationRunner(self)


        self._exe_path_edit: QLineEdit = QLineEdit()
        self._exe_path_edit.setReadOnly(True)
        self._exe_path_edit.setPlaceholderText(
            "Select TwoConnectedTanks executable…"
        )

        self._browse_button: QPushButton = QPushButton("Browse…")

        # Max start is 3 because the smallest valid stop is start + 1 and
        # stop max is 4, so start can be at most 3.
        self._start_spin: QSpinBox = QSpinBox()
        self._start_spin.setRange(0, 3)
        self._start_spin.setValue(0)
        self._start_spin.setSuffix(" s")

        self._stop_spin: QSpinBox = QSpinBox()
        self._stop_spin.setRange(1, 4)
        self._stop_spin.setValue(4)
        self._stop_spin.setSuffix(" s")

        self._run_button: QPushButton = QPushButton("Run Simulation")

        self._error_label: QLabel = QLabel("")
        self._error_label.setStyleSheet("color: #c0392b; font-weight: bold;")

        self._console: QTextEdit = QTextEdit()
        self._console.setReadOnly(True)
        self._console.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._console.setStyleSheet(
            "QTextEdit { font-family: 'Consolas', 'Courier New', monospace; "
            "font-size: 10pt; }"
        )

        self._build_layout()
        self._wire_signals()
        self.statusBar().showMessage("Idle")
        self._refresh_validation()

   

    def _build_layout(self) -> None:
        """Arrange all widgets inside the central widget."""
        central = QWidget()
        self.setCentralWidget(central)

        # Executable row: path + browse side-by-side.
        exe_row = QHBoxLayout()
        exe_row.addWidget(self._exe_path_edit, stretch=1)
        exe_row.addWidget(self._browse_button)

        form = QFormLayout()
        form.addRow("Executable:", exe_row)
        form.addRow("Start time:", self._start_spin)
        form.addRow("Stop time:", self._stop_spin)
        form.addRow("", self._run_button)
        form.addRow("", self._error_label)

        layout = QVBoxLayout(central)
        layout.addLayout(form)
        layout.addWidget(QLabel("Console output:"))
        layout.addWidget(self._console, stretch=1)

   
    def _wire_signals(self) -> None:
        """Connect UI signals to their handler slots."""
        self._browse_button.clicked.connect(self._on_browse)
        self._run_button.clicked.connect(self._on_run)
        self._exe_path_edit.textChanged.connect(self._refresh_validation)
        self._start_spin.valueChanged.connect(self._refresh_validation)
        self._stop_spin.valueChanged.connect(self._refresh_validation)

        self._runner.output_received.connect(self._append_output)
        self._runner.finished.connect(self._on_finished)

    
    def _on_browse(self) -> None:
        """Open a file dialog to select the simulation executable."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TwoConnectedTanks executable",
            "",
            "Windows Executable (*.exe);;All Files (*)",
        )
        if path:
            self._exe_path_edit.setText(path)

    def _refresh_validation(self) -> None:
        """Re-check inputs and enable/disable the Run button accordingly."""
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
        self.statusBar().showMessage("Running…")
        self._run_button.setEnabled(False)

        started = self._runner.start(
            self._exe_path_edit.text(),
            self._start_spin.value(),
            self._stop_spin.value(),
        )
        if not started:
            self.statusBar().showMessage("Failed to start process.")
            self._append_output_coloured(
                "ERROR: Could not start the executable. "
                "Check that the file exists and is a valid Windows PE.",
                QColor("#c0392b"),
            )
            self._run_button.setEnabled(True)

    def _append_output(self, text: str) -> None:
        """Append process output to the console, colour-coded by content."""
        stripped = text.rstrip("\n")
        if not stripped:
            return

        if "LOG_ASSERT" in stripped or "error" in stripped.lower():
            colour = QColor("#c0392b")  # red
        elif "warning" in stripped.lower():
            colour = QColor("#e67e22")  # orange
        elif stripped.startswith("[stderr]"):
            colour = QColor("#c0392b")  # red
        else:
            colour = QColor(self._console.palette().text().color())

        self._append_output_coloured(stripped, colour)

    def _append_output_coloured(self, text: str, colour: QColor) -> None:
        """Insert *text* at the end of the console with the given colour."""
        self._console.setTextColor(colour)
        self._console.append(text)

    def _on_finished(self, exit_code: int, message: str) -> None:
        """Update the status bar and re-enable the Run button."""
        if exit_code == 0:
            colour = QColor("#27ae60")  # green
        else:
            colour = QColor("#c0392b")  # red

        self._append_output_coloured(f"\n── {message}", colour)
        self.statusBar().showMessage(message)
        self._refresh_validation()

   
    def closeEvent(self, event: QCloseEvent) -> None:
        """Terminate any running simulation before closing."""
        self._runner.stop()
        super().closeEvent(event)



def run_application() -> int:
    """Create the QApplication, show the window, and run the event loop."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_application())
