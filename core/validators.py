"""Pure validation logic for the TwoConnectedTanks GUI launcher.

This module intentionally has **no** Qt / PyQt dependencies so that it can be
unit-tested in isolation (see ``tests/test_validators.py``) and reused by
different front-ends.
"""

from __future__ import annotations

import os

#: Inclusive lower bound for both start and stop time (seconds).
MIN_TIME: int = 0
#: Exclusive upper bound for stop time. The constraint is ``stop < MAX_TIME``.
MAX_TIME: int = 5


def validate_time_range(start_time: int, stop_time: int) -> tuple[bool, str | None]:
    """Validate the simulation start/stop time pair.

    The enforced constraint is ``0 <= start_time < stop_time < 5``.

    Args:
        start_time: Requested simulation start time (integer seconds).
        stop_time: Requested simulation stop time (integer seconds).

    Returns:
        A ``(is_valid, error_message)`` tuple. When valid, ``error_message``
        is ``None``; otherwise it is a human-readable explanation.
    """
    if start_time < MIN_TIME:
        return False, f"Start time must be >= {MIN_TIME} (got {start_time})."
    if stop_time >= MAX_TIME:
        return False, f"Stop time must be < {MAX_TIME} (got {stop_time})."
    if start_time >= stop_time:
        return False, (
            f"Start time must be strictly less than stop time "
            f"(got start={start_time}, stop={stop_time})."
        )
    return True, None


def validate_executable(path: str) -> tuple[bool, str | None]:
    """Validate that ``path`` points to an existing Windows ``.exe`` file.

    Args:
        path: Filesystem path to the compiled simulation executable.

    Returns:
        A ``(is_valid, error_message)`` tuple. ``error_message`` is ``None``
        when the path is acceptable.
    """
    if not path or not path.strip():
        return False, "No executable path provided."
    if not path.strip().lower().endswith(".exe"):
        return False, "The selected file is not a Windows executable (.exe)."
    if not os.path.isfile(path):
        return False, f"Executable not found at path: {path}"
    return True, None
