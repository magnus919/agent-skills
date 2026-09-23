"""Paired-eval selection must never present a truncated subset as complete."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.selection import (
    changed_paths,
    manifests_for_paths,
    render_summary,
    select,
    selection_evidence,
)


class SelectionTests(unittest.TestCase):
    def test_selects_changed_skills_once_and_ignores_unrelated_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("alpha", "beta"):
                manifest = root / name / "evals" / "evals.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text("{}", encoding="utf-8")
                (root / name / "SKILL.md").write_text("skill", encoding="utf-8")
            manifests = manifests_for_paths(
                [
                    "beta/references/guide.md",
                    "alpha/SKILL.md",
                    "alpha/templates/example.md",
                    "beta/README.md",
                    "missing/SKILL.md",
                    "../../escape/SKILL.md",
                ],
                root,
            )
            self.assertEqual(manifests, ["alpha/evals/evals.json", "beta/evals/evals.json"])
            selected = select(manifests, 5)
            self.assertEqual((selected["eligible_count"], selected["selected_count"]), (2, 2))

    def test_git_diff_includes_reference_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True
            )
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            skill = root / "alpha"
            (skill / "references").mkdir(parents=True)
            (skill / "evals").mkdir()
            (skill / "SKILL.md").write_text("skill", encoding="utf-8")
            (skill / "evals" / "evals.json").write_text("{}", encoding="utf-8")
            reference = skill / "references" / "guide.md"
            reference.write_text("before", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)
            reference.write_text("after", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "reference change"], check=True
            )
            paths = changed_paths(root, "HEAD^", "HEAD")
            self.assertEqual(paths, ["alpha/references/guide.md"])
            self.assertEqual(manifests_for_paths(paths, root), ["alpha/evals/evals.json"])

    def test_over_limit_fails_closed_without_selecting_first_five(self):
        manifests = [f"skill-{i}/evals/evals.json" for i in range(6)]
        selected = select(manifests, 5)
        self.assertEqual(selected["status"], "over_limit")
        self.assertEqual(selected["manifests"], [])
        self.assertEqual(selected["eligible_count"], 6)
        self.assertIn("No paired evals started", render_summary(selected))
        self.assertIn("exceeding the 5-skill resource cap", render_summary(selected))

    def test_empty_selection_is_explicit(self):
        selected = select([], 5)
        self.assertEqual(selected["status"], "none")
        self.assertIn("no paired evals started", render_summary(selected))

    def test_selection_evidence_freezes_expected_case_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "alpha" / "evals" / "evals.json"
            manifest.parent.mkdir(parents=True)
            case = {
                "id": "first-case",
                "prompt": "Test",
                "expected_output": "Answer",
                "assertions": ["Works"],
            }
            manifest.write_text(json.dumps({"evals": [case]}), encoding="utf-8")
            evidence = selection_evidence(select(["alpha/evals/evals.json"], 5), root)
            self.assertEqual(evidence["expected_cases"], {"alpha": ["first-case"]})
            manifest.write_text(json.dumps({"evals": [case, case]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique case IDs"):
                selection_evidence(select(["alpha/evals/evals.json"], 5), root)


if __name__ == "__main__":
    unittest.main()
