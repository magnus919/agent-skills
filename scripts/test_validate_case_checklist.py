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

    def test_regenerator_accepts_nested_skill_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)

            added, errors = regenerator.add_pending_case(
                checklist, root, "bundle/skills/child/manual-case"
            )

            self.assertEqual(errors, [])
            self.assertEqual(added, 1)
            row = json.loads(checklist.read_text())["rows"][0]
            self.assertEqual(row["skill"], "bundle/skills/child")
            self.assertEqual(row["case_id"], "manual-case")

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
        self.assertTrue(
            validator.build_inventory()["independent_adjudication"]["source_pins_valid"]
        )

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
                "life-coach/tests/test_validate_capabilities.py",
                "misc/test_unclassified.py",
                "scripts/check-artifacts.py",
                "terraform/tests/test_tfops.py",
                "terraform/tests/test_skipped.py",
                "terraform/tests/test_import_failing.py",
                "terraform/tests/test_helper.py",
                "terraform/tests/subpkg/__init__.py",
                "terraform/tests/subpkg/test_nested.py",
                "terraform/tests/dynamic/__init__.py",
                "terraform/tests/dynamic/test_hidden.py",
                "terraform/tests/globals_dynamic/__init__.py",
                "terraform/tests/globals_dynamic/test_hidden.py",
                "terraform/tests/null_hook/__init__.py",
                "terraform/tests/null_hook/test_visible.py",
                "terraform/tests/imported/__init__.py",
                "terraform/tests/imported/suite.py",
                "terraform/tests/imported/test_hidden.py",
                "terraform/tests/assigned/__init__.py",
                "terraform/tests/assigned/test_hidden.py",
                "terraform/tests/unsafe/__init__.py",
                "terraform/tests/unsafe/test_hidden.py",
                "terraform/tests/test_pytest_only.py",
                "terraform/tests/test-invalid.py",
                "terraform/tests/helper_test.py",
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
            workflow.write_text(
                "run: python misc/test_workflow.py\n"
                "run: python3 -m unittest discover -s life-coach/tests -p 'test_*.py'\n"
                "run: python3 scripts/check-artifacts.py\n"
            )

            (root / "terraform/tests/test_tfops.py").write_text(
                "from unittest import TestCase as BaseCase\n\n"
                "class BaseTests(BaseCase):\n    pass\n\n"
                "class TerraformCliTests(BaseTests):\n"
                "    def test_mutation_guard(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/test_skipped.py").write_text(
                "import unittest\n\n"
                "@unittest.skip('fixture skip')\n"
                "class SkippedTests(unittest.TestCase):\n"
                "    def test_skipped(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/test_import_failing.py").write_text(
                "import missing_fixture_dependency\n"
                "import unittest\n\n"
                "class ImportFailingTests(unittest.TestCase):\n"
                "    def test_import_failure(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/test_helper.py").write_text(
                "def make_fixture():\n    return None\n"
            )
            (root / "terraform/tests/subpkg/test_nested.py").write_text(
                "import unittest\n\n"
                "class NestedTests(unittest.TestCase):\n"
                "    def test_nested(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/dynamic/__init__.py").write_text(
                "def load_tests(loader, standard_tests, pattern):\n    return standard_tests\n"
            )
            (root / "terraform/tests/dynamic/test_hidden.py").write_text(
                "import unittest\n\n"
                "class HiddenTests(unittest.TestCase):\n"
                "    def test_hidden(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/globals_dynamic/__init__.py").write_text(
                "globals()['load_tests'] = lambda loader, tests, pattern: tests\n"
            )
            (root / "terraform/tests/globals_dynamic/test_hidden.py").write_text(
                "import unittest\n\n"
                "class GlobalsHookTests(unittest.TestCase):\n"
                "    def test_hidden(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/null_hook/__init__.py").write_text("load_tests = None\n")
            (root / "terraform/tests/null_hook/test_visible.py").write_text(
                "import unittest\n\n"
                "class NullHookTests(unittest.TestCase):\n"
                "    def test_visible(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/imported/__init__.py").write_text(
                "from .suite import load_tests\n"
            )
            (root / "terraform/tests/imported/suite.py").write_text(
                "def load_tests(loader, standard_tests, pattern):\n    return standard_tests\n"
            )
            (root / "terraform/tests/imported/test_hidden.py").write_text(
                "import unittest\n\n"
                "class ImportedHookTests(unittest.TestCase):\n"
                "    def test_hidden(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/assigned/__init__.py").write_text(
                "load_tests = lambda loader, tests, pattern: tests\n"
            )
            (root / "terraform/tests/assigned/test_hidden.py").write_text(
                "import unittest\n\n"
                "class AssignedHookTests(unittest.TestCase):\n"
                "    def test_hidden(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/unsafe/__init__.py").write_text(
                "exec('load_tests = lambda loader, tests, pattern: tests')\n"
            )
            (root / "terraform/tests/unsafe/test_hidden.py").write_text(
                "import unittest\n\n"
                "class DynamicHookTests(unittest.TestCase):\n"
                "    def test_hidden(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/test_pytest_only.py").write_text(
                "def test_pytest_function_only():\n    pass\n"
            )
            (root / "terraform/tests/test-invalid.py").write_text(
                "import unittest\n\n"
                "class InvalidModuleNameTests(unittest.TestCase):\n"
                "    def test_invalid_name(self):\n"
                "        pass\n"
            )
            (root / "terraform/tests/helper_test.py").write_text(
                "import unittest\n\n"
                "class SuffixStyleTests(unittest.TestCase):\n"
                "    def test_suffix_style(self):\n"
                "        pass\n"
            )
            (root / "life-coach/tests/test_validate_capabilities.py").write_text(
                "import unittest\n\n"
                "class LifeCoachTests(unittest.TestCase):\n"
                "    def test_capability(self):\n"
                "        pass\n"
            )

            report = validator.test_routing_inventory(root)

        self.assertEqual(report["test_source_count"], 22)
        self.assertEqual(
            report["routed_counts"],
            {
                "core_manifest": 1,
                "skill_local_python_autodiscovery": 1,
                "registered_skill_shell_run": 1,
                "registered_skill_shell_manual": 1,
                "integration_suite": 1,
                "workflow_explicit_path": 1,
                "workflow_directory_discovery": 1,
                "workflow_artifact_checker_unittest_discovery": 5,
            },
        )
        self.assertEqual(
            report["workflow_artifact_checker_unittest_paths"],
            [
                "terraform/tests/null_hook/test_visible.py",
                "terraform/tests/subpkg/test_nested.py",
                "terraform/tests/test_import_failing.py",
                "terraform/tests/test_skipped.py",
                "terraform/tests/test_tfops.py",
            ],
        )
        self.assertEqual(
            report["workflow_artifact_checker_overlap_paths"],
            ["life-coach/tests/test_validate_capabilities.py"],
        )
        self.assertEqual(
            report["workflow_artifact_checker_all_selected_paths"],
            [
                "life-coach/tests/test_validate_capabilities.py",
                "terraform/tests/null_hook/test_visible.py",
                "terraform/tests/subpkg/test_nested.py",
                "terraform/tests/test_import_failing.py",
                "terraform/tests/test_skipped.py",
                "terraform/tests/test_tfops.py",
            ],
        )
        self.assertEqual(
            report["unclassified_paths"],
            [
                "misc/test_unclassified.py",
                "terraform/tests/assigned/test_hidden.py",
                "terraform/tests/dynamic/test_hidden.py",
                "terraform/tests/globals_dynamic/test_hidden.py",
                "terraform/tests/helper_test.py",
                "terraform/tests/imported/test_hidden.py",
                "terraform/tests/test-invalid.py",
                "terraform/tests/test_helper.py",
                "terraform/tests/test_pytest_only.py",
                "terraform/tests/unsafe/test_hidden.py",
            ],
        )
        self.assertEqual(report["execution_status"], "not_assessed")
        self.assertIn("does not establish import success", report["interpretation"])

    def test_artifact_checker_route_requires_workflow_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            test_file = root / "terraform/tests/test_tfops.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                "import unittest\n\n"
                "class TerraformCliTests(unittest.TestCase):\n"
                "    def test_mutation_guard(self):\n"
                "        pass\n"
            )
            (root / "scripts").mkdir()
            (root / "scripts/check-artifacts.py").write_text("# checker fixture\n")
            workflow = root / ".github/workflows/validate.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: validate\n")

            report = validator.test_routing_inventory(root)
            workflow.write_text("run: python3 scripts/check-artifacts.py --self-check\n")
            self_check_report = validator.test_routing_inventory(root)

        self.assertEqual(
            report["routed_counts"]["workflow_artifact_checker_unittest_discovery"],
            0,
        )
        self.assertEqual(report["unclassified_paths"], ["terraform/tests/test_tfops.py"])
        self.assertEqual(
            self_check_report["routed_counts"]["workflow_artifact_checker_unittest_discovery"],
            0,
        )

    def test_invalid_adjudication_companion_hash_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            companion = root / "docs/fair-skill-evaluation-adjudication-run-38021806973-v1.json"
            companion.parent.mkdir(parents=True)
            companion.write_text(json.dumps({"integrity": {"sha256": "wrong"}}))

            errors = validator.validate(checklist, root)

        self.assertTrue(any("integrity hash" in error for error in errors))

    def test_adjudication_companion_source_pins_are_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checklist = self._fixture(root)
            dossier = root / "docs/fair-skill-evaluation-qualification-v1.json"
            contract = root / "eval_runner/fair-pilot-evidence-contracts-v2.json"
            dossier.parent.mkdir(parents=True)
            contract.parent.mkdir(parents=True)
            dossier.write_bytes(b"frozen dossier")
            contract.write_bytes(b"frozen evidence contract")
            record = {
                "review_basis": {
                    "dossier_sha256": hashlib.sha256(dossier.read_bytes()).hexdigest(),
                    "evidence_contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(),
                },
                "integrity": {},
            }

            def write_companion() -> None:
                canonical = json.dumps(
                    record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                )
                record["integrity"]["sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
                companion = root / "docs/fair-skill-evaluation-adjudication-run-38021806973-v1.json"
                companion.write_text(json.dumps(record))

            write_companion()
            self.assertEqual(validator.validate(checklist, root), [])

            for source, original in (
                (dossier, b"frozen dossier"),
                (contract, b"frozen evidence contract"),
            ):
                with self.subTest(source=source.name):
                    source.write_bytes(original + b" changed")
                    write_companion()
                    errors = validator.validate(checklist, root)
                    self.assertTrue(
                        any(source.relative_to(root).as_posix() in error for error in errors)
                    )
                    source.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
