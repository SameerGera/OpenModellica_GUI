

from __future__ import annotations

import os

#: Inclusive lower bound for both start and stop time (seconds).
MIN_TIME: int = 0
#: Exclusive upper bound for stop time. The constraint is ``stop < MAX_TIME``.
MAX_TIME: int = 5


def validate_time_range(start_time: int, stop_time: int) -> tuple[bool, str | None]:
    
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
    
    if not path or not path.strip():
        return False, "No executable path provided."
    if not path.strip().lower().endswith(".exe"):
        return False, "The selected file is not a Windows executable (.exe)."
    if not os.path.isfile(path):
        return False, f"Executable not found at path: {path}"
    return True, None
