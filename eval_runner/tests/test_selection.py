"""Paired-eval selection must never present a truncated subset as complete."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from eval_runner.selection import manifests_for_paths, render_summary, select


class SelectionTests(unittest.TestCase):
    def test_selects_changed_skills_once_and_ignores_unrelated_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("alpha", "beta"):
                manifest = root / name / "evals" / "evals.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text("{}", encoding="utf-8")
            manifests = manifests_for_paths(
                [
                    "beta/scripts/helper.py",
                    "alpha/SKILL.md",
                    "alpha/evals/evals.json",
                    "beta/README.md",
                    "missing/SKILL.md",
                    "../../escape/SKILL.md",
                ],
                root,
            )
            self.assertEqual(manifests, ["alpha/evals/evals.json", "beta/evals/evals.json"])
            selected = select(manifests, 5)
            self.assertEqual((selected["eligible_count"], selected["selected_count"]), (2, 2))

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


if __name__ == "__main__":
    unittest.main()
