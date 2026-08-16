"""TwoConnectedTanks GUI Launcher — application entry point.

Run with::

    python main.py
"""

from gui.main_window import run_application


def main() -> None:
    """Launch the PyQt6 application and exit with its return code."""
    raise SystemExit(run_application())


if __name__ == "__main__":
    main()
