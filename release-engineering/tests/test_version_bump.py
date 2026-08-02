"""Tests for version_bump.py.

Covers: Conventional Commits bump rules (feat/fix/breaking/! and 0.x
handling), pre-release increment semantics, --from-file parsing,
--git-range, --json output, and exit codes.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
VERSION_BUMP = os.path.join(SCRIPTS_DIR, "version_bump.py")


def run_version_bump(args, cwd=None):
    """Run version_bump.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, VERSION_BUMP] + args
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=cwd,
    )
    return proc.returncode, proc.stdout, proc.stderr


def write_temp_file(content, suffix=".txt"):
    """Write content to a temp file and return its path (caller unlinks)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        return tmp.name


class TestVersionBumpBumpRules(unittest.TestCase):
    """Conventional Commits bump rules."""

    def test_feat_bumps_minor(self):
        """feat commits bump minor."""
        commits = write_temp_file("feat: add login\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.3.0", out)
        finally:
            os.unlink(commits)

    def test_fix_bumps_patch(self):
        """fix commits bump patch."""
        commits = write_temp_file("fix(api): retry timeout\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.2.4", out)
        finally:
            os.unlink(commits)

    def test_breaking_change_footer_bumps_major(self):
        """BREAKING CHANGE footer bumps major."""
        commits = write_temp_file("feat: new API\n\nBREAKING CHANGE: endpoint renamed\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("2.0.0", out)
        finally:
            os.unlink(commits)

    def test_bang_type_bumps_major(self):
        """feat! bumps major."""
        commits = write_temp_file("feat!: drop legacy endpoint\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("2.0.0", out)
        finally:
            os.unlink(commits)

    def test_bang_scope_bumps_major(self):
        """feat(scope)! bumps major."""
        commits = write_temp_file("feat(api)!: rename field\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("2.0.0", out)
        finally:
            os.unlink(commits)

    def test_zero_major_breaking_bumps_minor(self):
        """On a 0.x version, breaking changes bump minor instead of major."""
        commits = write_temp_file("feat!: unstable api change\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "0.2.0", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("0.3.0", out)
        finally:
            os.unlink(commits)

    def test_zero_major_feat_bumps_patch(self):
        """On a 0.x version, feat bumps patch."""
        commits = write_temp_file("feat: add helper\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "0.2.0", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("0.2.1", out)
        finally:
            os.unlink(commits)

    def test_other_types_bump_patch(self):
        """chore/docs/refactor commits bump patch."""
        commits = write_temp_file("chore: bump deps\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.2.4", out)
        finally:
            os.unlink(commits)

    def test_breaking_wins_over_feat(self):
        """A breaking change dominates any feat in the batch."""
        commits = write_temp_file("feat: add widget\nfix!: remove endpoint\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("2.0.0", out)
        finally:
            os.unlink(commits)


class TestVersionBumpPrerelease(unittest.TestCase):
    """Pre-release tag semantics."""

    def test_new_prerelease_starts_at_one(self):
        """A fresh pre-release starts at tag.1."""
        commits = write_temp_file("feat: add login\n")
        try:
            rc, out, _ = run_version_bump(
                [
                    "--current-version", "1.2.3",
                    "--commits-file", commits,
                    "--pre-release", "rc",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.3.0-rc.1", out)
        finally:
            os.unlink(commits)

    def test_same_prerelease_series_increments(self):
        """Same tag and numeric suffix increments without bumping core."""
        commits = write_temp_file("feat: add login\n")
        try:
            rc, out, _ = run_version_bump(
                [
                    "--current-version", "1.2.0-alpha.1",
                    "--commits-file", commits,
                    "--pre-release", "alpha",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.2.0-alpha.2", out)
        finally:
            os.unlink(commits)

    def test_different_prerelease_tag_restarts(self):
        """A different tag restarts the series on a fresh core bump."""
        commits = write_temp_file("feat: add login\n")
        try:
            rc, out, _ = run_version_bump(
                [
                    "--current-version", "1.2.0-alpha.1",
                    "--commits-file", commits,
                    "--pre-release", "beta",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.3.0-beta.1", out)
        finally:
            os.unlink(commits)

    def test_invalid_pre_release_choice_exit_2(self):
        """An unknown pre-release tag is a usage error (exit 2)."""
        commits = write_temp_file("feat: x\n")
        try:
            rc, _, _ = run_version_bump(
                [
                    "--current-version", "1.2.3",
                    "--commits-file", commits,
                    "--pre-release", "gamma",
                ]
            )
            self.assertEqual(rc, 2)
        finally:
            os.unlink(commits)


class TestVersionBumpJsonOutput(unittest.TestCase):
    """--json output is machine-parseable."""

    def test_json_parseable(self):
        """--json output parses and has expected fields."""
        commits = write_temp_file("feat: add login\nfix: retry\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits, "--json"]
            )
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["current_version"], "1.2.3")
            self.assertEqual(data["next_version"], "1.3.0")
            self.assertEqual(data["bump"], "minor")
            self.assertEqual(data["commit_count"], 2)
            self.assertEqual(data["breaking_count"], 0)
            self.assertEqual(data["source"], "commits-file")
        finally:
            os.unlink(commits)

    def test_json_reports_breaking(self):
        """Breaking counts are surfaced in JSON."""
        commits = write_temp_file("feat!: break\n")
        try:
            rc, out, _ = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits, "--json"]
            )
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["breaking_count"], 1)
            self.assertEqual(data["bump"], "major")
        finally:
            os.unlink(commits)

    def test_deterministic_output(self):
        """Two runs on the same input produce identical JSON."""
        commits = write_temp_file("feat: a\nfix: b\nchore: c\n")
        try:
            rc1, out1, _ = run_version_bump(
                ["--current-version", "1.0.0", "--commits-file", commits, "--json"]
            )
            rc2, out2, _ = run_version_bump(
                ["--current-version", "1.0.0", "--commits-file", commits, "--json"]
            )
            self.assertEqual(rc1, 0)
            self.assertEqual(rc2, 0)
            self.assertEqual(out1, out2)
        finally:
            os.unlink(commits)


class TestVersionBumpFromFile(unittest.TestCase):
    """--from-file reads package.json / pyproject.toml versions."""

    def test_package_json(self):
        """Reads version from package.json."""
        commits = write_temp_file("feat: add login\n")
        package = write_temp_file('{"name": "x", "version": "2.1.0"}', suffix=".json")
        try:
            rc, out, _ = run_version_bump(
                ["--from-file", package, "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("2.2.0", out)
        finally:
            os.unlink(commits)
            os.unlink(package)

    def test_pyproject_toml(self):
        """Reads version from a [project] table in pyproject.toml."""
        commits = write_temp_file("fix: retry\n")
        toml = write_temp_file(
            "[project]\nname = \"demo\"\nversion = \"3.1.5\"\n", suffix=".toml"
        )
        try:
            rc, out, _ = run_version_bump(
                ["--from-file", toml, "--commits-file", commits]
            )
            self.assertEqual(rc, 0)
            self.assertIn("3.1.6", out)
        finally:
            os.unlink(commits)
            os.unlink(toml)

    def test_from_file_missing_version_exit_1(self):
        """A package.json without a version field is an input error."""
        commits = write_temp_file("feat: x\n")
        package = write_temp_file('{"name": "x"}', suffix=".json")
        try:
            rc, _, err = run_version_bump(
                ["--from-file", package, "--commits-file", commits]
            )
            self.assertEqual(rc, 1)
            self.assertIn("version", err.lower())
        finally:
            os.unlink(commits)
            os.unlink(package)


class TestVersionBumpGitRange(unittest.TestCase):
    """--git-range reads commits from git log."""

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_git_range_bumps_minor(self):
        """git log subjects drive the bump."""
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
            subprocess.run(
                ["git", "-c", "user.name=t", "-c", "user.email=t@t",
                 "commit", "--allow-empty", "-q", "-m", "chore: init"],
                cwd=tmp, check=True,
            )
            first_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=tmp, check=True,
                capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(
                ["git", "-c", "user.name=t", "-c", "user.email=t@t",
                 "commit", "--allow-empty", "-q", "-m", "feat: widget"],
                cwd=tmp, check=True,
            )
            rc, out, _ = run_version_bump(
                ["--current-version", "1.0.0", "--git-range", "{}..HEAD".format(first_sha)],
                cwd=tmp,
            )
            self.assertEqual(rc, 0)
            self.assertIn("1.1.0", out)

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_git_range_failure_exit_1(self):
        """An invalid git range is an input error."""
        rc, _, err = run_version_bump(
            ["--current-version", "1.0.0", "--git-range", "nope..HEAD"]
        )
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())


class TestVersionBumpExitCodes(unittest.TestCase):
    """Exit codes and error handling."""

    def test_no_args_exit_2(self):
        """Missing required arguments is a usage error (exit 2)."""
        rc, _, err = run_version_bump([])
        self.assertEqual(rc, 2)
        self.assertIn("usage", err.lower())

    def test_invalid_current_version_exit_1(self):
        """A non-SemVer current version is an input error."""
        commits = write_temp_file("feat: x\n")
        try:
            rc, _, err = run_version_bump(
                ["--current-version", "not.a.version", "--commits-file", commits]
            )
            self.assertEqual(rc, 1)
            self.assertIn("invalid", err.lower())
        finally:
            os.unlink(commits)

    def test_no_conventional_commits_exit_1(self):
        """Input with no conventional commits is an input error."""
        commits = write_temp_file("merge branch 'main'\n\nsome random text\n")
        try:
            rc, _, err = run_version_bump(
                ["--current-version", "1.2.3", "--commits-file", commits]
            )
            self.assertEqual(rc, 1)
            self.assertIn("no conventional commits", err.lower())
        finally:
            os.unlink(commits)

    def test_missing_commits_file_exit_1(self):
        """A missing commits file is an input error."""
        rc, _, err = run_version_bump(
            ["--current-version", "1.2.3", "--commits-file", "/nonexistent/commits.txt"]
        )
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())

    def test_no_traceback_on_error(self):
        """Errors never produce a Python traceback."""
        rc, out, err = run_version_bump(
            ["--current-version", "1.2.3", "--commits-file", "/nonexistent/x.txt"]
        )
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_help_exits_0(self):
        """--help exits 0 and describes usage."""
        rc, out, _ = run_version_bump(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("usage", out.lower())
        self.assertIn("version_bump", out.lower())


if __name__ == "__main__":
    unittest.main()
