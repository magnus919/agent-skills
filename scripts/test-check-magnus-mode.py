#!/usr/bin/env python3
"""Test the Magnus Mode CI entry point on synthetic catalog changes."""

import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

mode = importlib.import_module("check-magnus-mode")
SCRIPT = Path(__file__).with_name("check-magnus-mode.py").resolve()


class MagnusModeTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for file in (mode.SCOPE, mode.SOURCE, mode.REFERENCE):
            (self.root / file).parent.mkdir(parents=True, exist_ok=True)
        self.skill("magnus-mode")
        self.skill("builder")
        self.scope("magnus-mode", "router")
        self.scope("builder", "route")
        self.step = {
            "id": "build",
            "title": "Build",
            "applies": "For a build.",
            "evidence": "Inspect the candidate.",
            "after": [],
            "owner": "builder",
            "support": [],
        }
        self.routes()

    def skill(self, name: str, description: str = "Build a test fixture.") -> None:
        directory = self.root / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n")

    def scope(self, name: str, scope: str) -> None:
        path = self.root / mode.SCOPE
        current = json.loads(path.read_text()) if path.exists() else {}
        current[name] = {
            "scope": scope,
            "description_sha256": mode.description_id(self.root, name),
        }
        path.write_text(json.dumps(current))

    def routes(self) -> None:
        (self.root / mode.SOURCE).write_text(json.dumps({"Build": [self.step]}))

    def check(self, *args: str, error: str | None = None) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertEqual(result.returncode, 1 if error else 0, result.stderr)
        if error:
            self.assertIn(error, result.stderr)

    def test_new_skill_requires_classification(self) -> None:
        self.skill("planner")
        self.check(error="Catalog scope: missing ['planner']")

    def test_classified_relevant_skill_requires_route(self) -> None:
        self.skill("planner")
        self.scope("planner", "route")
        self.check(error="Lifecycle route coverage: missing ['planner']")

    def test_unrelated_addition_leaves_runtime_map_unchanged(self) -> None:
        self.check("--write")
        self.skill("shopping")
        self.scope("shopping", "unrelated")
        self.check()

    def test_removed_skill_requires_reconciliation(self) -> None:
        (self.root / "builder/SKILL.md").unlink()
        self.check(error="extra ['builder']")

    def test_unrelated_route_and_recursive_entry_fail(self) -> None:
        self.step["support"] = ["magnus-mode"]
        self.routes()
        self.check(error="extra ['magnus-mode']")

    def test_changed_trigger_requires_explicit_review(self) -> None:
        self.skill("builder", "Plan before building.")
        self.check("--write", error="Scope review required")

    def test_nested_helper_is_not_public(self) -> None:
        self.skill("builder/skills/internal-helper")
        self.check("--write")
        self.check()

    def test_cycle_is_rejected(self) -> None:
        self.step["after"] = ["build"]
        self.routes()
        self.check(error="cycle")

    def test_stale_target_after_rename(self) -> None:
        (self.root / "builder").rename(self.root / "builder-new")
        path = self.root / mode.SCOPE
        scope = json.loads(path.read_text())
        del scope["builder"]
        path.write_text(json.dumps(scope))
        self.scope("builder-new", "route")
        self.check(error="missing ['builder-new'], extra ['builder']")

    def test_validate_checkout_without_writing(self) -> None:
        self.assertEqual(mode.run(SCRIPT.parents[1], False, None), 0)

    def test_stale_projection_fails_after_map_edit(self) -> None:
        self.check("--write")
        self.step["evidence"] = "Inspect the deployed revision."
        self.routes()
        self.check(error="Stale")
        self.check("--write")
        self.check()


if __name__ == "__main__":
    unittest.main()
