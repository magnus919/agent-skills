"""Tests for release_plan_scaffold.py.

Covers: rendered document structure, --output file writing, --json output
with parsed fields, --git-range scope source, determinism, and exit codes.

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
PLAN_SCAFFOLD = os.path.join(SCRIPTS_DIR, "release_plan_scaffold.py")

BASE_ARGS = [
    "--version", "1.2.3",
    "--name", "Acme 1.2.3",
    "--date", "2026-08-15",
    "--owner", "Jane Doe",
    "--milestones", "Branch cut;Release candidate;GA",
    "--scope", "feat: new API;fix: retry bug",
    "--risks", "DB migration late;API contract change",
]


def run_plan(args, cwd=None):
    """Run release_plan_scaffold.py with given args, return (rc, stdout, stderr)."""
    cmd = [sys.executable, PLAN_SCAFFOLD] + args
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)
    return proc.returncode, proc.stdout, proc.stderr


class TestReleasePlanScaffoldRender(unittest.TestCase):
    """Rendered document structure."""

    def test_document_contains_fields(self):
        """The rendered markdown contains the provided fields."""
        rc, out, _ = run_plan(BASE_ARGS)
        self.assertEqual(rc, 0)
        self.assertIn("# Release Plan: Acme 1.2.3", out)
        self.assertIn("| Version | 1.2.3 |", out)
        self.assertIn("| Target date (GA) | 2026-08-15 |", out)
        self.assertIn("| Release manager (DRI) | Jane Doe |", out)

    def test_document_contains_lists(self):
        """Milestones, scope, and risks are rendered as tables."""
        rc, out, _ = run_plan(BASE_ARGS)
        self.assertEqual(rc, 0)
        self.assertIn("| Branch cut | TBD | TBD | TBD |", out)
        self.assertIn("| S-1 | feat: new API | feat | — |", out)
        self.assertIn("| R-1 | DB migration late | TBD | TBD | TBD | TBD |", out)

    def test_standard_sections_present(self):
        """The release plan template structure is complete."""
        rc, out, _ = run_plan(BASE_ARGS)
        self.assertEqual(rc, 0)
        for section in (
            "## Metadata",
            "## 1. Overview and Scope",
            "## 2. Versioning and Artifacts",
            "## 3. Timeline and Milestones",
            "## 4. Owners and RACI",
            "## 5. Risks and Mitigations",
            "## 6. Rollout Plan",
            "## 7. Rollback Contingency",
            "## 8. Communication Plan",
            "## 9. Post-Release Monitoring",
            "## 10. Sign-offs",
        ):
            self.assertIn(section, out)

    def test_default_name_and_placeholders(self):
        """Unspecified fields fall back to deterministic TBD placeholders."""
        rc, out, _ = run_plan(["--version", "1.2.3"])
        self.assertEqual(rc, 0)
        self.assertIn("# Release Plan: Release 1.2.3", out)
        self.assertIn("| Target date (GA) | TBD |", out)
        self.assertIn("| Release manager (DRI) | TBD |", out)

    def test_empty_lists_render_tbd(self):
        """No scope/milestones/risks render TBD placeholder rows."""
        rc, out, _ = run_plan(["--version", "1.2.3"])
        self.assertEqual(rc, 0)
        self.assertIn("_TBD_", out)

    def test_deterministic_output(self):
        """Two runs on identical input produce identical output."""
        rc1, out1, _ = run_plan(BASE_ARGS)
        rc2, out2, _ = run_plan(BASE_ARGS)
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 0)
        self.assertEqual(out1, out2)


class TestReleasePlanScaffoldOutput(unittest.TestCase):
    """--output and --json."""

    def test_output_writes_file(self):
        """--output writes the rendered markdown to the file."""
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "release-plan.md")
            rc, out, _ = run_plan(BASE_ARGS + ["--output", target])
            self.assertEqual(rc, 0)
            self.assertEqual(out, "")
            with open(target, "r") as fh:
                content = fh.read()
            self.assertIn("# Release Plan: Acme 1.2.3", content)

    def test_json_parseable(self):
        """--json emits parsed fields plus the rendered document."""
        rc, out, _ = run_plan(BASE_ARGS + ["--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["version"], "1.2.3")
        self.assertEqual(data["name"], "Acme 1.2.3")
        self.assertEqual(data["date"], "2026-08-15")
        self.assertEqual(data["owner"], "Jane Doe")
        self.assertEqual(data["milestones"], ["Branch cut", "Release candidate", "GA"])
        self.assertEqual(data["scope"], ["feat: new API", "fix: retry bug"])
        self.assertEqual(data["risks"], ["DB migration late", "API contract change"])
        self.assertEqual(data["scope_source"], "flags")
        self.assertIn("# Release Plan: Acme 1.2.3", data["document"])

    def test_json_with_output_writes_both(self):
        """--json plus --output writes the file and prints JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "plan.md")
            rc, out, _ = run_plan(BASE_ARGS + ["--json", "--output", target])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["version"], "1.2.3")
            with open(target, "r") as fh:
                self.assertIn("# Release Plan: Acme 1.2.3", fh.read())

    def test_json_deterministic(self):
        """Two --json runs produce identical output."""
        rc1, out1, _ = run_plan(BASE_ARGS + ["--json"])
        rc2, out2, _ = run_plan(BASE_ARGS + ["--json"])
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 0)
        self.assertEqual(out1, out2)


