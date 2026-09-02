#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "validator", Path(__file__).parent / "validate-case-checklist.py"
)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ChecklistValidatorTest(unittest.TestCase):
    def test_current_checklist_matches_manifests(self) -> None:
        self.assertEqual(validator.validate(), [])

    def test_missing_orphan_and_duplicate_rows_fail(self) -> None:
        source = json.loads(validator.CHECKLIST.read_text())
        source["rows"] = source["rows"][:-1]
        source["rows"].append({"skill": "not-a-skill", "case_id": "orphan"})
        source["rows"].append(source["rows"][0])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checklist.json"
            path.write_text(json.dumps(source))
            errors = validator.validate(path)
        self.assertTrue(any("missing checklist rows" in error for error in errors))
        self.assertTrue(any("orphan checklist rows" in error for error in errors))
        self.assertTrue(any("duplicate checklist rows" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
