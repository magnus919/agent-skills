"""Integration tests for the agent-skills validation pipeline.

Tests the full validation flow end-to-end: creating a skill, validating its
structure, checking eval manifests, and verifying coverage reporting.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

from eval_validation import find_skill_manifests, validate_manifest


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _make_skill_dir(tmp: Path, name: str) -> Path:
    """Create a minimal valid skill directory."""
    skill = tmp / name
    skill.mkdir(parents=True)

    # SKILL.md
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill for integration testing.\n---\n\n"
        "# {name}\n\nA test skill for the integration test suite.\n"
    )

    # README.md
    (skill / "README.md").write_text(
        f"# {name}\n\n## Why Install This Skill\n\n"
        "This skill helps with testing the validation pipeline.\n\n"
        "## What You Get\n\n"
        "| File | Purpose |\n|------|--------|\n| SKILL.md | Instructions |\n\n"
        "## Quick Start\n\nNo setup needed.\n\n"
        "## Triggers\n\n- When integration tests run\n\n"
        "## Requirements\n\nPython 3.10+\n"
    )

    # evals/evals.json
    (skill / "evals").mkdir(exist_ok=True)
    manifest = {
        "schema_version": 1,
        "skill_name": name,
        "evals": [
            {
                "id": "int-01",
                "prompt": "Run the skill.",
                "expected_output": "The skill ran successfully.",
                "assertions": ["Skill completes without error."],
            },
            {
                "id": "int-02",
                "prompt": "Test edge case.",
                "expected_output": "Edge case handled.",
                "assertions": ["No crash on edge input."],
            },
            {
                "id": "int-03",
                "prompt": "Verify output format.",
                "expected_output": "Valid JSON output.",
                "assertions": ["Output is valid JSON."],
            },
            {
                "id": "int-04",
                "prompt": "Test with empty input.",
                "expected_output": "Graceful handling.",
                "assertions": ["Returns appropriate error."],
            },
            {
                "id": "int-05",
                "prompt": "Test concurrent access.",
                "expected_output": "Thread-safe operation.",
                "assertions": ["No race conditions."],
            },
        ],
    }
    (skill / "evals" / "evals.json").write_text(json.dumps(manifest, indent=2))

    return skill


class TestValidateEvalsIntegration(unittest.TestCase):
    """Integration tests for eval validation."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "test@example.invalid")
        _git(self.root, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_valid_skill_passes_validation(self) -> None:
        """A properly constructed skill should pass eval validation."""
        skill = _make_skill_dir(self.root, "test-skill")
        manifest_path = skill / "evals" / "evals.json"

        self.assertTrue(manifest_path.exists())
        result = validate_manifest(manifest_path, self.root)
        self.assertEqual(len(result.errors), 0, f"Validation errors: {result.errors}")
        self.assertEqual(result.states.get("schema_valid"), True)

    def test_manifest_with_missing_evals_fails(self) -> None:
        """A manifest without the 'evals' key should fail validation."""
        skill = _make_skill_dir(self.root, "bad-skill")
        (skill / "evals" / "evals.json").write_text(
            json.dumps({"schema_version": 1, "skill_name": "bad-skill"})
        )
        result = validate_manifest(skill / "evals" / "evals.json", self.root)
        self.assertGreater(len(result.errors), 0)

    def test_manifest_with_empty_evals_fails(self) -> None:
        """A manifest with empty evals array should fail."""
        skill = _make_skill_dir(self.root, "empty-skill")
        (skill / "evals" / "evals.json").write_text(
            json.dumps({
                "schema_version": 1,
                "skill_name": "empty-skill",
                "evals": [],
            })
        )
        result = validate_manifest(skill / "evals" / "evals.json", self.root)
        self.assertGreater(len(result.errors), 0)

    def test_manifest_with_invalid_schema_version_fails(self) -> None:
        """A manifest with wrong schema_version should fail."""
        skill = _make_skill_dir(self.root, "wrong-version")
        manifest = json.loads((skill / "evals" / "evals.json").read_text())
        manifest["schema_version"] = 99
        (skill / "evals" / "evals.json").write_text(json.dumps(manifest))
        result = validate_manifest(skill / "evals" / "evals.json", self.root)
        self.assertGreater(len(result.errors), 0)
        self.assertNotEqual(result.states.get("schema_valid"), True)

    def test_find_skill_manifests_discovers_all(self) -> None:
        """find_skill_manifests should discover all skill eval manifests."""
        _make_skill_dir(self.root, "skill-a")
        _make_skill_dir(self.root, "skill-b")

        manifests = find_skill_manifests(self.root)
        self.assertGreaterEqual(len(manifests), 2)

        names = {m.parent.parent.name for m in manifests}
        self.assertIn("skill-a", names)
        self.assertIn("skill-b", names)

    def test_skill_without_evals_dir_is_handled(self) -> None:
        """Skills without evals dir should not cause errors in discovery."""
        skill = self.root / "no-evals-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: no-evals-skill\ndescription: Test.\n---\n# Test\n"
        )
        manifests = find_skill_manifests(self.root)
        no_eval_paths = [m for m in manifests if "no-evals-skill" in str(m)]
        self.assertEqual(len(no_eval_paths), 0)


class TestValidationPipelineEndToEnd(unittest.TestCase):
    """End-to-end tests for the full validation pipeline."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "test@example.invalid")
        _git(self.root, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_validate_evals_accepts_valid_skill(self) -> None:
        """validate-evals.py should accept a valid skill."""
        _make_skill_dir(self.root, "test-skill")
        _git(self.root, "add", "test-skill/")
        _git(self.root, "commit", "-m", "add skill")

        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "validate-evals.py")],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

    def test_eval_coverage_reports_on_skills(self) -> None:
        """eval-coverage.py should report coverage for skills."""
        _make_skill_dir(self.root, "covered-skill")
        _git(self.root, "add", "covered-skill/")
        _git(self.root, "commit", "-m", "add covered skill")

        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "eval-coverage.py")],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        # Coverage script reports (always exits 0 for informational mode)
        self.assertEqual(result.returncode, 0)
        self.assertIn("schema-valid", result.stdout.lower())


class TestScanTechDebt(unittest.TestCase):
    """Integration test for the tech debt scanner."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "test@example.invalid")
        _git(self.root, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_detects_todo_markers(self) -> None:
        """scan-tech-debt.py should detect TODO markers in Python files."""
        test_file = self.root / "module.py"
        test_file.write_text("# TODO(#42): Fix this later\ndef foo(): pass\n")
        _git(self.root, "add", "module.py")

        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "scan-tech-debt.py")],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertIn("TODO", result.stdout)

    def test_reports_zero_for_clean_code(self) -> None:
        """scan-tech-debt.py should report zero for clean code."""
        test_file = self.root / "clean.py"
        test_file.write_text("def foo():\n    return 42\n")
        _git(self.root, "add", "clean.py")

        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "scan-tech-debt.py")],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertIn("No technical debt markers found", result.stdout)
