#!/usr/bin/env python3
"""Tests for the read-only community guide plan checker."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import validate_guide

SCRIPT = Path(__file__).with_name("validate_guide.py")


class ValidateGuideTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "worksheets").mkdir()
        (self.root / "worksheets" / "intro.md").write_text("intro", encoding="utf-8")
        (self.root / "participant.md").write_text("participant", encoding="utf-8")
        (self.root / "facilitator.md").write_text("facilitator", encoding="utf-8")
        self.plan_path = self.root / "plan.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def plan(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "title": "A useful guide",
            "modules": [
                {
                    "id": "intro",
                    "title": "Introduction",
                    "duration_minutes": 30,
                    "activities": [{"title": "Discuss", "minutes": 20}],
                    "worksheet_ids": ["welcome"],
                }
            ],
            "worksheets": [{"id": "welcome", "path": "worksheets/intro.md"}],
            "materials": {"participant": "participant.md", "facilitator": "facilitator.md"},
            "maintenance": {
                "owner": "Community team",
                "status": "confirmed",
                "review_date": "2026-10-01",
            },
            "sources": [
                {
                    "id": "source-1",
                    "locator": "https://example.test/source",
                    "checked_on": "2026-09-01",
                    "status": "verified",
                }
            ],
        }

    def write_plan(self, plan: object) -> None:
        self.plan_path.write_text(json.dumps(plan), encoding="utf-8")

    def run_cli(self, path: Path | str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_plan_and_non_readiness_warnings(self) -> None:
        plan = self.plan()
        plan["maintenance"] = {  # type: ignore[index]
            "owner": "Community team",
            "status": "proposed",
            "review_date": "2026-10-01",
        }
        plan["sources"] = [  # type: ignore[index]
            {
                "id": "source-1",
                "locator": "provided by the author",
                "checked_on": "2026-09-01",
                "status": "unresolved",
            }
        ]
        self.write_plan(plan)

        result = validate_guide.validate_file(self.plan_path)

        self.assertEqual(result[1], 0)
        self.assertTrue(result[0]["valid"])
        self.assertEqual(len(result[0]["errors"]), 0)
        self.assertEqual(len(result[0]["warnings"]), 2)

    def test_required_fields_types_dates_and_duplicates(self) -> None:
        plan = self.plan()
        plan["schema_version"] = True  # type: ignore[index]
        plan["title"] = "   "  # type: ignore[index]
        plan["modules"] = [  # type: ignore[index]
            {
                "id": "same",
                "title": "One",
                "duration_minutes": 0,
                "activities": [{"title": "", "minutes": False}],
                "worksheet_ids": [3],
            },
            {
                "id": "same",
                "title": "Two",
                "duration_minutes": 10,
                "activities": [],
                "worksheet_ids": [],
            },
        ]
        plan["worksheets"] = [  # type: ignore[index]
            {"id": "welcome", "path": "worksheets/intro.md"},
            {"id": "welcome", "path": "worksheets/intro.md"},
        ]
        plan["maintenance"] = {  # type: ignore[index]
            "owner": "owner",
            "status": [],
            "review_date": "2026-02-30",
        }
        plan["sources"][0]["status"] = []  # type: ignore[index]
        self.write_plan(plan)

        result, exit_code = validate_guide.validate_file(self.plan_path)

        self.assertEqual(exit_code, 1)
        self.assertFalse(result["valid"])
        joined = "\n".join(result["errors"])
        self.assertIn("schema_version: must be the integer 1", joined)
        self.assertIn("title: must be a nonblank string", joined)
        self.assertIn("duplicate module id", joined)
        self.assertIn("duplicate worksheet id", joined)
        self.assertIn("positive integer", joined)
        self.assertIn("must contain at least one activity", joined)
        self.assertIn("valid calendar date", joined)

    def test_timing_and_unresolved_worksheet_reference(self) -> None:
        plan = self.plan()
        plan["modules"][0]["duration_minutes"] = 10  # type: ignore[index]
        plan["modules"][0]["worksheet_ids"] = ["missing"]  # type: ignore[index]
        self.write_plan(plan)

        result, exit_code = validate_guide.validate_file(self.plan_path)

        self.assertEqual(exit_code, 1)
        self.assertIn("exceeds duration_minutes", "\n".join(result["errors"]))
        self.assertIn("does not resolve", "\n".join(result["errors"]))

    def test_relative_file_refs_missing_and_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as external_dir:
            outside = Path(external_dir) / "outside-material.md"
            outside.write_text("outside", encoding="utf-8")
            plan = self.plan()
            plan["materials"]["participant"] = os.path.relpath(  # type: ignore[index]
                outside, self.plan_path.parent
            )
            plan["worksheets"][0]["path"] = "missing.md"  # type: ignore[index]
            self.write_plan(plan)

            result, exit_code = validate_guide.validate_file(self.plan_path)

            self.assertEqual(exit_code, 1)
            joined = "\n".join(result["errors"])
            self.assertIn("'..' path components are not allowed", joined)
            self.assertIn("referenced file does not exist", joined)

    def test_parent_components_inside_base_and_backslashes_are_rejected(self) -> None:
        plan = self.plan()
        plan["materials"]["participant"] = "nested/../participant.md"  # type: ignore[index]
        self.write_plan(plan)

        result, exit_code = validate_guide.validate_file(self.plan_path)

        self.assertEqual(exit_code, 1)
        self.assertIn("'..' path components are not allowed", "\n".join(result["errors"]))

        plan = self.plan()
        plan["materials"]["facilitator"] = "facilitator\\.md"  # type: ignore[index]
        self.write_plan(plan)

        result, exit_code = validate_guide.validate_file(self.plan_path)

        self.assertEqual(exit_code, 1)
        self.assertIn("backslashes are not allowed", "\n".join(result["errors"]))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as external_dir:
            external = Path(external_dir) / "external-guide-material.md"
            external.write_text("external", encoding="utf-8")
            link = self.root / "escape.md"
            try:
                link.symlink_to(external)
                plan = self.plan()
                plan["materials"]["participant"] = "escape.md"  # type: ignore[index]
                self.write_plan(plan)

                result, exit_code = validate_guide.validate_file(self.plan_path)

                self.assertEqual(exit_code, 1)
                self.assertIn("resolves outside the plan directory", "\n".join(result["errors"]))
            finally:
                link.unlink(missing_ok=True)

    def test_cli_exit_codes_json_and_duplicate_keys(self) -> None:
        self.write_plan(self.plan())
        valid = self.run_cli(self.plan_path)
        self.assertEqual(valid.returncode, 0)
        self.assertEqual(valid.stderr, "")
        self.assertTrue(json.loads(valid.stdout)["valid"])

        invalid_path = self.root / "invalid.json"
        invalid_path.write_text("{}", encoding="utf-8")
        invalid = self.run_cli(invalid_path)
        self.assertEqual(invalid.returncode, 1)
        self.assertFalse(json.loads(invalid.stdout)["valid"])
        self.assertEqual(invalid.stderr, "")

        duplicate_path = self.root / "duplicate.json"
        duplicate_path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        duplicate = self.run_cli(duplicate_path)
        self.assertEqual(duplicate.returncode, 2)
        duplicate_result = json.loads(duplicate.stdout)
        self.assertIn("duplicate JSON key", duplicate_result["errors"][0])
        self.assertEqual(duplicate.stderr, "")

        missing = self.run_cli(self.root / "does-not-exist.json")
        self.assertEqual(missing.returncode, 2)
        self.assertIn("cannot read plan", json.loads(missing.stdout)["errors"][0])

        malformed = self.root / "malformed.json"
        malformed.write_text("{", encoding="utf-8")
        malformed_result = self.run_cli(malformed)
        self.assertEqual(malformed_result.returncode, 2)
        self.assertIn("invalid JSON", json.loads(malformed_result.stdout)["errors"][0])

    def test_no_argument_is_json_input_failure(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        self.assertIn("exactly one", json.loads(result.stdout)["errors"][0])

    def test_help_is_concise_and_succeeds(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("Usage: python3 scripts/validate_guide.py PATH_TO_PLAN_JSON", result.stdout)
        self.assertIn("Exit codes: 0 valid, 1 invalid plan, 2 input failure.", result.stdout)


if __name__ == "__main__":
    unittest.main()
