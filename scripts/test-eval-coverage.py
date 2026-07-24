#!/usr/bin/env python3
"""Tests for scripts/eval-coverage.py ratchet logic.

Uses a temporary git repository to verify modified-skill detection,
coverage-decrease detection, and threshold behavior.
"""

import json
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

# Import the module under test.  The script is named eval-coverage.py
# (hyphenated), so we load it via importlib rather than a normal import.
import importlib.util  # noqa: E402
from eval_validation import NOT_APPLICABLE  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "eval_coverage", SCRIPT_DIR / "eval-coverage.py"
)
eval_coverage = importlib.util.module_from_spec(_spec)
sys.modules["eval_coverage"] = eval_coverage
_spec.loader.exec_module(eval_coverage)  # type: ignore[union-attr]


def git(repo: str, *args: str) -> str:
    """Run a git command in *repo* and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def write_skill(repo: str, name: str, evals: list[dict] | None = None) -> None:
    """Create a minimal skill directory with an optional evals manifest."""
    skill_dir = Path(repo) / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill {name}.\n---\n\n# {name}\n"
    )
    if evals is not None:
        evals_dir = skill_dir / "evals"
        evals_dir.mkdir(exist_ok=True)
        (evals_dir / "evals.json").write_text(
            json.dumps({"schema_version": 1, "skill_name": name, "evals": evals}, indent=2)
        )


def make_case(case_id: str) -> dict:
    return {"id": case_id, "prompt": "test", "expected_output": "ok", "assertions": ["a"]}


class TestModifiedSkills(unittest.TestCase):
    """modified_skills() must detect changes to any file under a skill dir."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@test.invalid")
        git(self.repo, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _commit(self, msg: str) -> str:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", msg)
        return git(self.repo, "rev-parse", "HEAD")

    def test_skill_md_change_detected(self) -> None:
        write_skill(self.repo, "alpha")
        base = self._commit("initial")
        (Path(self.repo) / "alpha" / "SKILL.md").write_text("changed")
        self._commit("edit SKILL.md")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("alpha"), mods)

    def test_reference_change_detected(self) -> None:
        write_skill(self.repo, "beta")
        ref_dir = Path(self.repo) / "beta" / "references"
        ref_dir.mkdir()
        (ref_dir / "guide.md").write_text("v1")
        base = self._commit("initial")
        (ref_dir / "guide.md").write_text("v2")
        self._commit("edit reference")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("beta"), mods)

    def test_added_skill_detected(self) -> None:
        write_skill(self.repo, "existing")
        base = self._commit("initial")
        write_skill(self.repo, "added")
        self._commit("add skill")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("added"), mods)

    def test_renamed_skill_detected_under_new_name(self) -> None:
        write_skill(self.repo, "before")
        base = self._commit("initial")
        git(self.repo, "mv", "before", "after")
        self._commit("rename skill")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("after"), mods)
        self.assertNotIn(Path("before"), mods)

    def test_deleted_skill_detected_under_old_name(self) -> None:
        write_skill(self.repo, "removed")
        base = self._commit("initial")
        git(self.repo, "rm", "-r", "removed")
        self._commit("delete skill")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("removed"), mods)

    def test_deleted_skill_flows_through_ratchet_without_eval_error(self) -> None:
        write_skill(self.repo, "removed")
        base = self._commit("initial")
        git(self.repo, "rm", "-r", "removed")
        self._commit("delete skill")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            modified = eval_coverage.modified_skills(base)
            current = set(eval_coverage.find_skills())
            without_evals = {
                skill for skill in current if not eval_coverage.check_evals(skill)[0]
            }
            warnings, errors = eval_coverage.evaluate_ratchet(
                modified=modified,
                current=current,
                without_evals=without_evals,
                coverage_pct=100.0,
            )
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("removed"), modified)
        self.assertEqual([], warnings)
        self.assertEqual([], errors)

    def test_script_fixture_and_readme_changes_detected(self) -> None:
        paths = {
            "scripted": Path("scripts") / "run.py",
            "fixtured": Path("fixtures") / "case.txt",
            "documented": Path("README.md"),
        }
        for skill, relative in paths.items():
            write_skill(self.repo, skill)
            target = Path(self.repo) / skill / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("v1")
        base = self._commit("initial")
        for skill, relative in paths.items():
            (Path(self.repo) / skill / relative).write_text("v2")
        self._commit("edit supporting files")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertTrue({Path(name) for name in paths}.issubset(mods))

    def test_nested_change_maps_to_nearest_skill_owner(self) -> None:
        parent = "bundles/example"
        child = "bundles/example/skills/child"
        write_skill(self.repo, parent)
        write_skill(self.repo, child)
        reference = Path(self.repo) / child / "references" / "guide.md"
        reference.parent.mkdir(parents=True)
        reference.write_text("v1")
        base = self._commit("initial")
        reference.write_text("v2")
        self._commit("edit child reference")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path(child), mods)
        self.assertNotIn(Path(parent), mods)

    def test_eval_manifest_deletion_detected(self) -> None:
        write_skill(self.repo, "gamma", evals=[make_case("c1")])
        base = self._commit("initial")
        (Path(self.repo) / "gamma" / "evals" / "evals.json").unlink()
        self._commit("delete evals")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertIn(Path("gamma"), mods)

    def test_unrelated_file_not_detected(self) -> None:
        write_skill(self.repo, "delta")
        (Path(self.repo) / "README.md").write_text("root readme")
        base = self._commit("initial")
        (Path(self.repo) / "README.md").write_text("changed readme")
        self._commit("edit root readme")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            mods = eval_coverage.modified_skills(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertNotIn(Path("delta"), mods)


class TestCoverageDecreased(unittest.TestCase):
    """coverage_decreased() must detect a drop in eval coverage."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@test.invalid")
        git(self.repo, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _commit(self, msg: str) -> str:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", msg)
        return git(self.repo, "rev-parse", "HEAD")

    def test_decrease_detected(self) -> None:
        write_skill(self.repo, "s1", evals=[make_case("c1")])
        write_skill(self.repo, "s2", evals=[make_case("c2")])
        base = self._commit("two skills with evals")
        # Remove evals from s2.
        (Path(self.repo) / "s2" / "evals" / "evals.json").unlink()
        self._commit("remove s2 evals")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            decreased, base_pct, head_pct = eval_coverage.coverage_decreased(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertTrue(decreased)
        self.assertAlmostEqual(base_pct, 100.0)
        self.assertAlmostEqual(head_pct, 50.0)

    def test_replacing_valid_manifest_with_invalid_is_regression(self) -> None:
        write_skill(self.repo, "s1", evals=[make_case("c1")])
        base = self._commit("valid manifest")
        (Path(self.repo) / "s1" / "evals" / "evals.json").write_text(
            json.dumps({"schema_version": 1, "skill_name": "s1", "evals": []}),
            encoding="utf-8",
        )
        self._commit("break manifest")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            decreased, base_pct, head_pct = eval_coverage.coverage_decreased(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertTrue(decreased)
        self.assertAlmostEqual(base_pct, 100.0)
        self.assertAlmostEqual(head_pct, 0.0)

    def test_no_decrease_when_stable(self) -> None:
        write_skill(self.repo, "s1", evals=[make_case("c1")])
        write_skill(self.repo, "s2")
        base = self._commit("one with evals, one without")
        (Path(self.repo) / "s2" / "SKILL.md").write_text("edited")
        self._commit("edit s2")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            decreased, base_pct, head_pct = eval_coverage.coverage_decreased(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertFalse(decreased)
        self.assertAlmostEqual(base_pct, 50.0)
        self.assertAlmostEqual(head_pct, 50.0)

    def test_increase_not_flagged(self) -> None:
        write_skill(self.repo, "s1")
        base = self._commit("no evals")
        write_skill(self.repo, "s1", evals=[make_case("c1")])
        self._commit("add evals")
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            decreased, base_pct, head_pct = eval_coverage.coverage_decreased(base)
        finally:
            eval_coverage.ROOT = old_root
        self.assertFalse(decreased)
        self.assertAlmostEqual(base_pct, 0.0)
        self.assertAlmostEqual(head_pct, 100.0)


class TestRatchetThresholds(unittest.TestCase):
    """Threshold policy must warn at 25% and fail at 50%."""

    def test_below_warning_threshold_is_advisory_only(self) -> None:
        warnings, errors = eval_coverage.evaluate_ratchet(
            modified={Path("alpha")},
            current={Path("alpha")},
            without_evals={Path("alpha")},
            coverage_pct=24.9,
        )
        self.assertEqual([], warnings)
        self.assertEqual([], errors)

    def test_warning_threshold_emits_warning(self) -> None:
        warnings, errors = eval_coverage.evaluate_ratchet(
            modified={Path("alpha")},
            current={Path("alpha")},
            without_evals={Path("alpha")},
            coverage_pct=25.0,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual([], errors)

    def test_warning_band_remains_warning_below_failure_threshold(self) -> None:
        warnings, errors = eval_coverage.evaluate_ratchet(
            modified={Path("alpha")},
            current={Path("alpha")},
            without_evals={Path("alpha")},
            coverage_pct=49.9,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual([], errors)

    def test_failure_threshold_emits_error(self) -> None:
        warnings, errors = eval_coverage.evaluate_ratchet(
            modified={Path("alpha")},
            current={Path("alpha")},
            without_evals={Path("alpha")},
            coverage_pct=50.0,
        )
        self.assertEqual([], warnings)
        self.assertEqual(1, len(errors))

    def test_deleted_skill_does_not_require_new_evals(self) -> None:
        warnings, errors = eval_coverage.evaluate_ratchet(
            modified={Path("removed")},
            current=set(),
            without_evals=set(),
            coverage_pct=100.0,
        )
        self.assertEqual([], warnings)
        self.assertEqual([], errors)


class TestBaseRefValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@test.invalid")
        git(self.repo, "config", "user.name", "Test")
        write_skill(self.repo, "alpha", evals=[make_case("c1")])
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", "initial")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_main_rejects_invalid_modified_from_ref(self) -> None:
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        stderr = io.StringIO()
        try:
            with mock.patch.object(
                sys, "argv", ["eval-coverage.py", "--modified-from", "does-not-exist"]
            ), redirect_stderr(stderr):
                exit_code = eval_coverage.main()
        finally:
            eval_coverage.ROOT = old_root
        self.assertEqual(2, exit_code)
        self.assertEqual(
            "ERROR: invalid --modified-from ref: 'does-not-exist' is not an existing commit\n",
            stderr.getvalue(),
        )

    def test_main_rejects_option_like_modified_from_ref(self) -> None:
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        stderr = io.StringIO()
        try:
            with mock.patch.object(
                sys, "argv", ["eval-coverage.py", "--modified-from=--name-only"]
            ), redirect_stderr(stderr):
                exit_code = eval_coverage.main()
        finally:
            eval_coverage.ROOT = old_root
        self.assertEqual(2, exit_code)
        self.assertEqual(
            "ERROR: invalid --modified-from ref: '--name-only' is not an existing commit\n",
            stderr.getvalue(),
        )

    def test_main_accepts_valid_branch_ref(self) -> None:
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        stderr = io.StringIO()
        try:
            with mock.patch.object(
                sys, "argv", ["eval-coverage.py", "--modified-from", "main", "--json"]
            ), redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                exit_code = eval_coverage.main()
        finally:
            eval_coverage.ROOT = old_root
        self.assertEqual(0, exit_code)
        self.assertEqual("", stderr.getvalue())


class TestCoverageOutput(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-b", "main")
        write_skill(self.repo, "covered", evals=[make_case("c1")])
        write_skill(self.repo, "uncovered")
        git(self.repo, "add", "-A")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_json_names_all_five_states_and_per_skill_values(self) -> None:
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        output = io.StringIO()
        try:
            with mock.patch.object(sys, "argv", ["eval-coverage.py", "--json"]), redirect_stdout(output):
                exit_code = eval_coverage.main()
        finally:
            eval_coverage.ROOT = old_root
        self.assertEqual(0, exit_code)
        report = json.loads(output.getvalue())
        expected = {
            "manifest_present",
            "schema_valid",
            "executable_grader_bindings_present",
            "recent_run_evidence_present",
            "release_gated_evidence_present",
        }
        self.assertEqual(expected, set(report["states"]))
        self.assertEqual("supported", report["states"]["manifest_present"]["assessment"])
        self.assertEqual("supported", report["states"]["schema_valid"]["assessment"])
        for key in (
            "executable_grader_bindings_present",
            "recent_run_evidence_present",
            "release_gated_evidence_present",
        ):
            self.assertEqual("not_assessed", report["states"][key]["assessment"])
            self.assertIsNone(report["states"][key]["count"])
            self.assertIsNone(report["states"][key]["percentage"])
            self.assertTrue(report["states"][key]["reason"])
        for skill in report["skills"]:
            self.assertTrue(expected.issubset(skill))
            self.assertIsInstance(skill["manifest_present"], bool)
            self.assertIn(skill["schema_valid"], (True, False, NOT_APPLICABLE))
            self.assertEqual("not_assessed", skill["executable_grader_bindings_present"])
            self.assertEqual("not_assessed", skill["recent_run_evidence_present"])
            self.assertEqual("not_assessed", skill["release_gated_evidence_present"])

        per_skill = {entry["skill"]: entry for entry in report["skills"]}
        self.assertTrue(per_skill["covered"]["schema_valid"])
        self.assertEqual(NOT_APPLICABLE, per_skill["uncovered"]["schema_valid"])

    def test_human_output_uses_same_state_names_and_not_assessed_wording(self) -> None:
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        output = io.StringIO()
        try:
            with mock.patch.object(sys, "argv", ["eval-coverage.py"]), redirect_stdout(output):
                exit_code = eval_coverage.main()
        finally:
            eval_coverage.ROOT = old_root
        self.assertEqual(0, exit_code)
        text = output.getvalue()
        self.assertIn("manifest_present", text)
        self.assertIn("schema_valid", text)
        self.assertIn("executable_grader_bindings_present: not assessed", text)
        self.assertIn("recent_run_evidence_present: not assessed", text)
        self.assertIn("release_gated_evidence_present: not assessed", text)

    def test_present_invalid_and_missing_manifest_reporting(self) -> None:
        invalid_manifest = Path(self.repo) / "uncovered" / "evals"
        invalid_manifest.mkdir(parents=True, exist_ok=True)
        (invalid_manifest / "evals.json").write_text(
            json.dumps({"schema_version": 1, "skill_name": "uncovered", "evals": []}),
            encoding="utf-8",
        )
        old_root = eval_coverage.ROOT
        eval_coverage.ROOT = Path(self.repo)
        try:
            covered = eval_coverage.check_eval_states(Path("covered"))
            uncovered = eval_coverage.check_eval_states(Path("uncovered"))
            missing = eval_coverage.check_eval_states(Path("missing"))
        finally:
            eval_coverage.ROOT = old_root
        self.assertTrue(covered.states["manifest_present"])
        self.assertTrue(covered.states["schema_valid"])
        self.assertTrue(uncovered.states["manifest_present"])
        self.assertFalse(uncovered.states["schema_valid"])
        self.assertFalse(missing.states["manifest_present"])
        self.assertEqual(NOT_APPLICABLE, missing.states["schema_valid"])


if __name__ == "__main__":
    unittest.main()
