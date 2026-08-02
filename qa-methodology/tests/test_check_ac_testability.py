"""Tests for check-ac-testability.py.

Covers: AC testability classification (vague vs concrete), exit codes,
--help, malformed/missing input handling, and idempotency.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
AC_SCRIPT = os.path.join(SCRIPTS_DIR, "check-ac-testability.py")


def run_ac(args, stdin_data=None):
    """Run check-ac-testability.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, AC_SCRIPT] + args
    proc = subprocess.run(
        cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestAcTestabilityClassification(unittest.TestCase):
    """Vague vs concrete AC classification."""

    def test_vague_should_handle(self):
        """'should handle errors gracefully' is flagged as untestable."""
        spec = "- The API should handle errors gracefully\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 1)
        self.assertIn("FAIL", out)
        self.assertIn("handle", out.lower())

    def test_vague_should_be_efficient(self):
        """'should be efficient' is flagged as untestable."""
        spec = "- The system should be efficient under load\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 1)
        self.assertIn("FAIL", out)

    def test_vague_should_work_properly(self):
        """'should work properly' is flagged as untestable."""
        spec = "- The feature should work properly\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 1)
        self.assertIn("FAIL", out)

    def test_concrete_returns_200(self):
        """'returns 200 with {id} when X' is testable."""
        spec = "- The API returns 200 with {id} when the resource exists\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_concrete_exit_code(self):
        """'exits with code 1' is testable."""
        spec = "- The script exits with code 1 when input is missing\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_concrete_within_time(self):
        """'within 200ms' is testable."""
        spec = "- The search endpoint responds within 200 ms\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_concrete_displays_message(self):
        """'displays an error message' is testable."""
        spec = "- The UI displays an error message when validation fails\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_mixed_input(self):
        """Mixed spec: vague flagged, concrete passed, exit 1."""
        spec = (
            "- The system should handle all edge cases\n"
            "- The API returns 404 when the item does not exist\n"
        )
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 1)
        self.assertIn("FAIL", out)
        self.assertIn("PASS", out)

    def test_all_testable_exit_0(self):
        """All-concrete spec exits 0."""
        spec = (
            "- The API returns 200 with {token} on successful login\n"
            "- The API returns 401 when credentials are invalid\n"
        )
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 0)
        self.assertNotIn("FAIL", out)

    def test_all_vague_exit_1(self):
        """All-vague spec exits 1."""
        spec = (
            "- The system should be robust\n"
            "- The system should be scalable\n"
        )
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 1)

    def test_no_acs_detected_exit_0(self):
        """Input with no AC-like lines exits 0."""
        spec = "# Project Overview\n\nThis is a description of the project.\n"
        rc, out, _ = run_ac([], spec)
        self.assertEqual(rc, 0)
        self.assertIn("No acceptance criteria", out)


class TestAcTestabilityExitCodes(unittest.TestCase):
    """Exit codes match the documented contract."""

    def test_testable_exit_0(self):
        """All-testable input exits 0."""
        spec = "- The endpoint returns 200 when the user is authenticated\n"
        rc, _, _ = run_ac([], spec)
        self.assertEqual(rc, 0)

    def test_untestable_exit_1(self):
        """Untestable criteria exit 1."""
        spec = "- The system should handle concurrency appropriately\n"
        rc, _, _ = run_ac([], spec)
        self.assertEqual(rc, 1)

    def test_missing_file_exit_2(self):
        """Nonexistent file path exits 2."""
        rc, _, err = run_ac(["/nonexistent/spec.md"])
        self.assertEqual(rc, 2)
        self.assertIn("error", err.lower())

    def test_empty_input_exit_2(self):
        """Empty stdin exits 2."""
        rc, _, err = run_ac([], "")
        self.assertEqual(rc, 2)
        self.assertIn("empty", err.lower())


class TestAcTestabilityNoTraceback(unittest.TestCase):
    """Malformed input never produces a Python traceback."""

    def test_no_traceback_missing_file(self):
        """No traceback on nonexistent file."""
        rc, out, err = run_ac(["/nonexistent/spec.md"])
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_no_traceback_empty_input(self):
        """No traceback on empty input."""
        rc, out, err = run_ac([], "")
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)


class TestAcTestabilityHelp(unittest.TestCase):
    """--help works correctly."""

    def test_help_exits_0(self):
        """--help exits 0."""
        rc, out, _ = run_ac(["--help"])
        self.assertEqual(rc, 0)

    def test_help_has_usage(self):
        """--help output describes usage."""
        rc, out, _ = run_ac(["--help"])
        self.assertIn("usage", out.lower())
        self.assertIn("check-ac-testability", out.lower())


class TestAcTestabilityIdempotency(unittest.TestCase):
    """Running twice on the same input yields identical output."""

    def test_idempotent_output(self):
        """Two runs produce identical stdout."""
        spec = (
            "- The API should handle rate limiting\n"
            "- The API returns 429 when the rate limit is exceeded\n"
        )
        rc1, out1, _ = run_ac([], spec)
        rc2, out2, _ = run_ac([], spec)
        self.assertEqual(rc1, rc2)
        self.assertEqual(out1, out2)

    def test_no_input_mutation(self):
        """Input file is not modified."""
        spec = "- The API returns 200 with {id} when X\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp:
            tmp.write(spec)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "r") as f:
                before = f.read()
            rc, _, _ = run_ac([tmp_path])
            self.assertEqual(rc, 0)
            with open(tmp_path, "r") as f:
                after = f.read()
            self.assertEqual(before, after)
        finally:
            os.unlink(tmp_path)


class TestAcTestabilityFileInput(unittest.TestCase):
    """File path input works correctly."""

    def test_file_input(self):
        """Reading from a file path works."""
        spec = "- The API returns 201 when the resource is created\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp:
            tmp.write(spec)
            tmp_path = tmp.name
        try:
            rc, out, _ = run_ac([tmp_path])
            self.assertEqual(rc, 0)
            self.assertIn("PASS", out)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