class TestReleasePlanScaffoldGitRange(unittest.TestCase):
    """--git-range pulls scope from commit subjects."""

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_git_range_scope(self):
        """Commit subjects become the scope items."""
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
            for message in ("feat: widget", "fix: retry"):
                subprocess.run(
                    ["git", "-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "--allow-empty", "-q", "-m", message],
                    cwd=tmp, check=True,
                )
            rc, out, _ = run_plan(
                ["--version", "1.2.3", "--git-range", "{}..HEAD".format(first_sha),
                 "--json"],
                cwd=tmp,
            )
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["scope_source"], "git-range")
            self.assertEqual(data["scope"], ["feat: widget", "fix: retry"])
            # Short commit SHAs are surfaced for the in-scope table.
            self.assertEqual(len(data["scope_sources"]), 2)
            self.assertTrue(all(data["scope_sources"]))
            self.assertIn("feat: widget", data["document"])
            self.assertIn("| feat |", data["document"])

    def test_git_range_failure_exit_1(self):
        """An invalid git range is an input error."""
        rc, _, err = run_plan(
            ["--version", "1.2.3", "--git-range", "nope..HEAD"]
        )
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())


class TestReleasePlanScaffoldExitCodes(unittest.TestCase):
    """Exit codes and usage errors."""

    def test_missing_version_exit_2(self):
        """Missing --version is a usage error (exit 2)."""
        rc, _, err = run_plan(["--name", "X"])
        self.assertEqual(rc, 2)
        self.assertIn("usage", err.lower())

    def test_scope_and_git_range_conflict_exit_2(self):
        """--scope and --git-range together is a usage error."""
        rc, _, _ = run_plan(
            ["--version", "1.2.3", "--scope", "a;b", "--git-range", "main..HEAD"]
        )
        self.assertEqual(rc, 2)

    def test_unwritable_output_exit_1(self):
        """An unwritable output path is an input error."""
        rc, _, err = run_plan(BASE_ARGS + ["--output", "/nonexistent/dir/plan.md"])
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())

    def test_no_traceback_on_error(self):
        """Errors never produce a traceback."""
        rc, out, err = run_plan(
            ["--version", "1.2.3", "--git-range", "nope..HEAD"]
        )
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_help_exits_0(self):
        """--help exits 0 and describes usage."""
        rc, out, _ = run_plan(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("usage", out.lower())
        self.assertIn("release_plan_scaffold", out.lower())


if __name__ == "__main__":
    unittest.main()
