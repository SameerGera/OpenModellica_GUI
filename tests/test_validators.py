\

from __future__ import annotations

import os
import tempfile
import unittest
from core.validators import MAX_TIME, MIN_TIME, validate_executable, validate_time_range


class TestValidateTimeRange(unittest.TestCase):
    """Boundary tests for the ``0 <= start < stop < 5`` constraint."""

    def test_valid_boundaries(self) -> None:
        self.assertEqual(validate_time_range(0, 4), (True, None))

    def test_valid_minimal(self) -> None:
        # Smallest valid non-degenerate interval.
        self.assertEqual(validate_time_range(0, 1), (True, None))

    def test_valid_adjacent(self) -> None:
        self.assertEqual(validate_time_range(2, 3), (True, None))

    def test_invalid_start_below_min(self) -> None:
        ok, msg = validate_time_range(-1, 2)
        self.assertFalse(ok)
        self.assertIn(str(MIN_TIME), msg)

    def test_invalid_equal_start_stop(self) -> None:
        ok, msg = validate_time_range(1, 1)
        self.assertFalse(ok)
        self.assertIn("less than", msg)

    def test_invalid_reversed(self) -> None:
        ok, msg = validate_time_range(3, 1)
        self.assertFalse(ok)

    def test_invalid_stop_at_max(self) -> None:
        ok, msg = validate_time_range(0, 5)
        self.assertFalse(ok)
        self.assertIn(str(MAX_TIME), msg)

    def test_invalid_stop_above_max(self) -> None:
        ok, msg = validate_time_range(2, 6)
        self.assertFalse(ok)

    def test_invalid_both_at_max(self) -> None:
        ok, _ = validate_time_range(4, 4)
        self.assertFalse(ok)

    def test_invalid_both_at_zero(self) -> None:
        ok, msg = validate_time_range(0, 0)
        self.assertFalse(ok)
        self.assertIn("less than", msg)


class TestValidateExecutable(unittest.TestCase):
    

    def test_empty_path(self) -> None:
        ok, msg = validate_executable("")
        self.assertFalse(ok)
        self.assertIn("No executable", msg)

    def test_whitespace_only_path(self) -> None:
        ok, msg = validate_executable("   ")
        self.assertFalse(ok)
        self.assertIn("No executable", msg)

    def test_non_exe_extension(self) -> None:
        ok, msg = validate_executable("/tmp/foo.txt")
        self.assertFalse(ok)
        self.assertIn(".exe", msg)

    def test_missing_exe(self) -> None:
        ok, msg = validate_executable("C:\\does\\not\\exist.exe")
        self.assertFalse(ok)
        self.assertIn("not found", msg)

    def test_existing_exe(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as handle:
            path = handle.name
        try:
            ok, msg = validate_executable(path)
            self.assertTrue(ok)
            self.assertIsNone(msg)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
