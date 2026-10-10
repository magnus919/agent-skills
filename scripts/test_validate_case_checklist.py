import hashlib
import importlib.util
import json
import tempfile
import types
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parent


def load_script(name: str, module_name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / name)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_script("validate-case-checklist.py", "case_checklist_validator")
regenerator = load_script("regenerate-case-checklist.py", "case_checklist_regenerator")


class ChecklistEvidenceTest(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        for skill in ("sample", "bundle/skills/child"):
            skill_root = root / skill
            (skill_root / "evals").mkdir(parents=True)
            (skill_root / "SKILL.md").write_text("---\nname: sample\n---\n")
        (root / "sample/evals/evals.json").write_text(
            json.dumps(
                {
                    "evals": [
                        {
                            "id": "exact-case",
                            "prompt": "check an exact property",
                            "assertions": ["exit_status:completed"],
                        }
                    ]
                }
            )
        )
        (root / "bundle/skills/child/evals/evals.json").write_text(
            json.dumps(
                {
                    "evals": [
                        {
                            "id": "manual-case",
                            "prompt": "review a behavior",
                            "assertions": ["Preserves authorization at execution time"],
                        }
                    ]
                }
            )
        )
        checklist = root / "checklist.json"
        checklist.write_text(json.dumps({"rows": []}))
        return checklist

    def test_current_checklist_is_a_valid_curated_subset(self) -> None:
        self.assertEqual(validator.validate(), [])
        report = validator.build_inventory()
        self.assertGreater(report["manifest_inventory"]["nested_manifests"], 0)
        self.assertGreater(report["case_review_records"]["cases_without_row"], 0)
        self.assertEqual(
            report["verified_behavioral_coverage"]["assessment"],
            "not_assessed_repository_wide",
        )

    def test_nested_manifests_are_counted_and_missing_rows_are_not_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            report = validator.build_inventory(root, checklist)
            self.assertEqual(validator.validate(checklist, root), [])
            self.assertEqual(report["manifest_inventory"]["top_level_manifests"], 1)
            self.assertEqual(report["manifest_inventory"]["nested_manifests"], 1)
            self.assertEqual(report["case_review_records"]["cases_without_row"], 2)

    def test_duplicate_and_orphan_rows_fail_without_requiring_full_case_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            row = {"skill": "sample", "case_id": "exact-case"}
            checklist.write_text(
                json.dumps(
                    {
                        "rows": [
                            row,
                            row,
                            {"skill": "missing-skill", "case_id": "orphan"},
                        ]
                    }
                )
            )
            errors = validator.validate(checklist, root)
            self.assertTrue(any("duplicate checklist rows" in error for error in errors))
            self.assertTrue(any("orphan checklist rows" in error for error in errors))
            self.assertFalse(any("missing checklist rows" in error for error in errors))

    def test_report_keeps_execution_review_and_verification_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            checklist.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "skill": "sample",
                                "case_id": "exact-case",
                                "reviewer": "reviewer-a",
                                "verdict": "reviewed",
                            }
                        ]
                    }
                )
            )
            artifact_dir = root / "lifecycle-evals/run-artifacts/manifests"
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "trial.manifest.json").write_text(
                json.dumps(
                    {
                        "status": "completed",
                        "adapter": {"name": "fake"},
                        "candidate": {"skill_path": "sample"},
                        "case": {"case_id": "exact-case"},
                    }
                )
            )
            report = validator.build_inventory(root, checklist)
            self.assertEqual(report["case_review_records"]["rows_present"], 1)
            self.assertEqual(report["execution_evidence"]["artifact_count"], 1)
            self.assertEqual(report["execution_evidence"]["adapter_counts"], {"fake": 1})
            self.assertEqual(
                report["verified_behavioral_coverage"]["assessment"],
                "not_assessed_repository_wide",
            )

    def test_regenerator_only_adds_one_explicit_pending_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            source = checklist.read_text()
            document, prompts, errors = regenerator.checklist_state(checklist, root)
            self.assertEqual(errors, [])
            self.assertEqual(len(prompts), 2)
            self.assertEqual(document["rows"], [])
            self.assertEqual(checklist.read_text(), source)

            added, errors = regenerator.add_pending_case(checklist, root, "sample/exact-case")
            self.assertEqual(errors, [])
            self.assertEqual(added, 1)
            row = json.loads(checklist.read_text())["rows"][0]
            self.assertEqual(row["capability"], "check an exact property")
            self.assertEqual(row["reviewer"], "unassigned")
            self.assertIsNone(row["reviewed_on"])
            self.assertEqual(row["verdict"], "pending")
            self.assertIsNone(row["assertions_grounded"])
            added, errors = regenerator.add_pending_case(checklist, root, "sample/exact-case")
            self.assertEqual(added, 0)
            self.assertTrue(any("already has" in error for error in errors))

    def test_independent_adjudication_companion_hash_and_summary(self) -> None:
        path = (
            Path(__file__).parents[1]
            / "docs/fair-skill-evaluation-adjudication-run-38021806973-v1.json"
        )
        record = json.loads(path.read_text())
        digest = record["integrity"].pop("sha256")
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(hashlib.sha256(canonical.encode()).hexdigest(), digest)
        self.assertEqual(len(record["cases"]), 12)
        self.assertEqual(record["summary"]["exact_label_matches"], 11)
        self.assertFalse(record["reviewer"]["human_ground_truth"])

    def test_test_routing_inventory_reads_annotated_shell_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = [
                "scripts/test_core.py",
                "sample/SKILL.md",
                "sample/scripts/test_auto.py",
                "sample/scripts/test_run.sh",
                "sample/scripts/test_manual.sh",
                "tests/integration/test_integration.py",
                "misc/test_workflow.py",
                "misc/test_unclassified.py",
            ]
            for relative in files:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# fixture\n")
            (root / "scripts/core-test-files.txt").write_text("scripts/test_core.py\n")
            (root / "scripts/check-skill-tests.py").write_text(
                "RUN_TESTS: list[tuple[str, list[str]]] = "
                '[("sample/scripts/test_run.sh", [])]\n'
                'MANUAL_TESTS: list[str] = ["sample/scripts/test_manual.sh"]\n'
            )
            workflow = root / ".github/workflows/validate.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("run: python misc/test_workflow.py\n")

            report = validator.test_routing_inventory(root)

        self.assertEqual(report["test_source_count"], 7)
        self.assertEqual(
            report["routed_counts"],
            {
                "core_manifest": 1,
                "skill_local_python_autodiscovery": 1,
                "registered_skill_shell_run": 1,
                "registered_skill_shell_manual": 1,
                "integration_suite": 1,
                "workflow_explicit_path": 1,
            },
        )
        self.assertEqual(report["unclassified_paths"], ["misc/test_unclassified.py"])

    def test_invalid_adjudication_companion_hash_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            companion = root / "docs/fair-skill-evaluation-adjudication-run-38021806973-v1.json"
            companion.parent.mkdir(parents=True)
            companion.write_text(json.dumps({"integrity": {"sha256": "wrong"}}))

            errors = validator.validate(checklist, root)

        self.assertTrue(any("integrity hash" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
