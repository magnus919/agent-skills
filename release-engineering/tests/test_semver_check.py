"""Tests for semver_check.py.

Covers: strict SemVer validation (--check), precedence comparison
(--compare), precedence-aware sorting (--sort), --json output, and exit
codes.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
SEMVER_CHECK = os.path.join(SCRIPTS_DIR, "semver_check.py")


def run_semver(args):
    """Run semver_check.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, SEMVER_CHECK] + args
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return proc.returncode, proc.stdout, proc.stderr


class TestSemverCheckValidation(unittest.TestCase):
    """--check validates strict SemVer 2.0.0."""

    def test_valid_version_exit_0(self):
        """A conforming version exits 0."""
        rc, out, _ = run_semver(["--check", "1.2.3"])
        self.assertEqual(rc, 0)
        self.assertIn("valid", out)

    def test_valid_with_prerelease(self):
        """Pre-release versions are valid."""
        rc, out, _ = run_semver(["--check", "1.2.3-alpha.1"])
        self.assertEqual(rc, 0)
        self.assertIn("valid", out)

    def test_valid_with_build_metadata(self):
        """Build metadata is valid."""
        rc, _, _ = run_semver(["--check", "1.2.3+build.5"])
        self.assertEqual(rc, 0)

    def test_zero_version_valid(self):
        """0.x.y versions are valid."""
        rc, _, _ = run_semver(["--check", "0.0.0"])
        self.assertEqual(rc, 0)

    def test_leading_zero_invalid_exit_1(self):
        """Leading zeros are rejected."""
        rc, out, _ = run_semver(["--check", "01.2.3"])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", out)
        self.assertIn("leading zeros", out)

    def test_missing_patch_invalid_exit_1(self):
        """A two-part version is invalid."""
        rc, out, _ = run_semver(["--check", "1.2"])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", out)

    def test_non_numeric_component_invalid(self):
        """Non-numeric components are invalid."""
        rc, out, _ = run_semver(["--check", "1.x.3"])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", out)

    def test_empty_version_invalid(self):
        """An empty version is invalid."""
        rc, out, _ = run_semver(["--check", ""])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", out)

    def test_v_prefix_invalid(self):
        """A 'v' prefix is not part of SemVer."""
        rc, out, _ = run_semver(["--check", "v1.2.3"])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", out)

    def test_leading_zero_prerelease_invalid(self):
        """Numeric pre-release identifiers must not have leading zeros."""
        rc, _, _ = run_semver(["--check", "1.2.3-alpha.01"])
        self.assertEqual(rc, 1)


class TestSemverCheckCompare(unittest.TestCase):
    """--compare applies SemVer precedence."""

    def test_compare_lt(self):
        """Lower precedence prints lt."""
        rc, out, _ = run_semver(["--compare", "1.2.3", "1.2.4"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "lt")

    def test_compare_gt(self):
        """Higher precedence prints gt."""
        rc, out, _ = run_semver(["--compare", "2.0.0", "1.9.9"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "gt")

    def test_compare_eq(self):
        """Equal precedence prints eq."""
        rc, out, _ = run_semver(["--compare", "1.2.3", "1.2.3"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "eq")

    def test_prerelease_sorts_below_release(self):
        """1.0.0-alpha < 1.0.0."""
        rc, out, _ = run_semver(["--compare", "1.0.0-alpha", "1.0.0"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "lt")

    def test_prerelease_numeric_below_alphanumeric(self):
        """Numeric pre-release identifiers sort below alphanumeric ones."""
        rc, out, _ = run_semver(["--compare", "1.0.0-1", "1.0.0-alpha"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "lt")

    def test_build_metadata_ignored(self):
        """Build metadata does not affect precedence."""
        rc, out, _ = run_semver(["--compare", "1.0.0+a", "1.0.0+b"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "eq")

    def test_invalid_compare_exit_1(self):
        """An invalid version in --compare is an input error."""
        rc, _, err = run_semver(["--compare", "1.2.3", "nope"])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", err.lower())


class TestSemverCheckSort(unittest.TestCase):
    """--sort orders versions ascending by precedence."""

    def test_sort_basic(self):
        """Simple numeric ordering."""
        rc, out, _ = run_semver(["--sort", "1.2.3", "1.0.0", "1.2.0"])
        self.assertEqual(rc, 0)
        lines = out.splitlines()
        self.assertEqual(lines, ["1.0.0", "1.2.0", "1.2.3"])

    def test_sort_prerelease_before_release(self):
        """Pre-releases sort before the same core without one."""
        rc, out, _ = run_semver(
            ["--sort", "1.0.0", "1.0.0-beta.2", "1.0.0-alpha.1"]
        )
        self.assertEqual(rc, 0)
        lines = out.splitlines()
        self.assertEqual(lines, ["1.0.0-alpha.1", "1.0.0-beta.2", "1.0.0"])

    def test_sort_build_metadata_keeps_input_order(self):
        """Equal-precedence versions (build only differs) keep input order."""
        rc, out, _ = run_semver(["--sort", "1.0.0+b", "1.0.0+a", "1.0.0+c"])
        self.assertEqual(rc, 0)
        lines = out.splitlines()
        self.assertEqual(lines, ["1.0.0+b", "1.0.0+a", "1.0.0+c"])

    def test_sort_invalid_exit_1(self):
        """An invalid version in --sort is an input error."""
        rc, _, err = run_semver(["--sort", "1.0.0", "2.x.0"])
        self.assertEqual(rc, 1)
        self.assertIn("invalid", err.lower())


class TestSemverCheckJsonOutput(unittest.TestCase):
    """--json output is machine-parseable."""

    def test_check_json_valid(self):
        """Valid --check --json parses with fields."""
        rc, out, _ = run_semver(["--check", "1.2.3", "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertTrue(data["valid"])
        self.assertEqual(data["version"], "1.2.3")
        self.assertEqual(data["parsed"]["major"], 1)

    def test_check_json_invalid(self):
        """Invalid --check --json carries a reason."""
        rc, out, _ = run_semver(["--check", "01.2.3", "--json"])
        self.assertEqual(rc, 1)
        data = json.loads(out)
        self.assertFalse(data["valid"])
        self.assertIsNotNone(data["reason"])

    def test_compare_json(self):
        """--compare --json parses with a relation."""
        rc, out, _ = run_semver(["--compare", "1.0.0", "1.0.1", "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["relation"], "lt")

    def test_sort_json(self):
        """--sort --json parses with a sorted list."""
        rc, out, _ = run_semver(["--sort", "2.0.0", "1.0.0", "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["sorted"], ["1.0.0", "2.0.0"])


class TestSemverCheckExitCodes(unittest.TestCase):
    """Exit codes and usage errors."""

    def test_no_mode_exit_2(self):
        """No mode given is a usage error (exit 2)."""
        rc, _, err = run_semver([])
        self.assertEqual(rc, 2)
        self.assertIn("usage", err.lower())

    def test_conflicting_modes_exit_2(self):
        """--check and --compare together is a usage error."""
        rc, _, _ = run_semver(["--check", "1.0.0", "--compare", "1.0.0", "2.0.0"])
        self.assertEqual(rc, 2)

    def test_no_traceback_on_invalid(self):
        """Invalid input never produces a traceback."""
        rc, out, err = run_semver(["--check", "1.2"])
        self.assertEqual(rc, 1)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_help_exits_0(self):
        """--help exits 0 and describes usage."""
        rc, out, _ = run_semver(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("usage", out.lower())
        self.assertIn("semver_check", out.lower())


if __name__ == "__main__":
    unittest.main()
