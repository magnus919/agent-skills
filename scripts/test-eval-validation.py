#!/usr/bin/env python3
"""Focused tests for the repository-owned eval manifest v1 contract."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from eval_validation import NOT_APPLICABLE, SCHEMA_VERSION, find_skill_manifests, validate_manifest


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def eval_case(**updates: object) -> dict[str, object]:
    case: dict[str, object] = {
        "id": "case-1",
        "prompt": "Do the task.",
        "expected_output": "A verified result.",
        "assertions": ["Includes verification."],
    }
    case.update(updates)
    return case


class EvalValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "Test")
        self.skill = self.root / "example"
        (self.skill / "evals").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: example\ndescription: test\n---\n", encoding="utf-8")
        self.manifest = self.skill / "evals" / "evals.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def valid(self, **updates: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "skill_name": "example",
            "evals": [eval_case()],
        }
        payload.update(updates)
        return payload

    def write(self, data: object, *, track_all: bool = True) -> None:
        self.manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        if track_all:
            git(self.root, "add", "-A")

    def errors(self, data: object) -> list[str]:
        self.write(data)
        return validate_manifest(self.manifest, self.root).errors

    def test_valid_manifest_passes(self) -> None:
        self.write(self.valid())
        result = validate_manifest(self.manifest, self.root)
        self.assertTrue(result.states["manifest_present"])
        self.assertTrue(result.states["schema_valid"])
        self.assertEqual("not_assessed", result.states["executable_grader_bindings_present"])
        self.assertEqual("not_assessed", result.states["recent_run_evidence_present"])
        self.assertEqual("not_assessed", result.states["release_gated_evidence_present"])
        self.assertEqual([], result.errors)

    def test_missing_manifest_reports_schema_valid_not_applicable(self) -> None:
        missing_manifest = self.skill / "evals" / "missing.json"
        result = validate_manifest(missing_manifest, self.root)
        self.assertFalse(result.states["manifest_present"])
        self.assertEqual(NOT_APPLICABLE, result.states["schema_valid"])
        self.assertEqual([], result.errors)

    def test_targeted_schema_version_errors(self) -> None:
        missing_errors = self.errors({"skill_name": "example", "evals": [eval_case()]})
        self.assertTrue(any("missing required schema_version" in error for error in missing_errors))

        string_errors = self.errors(self.valid(schema_version="1"))
        self.assertTrue(any("must be integer 1, not a string" in error for error in string_errors))

        unknown_errors = self.errors(self.valid(schema_version=2))
        self.assertTrue(any("unsupported schema_version" in error for error in unknown_errors))

    def test_boolean_and_non_integer_schema_version_errors(self) -> None:
        bool_errors = self.errors(self.valid(schema_version=True))
        self.assertTrue(any("schema_version must be integer 1" in error for error in bool_errors))

        float_errors = self.errors(self.valid(schema_version=1.5))
        self.assertTrue(any("schema_version must be integer 1" in error for error in float_errors))

    def test_expectations_alias_errors(self) -> None:
        legacy_only = eval_case()
        legacy_only.pop("assertions")
        legacy_only["expectations"] = ["legacy"]
        errors = self.errors(self.valid(evals=[legacy_only]))
        self.assertTrue(any("expectations is not supported" in error for error in errors))

        both = eval_case(expectations=["legacy"])
        errors = self.errors(self.valid(evals=[both]))
        self.assertTrue(any("cannot both be present" in error for error in errors))

    def test_missing_required_fields_fail(self) -> None:
        for field in ("id", "prompt", "expected_output", "assertions"):
            with self.subTest(field=field):
                case = eval_case()
                case.pop(field)
                errors = self.errors(self.valid(evals=[case]))
                self.assertTrue(any(field in error for error in errors))

    def test_whitespace_prompt_and_expected_output_fail(self) -> None:
        errors = self.errors(self.valid(evals=[eval_case(prompt="   ")]))
        self.assertTrue(any("prompt" in error for error in errors))
        errors = self.errors(self.valid(evals=[eval_case(expected_output="\t")]))
        self.assertTrue(any("expected_output" in error for error in errors))

    def test_invalid_ids_fail(self) -> None:
        invalid_values: list[object] = [123, "", "UPPER", "has spaces", "path/slash", "a" * 65]
        for bad in invalid_values:
            with self.subTest(bad=bad):
                errors = self.errors(self.valid(evals=[eval_case(id=bad)]))
                self.assertTrue(any("id" in error for error in errors))

    def test_duplicate_ids_fail(self) -> None:
        errors = self.errors(self.valid(evals=[eval_case(id="dup"), eval_case(id="dup")]))
        self.assertTrue(any("duplicate case ID" in error for error in errors))

    def test_duplicate_assertions_fail(self) -> None:
        errors = self.errors(self.valid(evals=[eval_case(assertions=["A", "A"])]))
        self.assertTrue(any("duplicate assertion" in error for error in errors))

    def test_empty_evals_fail(self) -> None:
        errors = self.errors(self.valid(evals=[]))
        self.assertTrue(any("evals" in error and "non-empty" in error.lower() for error in errors))

    def test_empty_and_whitespace_only_assertions_fail(self) -> None:
        for assertion in ("", "   "):
            with self.subTest(assertion=repr(assertion)):
                errors = self.errors(self.valid(evals=[eval_case(assertions=[assertion])]))
                self.assertTrue(any("nonempty non-whitespace" in error for error in errors))

    def test_unknown_top_level_and_case_fields_fail(self) -> None:
        top_level_errors = self.errors(self.valid(unknown_field=True))
        self.assertTrue(
            any("Additional properties" in error and "unknown_field" in error for error in top_level_errors)
        )

        case_errors = self.errors(self.valid(evals=[eval_case(unknown_field=True)]))
        self.assertTrue(
            any("Additional properties" in error and "unknown_field" in error for error in case_errors)
        )

    def test_evidence_property_is_rejected_as_unknown_v1_property(self) -> None:
        errors = self.errors(self.valid(evidence={"grader_bindings": ["scripts/grader.py"]}))
        self.assertTrue(any("Additional properties" in error and "evidence" in error for error in errors))

    def test_duplicate_json_object_keys_fail_before_semantic_validation(self) -> None:
        self.manifest.write_text(
            """
{
  "schema_version": 1,
  "schema_version": 2,
  "skill_name": "example",
  "evals": [{
    "id": "case-1",
    "prompt": "P",
    "expected_output": "E",
    "assertions": ["A"]
  }]
}
""".strip()
            + "\n",
            encoding="utf-8",
        )
        git(self.root, "add", "-A")
        result = validate_manifest(self.manifest, self.root)
        self.assertFalse(result.states["schema_valid"])
        self.assertEqual(1, len(result.errors))
        self.assertIn("duplicate JSON object key", result.errors[0])

    def test_malformed_json_manifest_is_present_but_schema_invalid(self) -> None:
        self.manifest.write_text("{\n", encoding="utf-8")
        git(self.root, "add", "-A")
        result = validate_manifest(self.manifest, self.root)
        self.assertTrue(result.states["manifest_present"])
        self.assertFalse(result.states["schema_valid"])
        self.assertTrue(any("invalid JSON" in error for error in result.errors))

    def test_skill_name_must_match_containing_directory(self) -> None:
        errors = self.errors(self.valid(skill_name="wrong"))
        self.assertTrue(any("containing skill directory" in error for error in errors))

    def test_files_accepts_tracked_regular_file(self) -> None:
        fixture = self.skill / "fixtures" / "input.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text("{}\n", encoding="utf-8")
        self.write(self.valid(evals=[eval_case(files=["fixtures/input.json"])]))
        result = validate_manifest(self.manifest, self.root)
        self.assertTrue(result.states["schema_valid"])

    def test_data_dot_dot_filename_is_allowed(self) -> None:
        fixture = self.skill / "fixtures" / "data..json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text("{}\n", encoding="utf-8")
        self.write(self.valid(evals=[eval_case(files=["fixtures/data..json"])]))
        result = validate_manifest(self.manifest, self.root)
        self.assertTrue(result.states["schema_valid"])

    def test_duplicate_file_paths_fail(self) -> None:
        fixture = self.skill / "fixtures" / "input.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text("{}\n", encoding="utf-8")
        errors = self.errors(
            self.valid(evals=[eval_case(files=["fixtures/input.json", "fixtures/input.json"])]),
        )
        self.assertTrue(any("non-unique elements" in error for error in errors))

    def test_lexical_dot_empty_and_trailing_slash_paths_fail(self) -> None:
        fixture = self.skill / "fixtures" / "input.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text("{}\n", encoding="utf-8")

        for bad in (
            "fixtures/./input.json",
            "fixtures//input.json",
            "./input.json",
            "fixtures/input.json/",
        ):
            with self.subTest(path=bad):
                errors = self.errors(self.valid(evals=[eval_case(files=[bad])]))
                self.assertTrue(any("files[0]" in error for error in errors))

    def test_symlink_component_escaping_skill_is_rejected(self) -> None:
        external_dir = self.root / "external"
        external_dir.mkdir(parents=True, exist_ok=True)
        (external_dir / "outside.json").write_text("{}\n", encoding="utf-8")

        fixtures_dir = self.skill / "fixtures"
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        os.symlink(external_dir, fixtures_dir / "external")
        git(self.root, "add", "-A")

        errors = self.errors(self.valid(evals=[eval_case(files=["fixtures/external/outside.json"])]))
        self.assertTrue(any("symlink" in error for error in errors))

    def test_tracked_but_missing_file_fails_when_index_still_lists_it(self) -> None:
        fixture = self.skill / "fixtures" / "input.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text("{}\n", encoding="utf-8")
        self.write(self.valid(evals=[eval_case(files=["fixtures/input.json"])]))

        fixture.unlink()
        tracked_entry = git_output(
            self.root,
            "ls-files",
            "-s",
            "--",
            str(fixture.relative_to(self.root)),
        )
        self.assertNotEqual("", tracked_entry)

        errors = validate_manifest(self.manifest, self.root).errors
        self.assertTrue(any("does not exist in working tree" in error for error in errors))

    def test_nested_bundle_skill_name_matches_leaf_directory(self) -> None:
        nested_skill = self.root / "bundles" / "demo-bundle" / "skills" / "child-skill"
        (nested_skill / "evals").mkdir(parents=True)
        (nested_skill / "SKILL.md").write_text(
            "---\nname: child-skill\ndescription: test\n---\n",
            encoding="utf-8",
        )
        nested_manifest = nested_skill / "evals" / "evals.json"
        nested_manifest.write_text(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "skill_name": "child-skill",
                    "evals": [eval_case()],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        git(self.root, "add", "-A")

        result = validate_manifest(nested_manifest, self.root)
        self.assertTrue(result.states["schema_valid"])

    def test_file_boundary_failures(self) -> None:
        tracked = self.skill / "Fixtures" / "Input.json"
        tracked.parent.mkdir(parents=True, exist_ok=True)
        tracked.write_text("{}\n", encoding="utf-8")
        outside = self.root / "outside.json"
        outside.write_text("{}\n", encoding="utf-8")
        directory = self.skill / "fixtures"
        directory.mkdir(parents=True, exist_ok=True)
        symlink_target = directory / "target.json"
        symlink_target.write_text("{}\n", encoding="utf-8")
        os.symlink(symlink_target, directory / "linked.json")
        git(self.root, "add", "-A")

        invalid_paths = [
            str(tracked.resolve()),
            "../outside.json",
            "fixtures/missing.json",
            "fixtures",
            "fixtures\\bad.json",
            "fixtures/linked.json",
            "fixtures/\u0001bad.json",
            "fixtures/./input.json",
            "Fixtures/input.json",
        ]
        for bad in invalid_paths:
            with self.subTest(path=bad):
                errors = self.errors(self.valid(evals=[eval_case(files=[bad])]))
                self.assertTrue(any("files[0]" in error for error in errors))

    def test_missing_and_untracked_fixture_paths_report_distinct_reasons(self) -> None:
        untracked = self.skill / "fixtures" / "untracked.json"
        untracked.parent.mkdir(parents=True, exist_ok=True)
        untracked.write_text("{}\n", encoding="utf-8")

        self.write(self.valid(evals=[eval_case(files=["fixtures/missing.json"])]), track_all=False)
        git(self.root, "add", str(self.manifest.relative_to(self.root)))
        missing_errors = validate_manifest(self.manifest, self.root).errors
        self.assertTrue(any("does not exist" in error for error in missing_errors))
        self.assertFalse(any("not tracked by Git" in error for error in missing_errors))

        self.write(self.valid(evals=[eval_case(files=["fixtures/untracked.json"])]), track_all=False)
        git(self.root, "add", str(self.manifest.relative_to(self.root)))
        tracked_untracked = git_output(
            self.root,
            "ls-files",
            "--",
            str(untracked.relative_to(self.root)),
        )
        self.assertEqual("", tracked_untracked)
        untracked_errors = validate_manifest(self.manifest, self.root).errors
        self.assertTrue(any("not tracked by Git" in error for error in untracked_errors))
        self.assertFalse(any("does not exist" in error for error in untracked_errors))


class RepositoryManifestTest(unittest.TestCase):
    def test_known_migrated_set_is_present_and_all_discovered_manifests_validate(self) -> None:
        known = {
            "de-spin/evals/evals.json",
            "esp32-development/evals/evals.json",
            "raleigh/evals/evals.json",
            "restic/evals/evals.json",
            "supabase/evals/evals.json",
            "vercel-eve/evals/evals.json",
            "verification-methodology/evals/evals.json",
        }
        manifests = find_skill_manifests(ROOT)
        discovered = {str(path.relative_to(ROOT)) for path in manifests}
        self.assertTrue(known.issubset(discovered))

        invalid = []
        for manifest in manifests:
            result = validate_manifest(manifest, ROOT)
            if result.states["schema_valid"] is not True:
                invalid.append((manifest, result.errors))
        self.assertEqual([], invalid)


if __name__ == "__main__":
    unittest.main()
