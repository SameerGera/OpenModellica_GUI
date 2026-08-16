"""Entry point for the TwoConnectedTanks GUI launcher application.

Launches the :class:`gui.main_window.MainWindow` inside a ``QApplication``.
"""

from gui.main_window import run_application


def main() -> None:
    """Run the application and propagate its exit code."""
    raise SystemExit(run_application())


if __name__ == "__main__":
    main()
