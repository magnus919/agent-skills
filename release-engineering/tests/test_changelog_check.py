"""Tests for changelog_check.py.

Covers: Keep a Changelog and Release Please validation, format selection,
--json output, and exit codes.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
CHANGELOG_CHECK = os.path.join(SCRIPTS_DIR, "changelog_check.py")

VALID_CHANGELOG = """\
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New dashboard widget.

## [1.1.0] - 2026-07-01

### Added
- Export to CSV.

### Fixed
- Fixed the retry bug.

[Unreleased]: https://github.com/example/proj/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/example/proj/releases/tag/v1.1.0
"""

VALID_RELEASE_PLEASE = """\
# Changelog

## [0.6.0](https://github.com/magnus919/agent-skills/compare/v0.5.0...v0.6.0) (2026-08-03)

### Features
* add a feature ([abc123](https://github.com/example/proj/commit/abc123))

### Bug Fixes
* fix a bug ([def456](https://github.com/example/proj/commit/def456))

### Reverts
* revert an earlier change ([fedcba](https://github.com/example/proj/commit/fedcba))
"""


def run_changelog(args, cwd=None):
    """Run changelog_check.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, CHANGELOG_CHECK] + args
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)
    return proc.returncode, proc.stdout, proc.stderr


def write_changelog(content):
    """Write changelog content to a temp file and return its path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
        tmp.write(content)
        return tmp.name


class TestChangelogCheckValid(unittest.TestCase):
    """Valid changelogs pass."""

    def test_valid_canonical_changelog(self):
        """Canonical Keep a Changelog file exits 0."""
        path = write_changelog(VALID_CHANGELOG)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 0)
            self.assertIn("valid", out.lower())
        finally:
            os.unlink(path)

    def test_standalone_type_bullets_valid(self):
        """Bullets that name the change type are valid without subsections."""
        content = """\
# Changelog

## [Unreleased]

- Added: widget.
- Fixed: crash.

## [1.0.0] - 2026-01-01

- Added: thing.

[Unreleased]: https://example.com/x
[1.0.0]: https://example.com/x
"""
        path = write_changelog(content)
        try:
            rc, _, _ = run_changelog([path])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_prerelease_version_header_valid(self):
        """Pre-release version headers are allowed."""
        content = """\
# Changelog

## [Unreleased]

- Added: x.

## [1.2.0-rc.1] - 2026-07-10

- Added: y.

[Unreleased]: https://example.com/x
[1.2.0-rc.1]: https://example.com/x
"""
        path = write_changelog(content)
        try:
            rc, _, _ = run_changelog([path])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_default_changelog_filename(self):
        """Without a path argument, CHANGELOG.md in the cwd is checked."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "CHANGELOG.md"), "w") as fh:
                fh.write(VALID_CHANGELOG)
            rc, _, _ = run_changelog([], cwd=tmp)
            self.assertEqual(rc, 0)

    def test_yanked_header_valid(self):
        """A [YANKED] marker is accepted."""
        content = """\
# Changelog

## [Unreleased]

- Added: x.

## [1.0.0] - 2026-01-01 [YANKED]

- Added: broken.

[Unreleased]: https://example.com/x
[1.0.0]: https://example.com/x
"""
        path = write_changelog(content)
        try:
            rc, _, _ = run_changelog([path])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_release_please_format_valid(self):
        """Release Please's dated linked headers and star bullets pass."""
        path = write_changelog(VALID_RELEASE_PLEASE)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 0)
            self.assertIn("release-please", out.lower())
        finally:
            os.unlink(path)

    def test_release_please_explicit_format_valid(self):
        """The Release Please format can be selected explicitly."""
        path = write_changelog(VALID_RELEASE_PLEASE)
        try:
            rc, out, _ = run_changelog([path, "--format", "release-please"])
            self.assertEqual(rc, 0)
            self.assertIn("release-please", out.lower())
        finally:
            os.unlink(path)

    def test_release_please_custom_section_valid(self):
        """Custom Release Please section names remain valid."""
        content = VALID_RELEASE_PLEASE.replace("### Features", "### Documentation")
        path = write_changelog(content)
        try:
            rc, _, _ = run_changelog([path, "--format", "release-please"])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)


class TestChangelogCheckProblems(unittest.TestCase):
    """Each Keep a Changelog violation is reported with exit 1."""

    def test_missing_title_exit_1(self):
        """A missing '# Changelog' title is a problem."""
        content = VALID_CHANGELOG.replace("# Changelog\n\n", "", 1)
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("title", out.lower())
        finally:
            os.unlink(path)

    def test_missing_unreleased_exit_1(self):
        """A missing '## [Unreleased]' section is a problem."""
        content = VALID_CHANGELOG.replace("## [Unreleased]\n\n### Added\n- New dashboard widget.\n\n", "")
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("unreleased", out.lower())
        finally:
            os.unlink(path)

    def test_non_semver_version_exit_1(self):
        """A non-strict-SemVer version header is a problem."""
        content = VALID_CHANGELOG.replace("## [1.1.0] - 2026-07-01", "## [1.1] - 2026-07-01")
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("semver", out.lower())
        finally:
            os.unlink(path)

    def test_invalid_date_exit_1(self):
        """An impossible calendar date is a problem."""
        content = VALID_CHANGELOG.replace("## [1.1.0] - 2026-07-01", "## [1.1.0] - 2026-02-30")
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("date", out.lower())
        finally:
            os.unlink(path)

    def test_malformed_header_exit_1(self):
        """A version header missing its date is malformed."""
        content = VALID_CHANGELOG.replace("## [1.1.0] - 2026-07-01", "## [1.1.0]")
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("malformed", out.lower())
        finally:
            os.unlink(path)

    def test_bad_subsection_heading_exit_1(self):
        """A subsection heading outside the six change types is a problem."""
        content = VALID_CHANGELOG.replace("### Fixed", "### Improvements")
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("improvements", out.lower())
        finally:
            os.unlink(path)

    def test_standalone_bullet_without_type_exit_1(self):
        """A standalone bullet not naming a change type is a problem."""
        content = """\
# Changelog

## [Unreleased]

- Improved speed.

[Unreleased]: https://example.com/x
"""
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("added/changed/deprecated/removed/fixed/security", out.lower())
        finally:
            os.unlink(path)

    def test_missing_reference_link_exit_1(self):
        """A version header without a matching link reference is a problem."""
        content = VALID_CHANGELOG.replace(
            "[1.1.0]: https://github.com/example/proj/releases/tag/v1.1.0\n", ""
        )
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("reference link", out.lower())
        finally:
            os.unlink(path)

    def test_empty_file_exit_1(self):
        """An empty changelog is a problem."""
        path = write_changelog("")
        try:
            rc, out, _ = run_changelog([path])
            self.assertEqual(rc, 1)
            self.assertIn("empty", out.lower())
        finally:
            os.unlink(path)

    def test_malformed_release_please_header_exit_1(self):
        """A Release Please header without its compare link is invalid."""
        content = VALID_RELEASE_PLEASE.replace(
            "## [0.6.0](https://github.com/magnus919/agent-skills/compare/v0.5.0...v0.6.0) (2026-08-03)",
            "## [0.6.0] (2026-08-03)",
        )
        path = write_changelog(content)
        try:
            rc, out, _ = run_changelog([path, "--format", "release-please"])
            self.assertEqual(rc, 1)
            self.assertIn("header", out.lower())
        finally:
            os.unlink(path)

    def test_release_please_rejects_unreleased_section(self):
        """Release Please files must not contain Keep a Changelog Unreleased."""
        path = write_changelog(VALID_RELEASE_PLEASE.replace(
            "# Changelog\n", "# Changelog\n\n## [Unreleased]\n"
        ))
        try:
            rc, out, _ = run_changelog([path, "--format", "release-please"])
            self.assertEqual(rc, 1)
            self.assertIn("unreleased", out.lower())
        finally:
            os.unlink(path)


class TestChangelogCheckExitCodes(unittest.TestCase):
    """Exit codes for missing files and usage errors."""

    def test_missing_file_exit_1(self):
        """A missing changelog file is an input error."""
        rc, _, err = run_changelog(["/nonexistent/CHANGELOG.md"])
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())

    def test_bogus_flag_exit_2(self):
        """An unknown flag is a usage error (exit 2)."""
        rc, _, err = run_changelog(["--bogus"])
        self.assertEqual(rc, 2)
        self.assertIn("usage", err.lower())

    def test_no_traceback_on_bad_file(self):
        """Errors never produce a traceback."""
        rc, out, err = run_changelog(["/nonexistent/CHANGELOG.md"])
        self.assertEqual(rc, 1)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_help_exits_0(self):
        """--help exits 0 and describes usage."""
        rc, out, _ = run_changelog(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("usage", out.lower())
        self.assertIn("changelog_check", out.lower())


class TestChangelogCheckJsonOutput(unittest.TestCase):
    """--json output is machine-parseable."""

    def test_json_valid(self):
        """Valid changelog --json parses with valid=true."""
        path = write_changelog(VALID_CHANGELOG)
        try:
            rc, out, _ = run_changelog([path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertTrue(data["valid"])
            self.assertEqual(data["problem_count"], 0)
            self.assertEqual(data["problems"], [])
            self.assertEqual(data["format"], "keep-a-changelog")
        finally:
            os.unlink(path)

    def test_json_release_please_reports_format(self):
        """JSON reports the selected and detected Release Please format."""
        path = write_changelog(VALID_RELEASE_PLEASE)
        try:
            rc, out, _ = run_changelog([path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["format"], "release-please")
            self.assertEqual(data["detected_format"], "release-please")
        finally:
            os.unlink(path)

    def test_explicit_keep_format_rejects_release_please(self):
        """Explicit Keep a Changelog validation remains strict."""
        path = write_changelog(VALID_RELEASE_PLEASE)
        try:
            rc, out, _ = run_changelog([path, "--format", "keep-a-changelog"])
            self.assertEqual(rc, 1)
            self.assertIn("unreleased", out.lower())
        finally:
            os.unlink(path)

    def test_json_invalid(self):
        """Invalid changelog --json lists per-line problems."""
        path = write_changelog(VALID_CHANGELOG.replace("## [Unreleased]", "## Missing"))
        try:
            rc, out, _ = run_changelog([path, "--json"])
            self.assertEqual(rc, 1)
            data = json.loads(out)
            self.assertFalse(data["valid"])
            self.assertGreater(data["problem_count"], 0)
            for problem in data["problems"]:
                self.assertIn("line", problem)
                self.assertIn("message", problem)
        finally:
            os.unlink(path)

    def test_json_deterministic(self):
        """Two runs produce identical JSON."""
        path = write_changelog(VALID_CHANGELOG)
        try:
            rc1, out1, _ = run_changelog([path, "--json"])
            rc2, out2, _ = run_changelog([path, "--json"])
            self.assertEqual(rc1, 0)
            self.assertEqual(rc2, 0)
            self.assertEqual(out1, out2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
