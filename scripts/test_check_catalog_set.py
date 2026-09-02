#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_catalog_set", Path(__file__).parent / "check-catalog-set.py"
)
check_catalog_set = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_catalog_set)


class CatalogSetTest(unittest.TestCase):
    def test_current_catalogs_match(self):
        result = check_catalog_set.compare(Path(__file__).parent.parent)
        self.assertTrue(result["ok"], result)

    def test_missing_duplicate_extra_and_retired_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one").mkdir()
            (root / "one/SKILL.md").write_text("---\nname: one\ndescription: One\n---\n")
            (root / ".claude-plugin").mkdir()
            (root / ".codex-plugin").mkdir()
            (root / ".agents/plugins").mkdir(parents=True)
            (root / ".claude-plugin/marketplace.json").write_text(
                json.dumps({"plugins": [{"name": "one"}, {"name": "one"}, {"name": "jira-cli"}]})
            )
            (root / ".codex-plugin/plugin.json").write_text(
                json.dumps({"skills": ["./one", "./extra"]})
            )
            (root / ".agents/plugins/marketplace.json").write_text(
                json.dumps({"plugins": [{"name": "magnus919"}]})
            )
            (root / "llms.txt").write_text("- [one](one/SKILL.md): One\n")
            result = check_catalog_set.compare(root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["sources"]["claude_marketplace"]["duplicates"], ["one"])
            self.assertEqual(result["sources"]["claude_marketplace"]["retired"], ["jira-cli"])
            self.assertEqual(result["sources"]["codex_plugin"]["extra"], ["extra"])

    def test_nested_and_lifecycle_entries_are_excluded_from_canonical_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lifecycle-evals").mkdir()
            (root / "lifecycle-evals/SKILL.md").write_text(
                "---\nname: lifecycle-evals\ndescription: no\n---\n"
            )
            (root / "bundle/skills/helper").mkdir(parents=True)
            (root / "bundle/skills/helper/SKILL.md").write_text(
                "---\nname: helper\ndescription: no\n---\n"
            )
            names, excluded = check_catalog_set.canonical_names(root)
            self.assertEqual(names, [])
            self.assertIn("lifecycle-evals", excluded)
            self.assertIn("bundle/skills/helper/SKILL.md", excluded)


if __name__ == "__main__":
    unittest.main()
