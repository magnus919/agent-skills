"""Bounded subprocess tests use tiny Python fixtures, never model inference."""

import sys
import tempfile
import unittest
from pathlib import Path

from verify_export import bounded_command


class OutputBounds(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_command(self, code, **limits):
        return bounded_command(
            [sys.executable, "-c", code], self.root / "out", self.root / "err", **limits
        )

    def test_finite_output_retained(self):
        self.assertEqual(self.run_command("print('RED')"), "RED\n")

    def test_large_output_fails_without_memory_capture(self):
        with self.assertRaisesRegex(RuntimeError, "output limit"):
            self.run_command("print('x'*10000)", max_bytes=1024)
        self.assertTrue((self.root / "out").exists())

    def test_deadline_terminates_own_process(self):
        with self.assertRaisesRegex(TimeoutError, "deadline"):
            self.run_command("import time; time.sleep(10)", timeout=0.1)

    def test_nonzero_exit_preserves_stderr(self):
        with self.assertRaisesRegex(RuntimeError, "exited 3"):
            self.run_command("import sys; print('failure',file=sys.stderr); sys.exit(3)")
        self.assertIn("failure", (self.root / "err").read_text())

    def test_stdin_is_eof(self):
        self.assertEqual(self.run_command("import sys; print(len(sys.stdin.read()))"), "0\n")


if __name__ == "__main__":
    unittest.main()
