"""Contract checks for the advisory Jev eval artifact reader."""

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import yaml
from jev_eval_audit import (
    _read_json,
    audit,
    build_request,
    collect_groups,
    expected_report_ids,
    question_contract_sha256,
    question_input_sha256,
    render_summary,
    selection_is_complete,
)
from jev_eval_benchmark import metrics


def sample_report(response="A bounded answer"):
    trial = {
        "assertions": [
            {"assertion": "Explains the boundary", "verdict": "manual_review"},
            {"assertion": "exit_code == 0", "verdict": "pass"},
        ],
        "manifest": {"status": "completed", "outputs": {"response": response}},
    }
    return {
        "skill_name": "system-one",
        "case_id": "test-case",
        "candidate": trial,
        "baseline": trial,
    }


class JevEvalAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.reports = self.root / "system-one" / "reports"
        self.reports.mkdir(parents=True)
        self.path = self.reports / "test-case.comparison.json"
        self.path.write_text(json.dumps(sample_report()), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_collects_only_prose_and_keeps_response_out_of_report(self):
        groups, counts = collect_groups(self.root, 24000)
        self.assertEqual(
            (len(groups), counts["prose_assertions_seen"], counts["exact_assertions_untouched"]),
            (2, 2, 2),
        )
        self.assertEqual(groups[0]["assertions"], ["Explains the boundary"])
        request = build_request(groups[0])
        self.assertEqual(request["model"], "jev-1.13.0")
        result = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
        )
        serialized = json.dumps(result)
        self.assertNotIn("A bounded answer", serialized)
        self.assertTrue(result["advisory_only"])
        self.assertEqual(result["counts"]["groups_selected"], 2)
        self.assertEqual(result["question_contract_sha256"], question_contract_sha256())
        self.assertEqual(
            result["results"][0]["question_input_sha256"], question_input_sha256(request)
        )

    def test_question_contract_fingerprint_tracks_input_rubric_not_response(self):
        baseline = question_contract_sha256()
        self.assertEqual(len(baseline), 64)
        self.assertEqual(baseline, question_contract_sha256())
        with patch.dict("jev_eval_audit.CRITERIA", {"met": "Changed criterion"}):
            self.assertNotEqual(question_contract_sha256(), baseline)
        self.assertEqual(question_contract_sha256(), baseline)

    def test_shadow_question_is_distinct_and_does_not_change_deployed_request(self):
        group = {"response": "Expected 4, observed 3.", "assertions": ["Compares counts"]}
        deployed = build_request(group)
        shadow = build_request(group, "mismatch-shadow-v1")
        procedure_shadow = build_request(group, "procedure-conflict-shadow-v2")
        coverage_shadow = build_request(group, "all-requirements-shadow-v1")
        self.assertEqual(build_request(group), deployed)
        self.assertEqual(shadow["state"], deployed["state"])
        self.assertEqual(procedure_shadow["state"], deployed["state"])
        self.assertEqual(coverage_shadow["state"], deployed["state"])
        self.assertEqual(
            shadow["questions"]["a0"]["criteria"], deployed["questions"]["a0"]["criteria"]
        )
        self.assertEqual(
            procedure_shadow["questions"]["a0"]["criteria"],
            deployed["questions"]["a0"]["criteria"],
        )
        self.assertEqual(
            coverage_shadow["questions"]["a0"]["criteria"],
            deployed["questions"]["a0"]["criteria"],
        )
        self.assertIn("Check every named item", coverage_shadow["questions"]["a0"]["instructions"])
        self.assertNotEqual(question_input_sha256(shadow), question_input_sha256(deployed))
        self.assertNotEqual(
            question_input_sha256(procedure_shadow), question_input_sha256(deployed)
        )
        self.assertNotEqual(question_input_sha256(coverage_shadow), question_input_sha256(deployed))
        self.assertNotEqual(
            question_contract_sha256("mismatch-shadow-v1"), question_contract_sha256()
        )
        self.assertNotEqual(
            question_contract_sha256("all-requirements-shadow-v1"), question_contract_sha256()
        )
        shadow_report = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            question_variant="mismatch-shadow-v1",
        )
        self.assertEqual(shadow_report["question_variant"], "mismatch-shadow-v1")
        self.assertEqual(
            shadow_report["results"][0]["question_input_sha256"],
            question_input_sha256(
                build_request(
                    {"response": "A bounded answer", "assertions": ["Explains the boundary"]},
                    "mismatch-shadow-v1",
                )
            ),
        )
        with self.assertRaisesRegex(ValueError, "unknown question variant"):
            build_request(group, "unknown")

    def test_replay_workflow_is_trusted_opt_in_and_keeps_the_deployed_audit_unchanged(self):
        repo = Path(__file__).resolve().parents[2]
        replay = yaml.load(
            (repo / ".github/workflows/jev-eval-replay.yml").read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )
        events = replay["on"]
        self.assertEqual(set(events), {"workflow_dispatch"})
        inputs = events["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["authorize_jev_egress"]["default"], "false")
        self.assertEqual(inputs["question_variant"]["type"], "choice")
        self.assertEqual(
            set(inputs["question_variant"]["options"]),
            {
                "deployed",
                "mismatch-shadow-v1",
                "procedure-conflict-shadow-v1",
                "procedure-conflict-shadow-v2",
                "all-requirements-shadow-v1",
            },
        )
        self.assertEqual(replay["permissions"], {"actions": "read", "contents": "read"})
        job = replay["jobs"]["replay"]
        self.assertEqual(job["if"], "github.ref == 'refs/heads/main'")
        steps = {step["name"]: step for step in job["steps"]}
        self.assertEqual(
            steps["Check out trusted main-branch code"]["with"]["persist-credentials"], "false"
        )
        self.assertNotIn(
            "TYPESAFE_API_KEY",
            json.dumps(steps["Verify source run and per-run egress authorization"]),
        )
        self.assertIn(
            "as untrusted data", steps["Download paired model artifact as untrusted data"]["name"]
        )
        audit_step = steps["Replay advisory Jev audit with selected question variant"]
        self.assertEqual(audit_step["env"]["TYPESAFE_API_KEY"], "${{ secrets.TYPESAFE_API_KEY }}")
        self.assertIn('--question-variant "$QUESTION_VARIANT"', audit_step["run"])
        self.assertIn("--require-complete-selection", audit_step["run"])
        deployed = yaml.load(
            (repo / ".github/workflows/skill-eval.yml").read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )
        self.assertNotIn("--question-variant", json.dumps(deployed))

    def test_question_input_fingerprint_tracks_exact_assertions_without_response_text(self):
        group = {"response": "first response", "assertions": ["Checks the outcome"]}
        first = question_input_sha256(build_request(group))
        self.assertEqual(len(first), 64)
        group["response"] = "different private response"
        self.assertEqual(question_input_sha256(build_request(group)), first)
        group["assertions"] = ["Checks an independently confirmed outcome"]
        self.assertNotEqual(question_input_sha256(build_request(group)), first)
        with patch.dict("jev_eval_audit.CRITERIA", {"met": "Changed criterion"}):
            self.assertNotEqual(
                question_input_sha256(
                    build_request({"response": "x", "assertions": ["Checks the outcome"]})
                ),
                first,
            )

    def test_rejects_symlink_and_oversized_artifact(self):
        link = self.reports / "link.comparison.json"
        link.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "symlink"):
            collect_groups(self.root, 24000)
        link.unlink()
        self.path.write_text(" " * 2_000_001, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "size limit"):
            _read_json(self.path, self.root)

    def test_rejects_identity_mismatch_and_skips_unavailable_response(self):
        report = sample_report()
        report["skill_name"] = "another-skill"
        self.path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "identity"):
            collect_groups(self.root, 24000)
        self.path.write_text(json.dumps(sample_report("x" * 30)), encoding="utf-8")
        groups, counts = collect_groups(self.root, 20)
        self.assertEqual(groups, [])
        self.assertEqual(counts["skipped_response"], 2)

    def test_complete_selection_requires_nonempty_exact_report_identity_coverage(self):
        selection = {
            "schema_version": 1,
            "status": "selected",
            "manifests": ["system-one/evals/evals.json"],
            "selected_count": 1,
            "expected_cases": {"system-one": ["test-case"]},
        }
        complete = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            selection=selection,
        )
        self.assertTrue(selection_is_complete(complete))

        selection["expected_cases"]["system-one"] = ["missing-case"]
        incomplete = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            selection=selection,
        )
        self.assertFalse(selection_is_complete(incomplete))
        unselected = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
        )
        self.assertFalse(selection_is_complete(unselected))

    def test_replay_selection_flag_fails_closed_without_changing_default_audit_exit(self):
        selection_path = self.root / "selection.json"
        selection_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "selected",
                    "manifests": ["system-one/evals/evals.json"],
                    "selected_count": 1,
                    "expected_cases": {"system-one": ["missing-case"]},
                }
            ),
            encoding="utf-8",
        )
        from jev_eval_audit import main

        base_argv = [
            "jev_eval_audit.py",
            "--reports",
            str(self.root),
            "--selection",
            str(selection_path),
        ]
        with patch("sys.argv", base_argv), redirect_stdout(StringIO()):
            self.assertEqual(main(), 0)
        with (
            patch("sys.argv", [*base_argv, "--require-complete-selection"]),
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(main(), 1)

    def test_generation_errors_are_not_mislabeled_as_untouched_exact_assertions(self):
        report = sample_report()
        for side in ("candidate", "baseline"):
            report[side]["infra_error"] = True
            report[side]["assertions"] = [
                {"assertion": "Explains the boundary", "verdict": "infra_error"},
                {"assertion": "exit_code == 0", "verdict": "infra_error"},
            ]
            report[side]["manifest"] = {"status": "error", "outputs": {}}
        self.path.write_text(json.dumps(report), encoding="utf-8")

        groups, counts = collect_groups(self.root, 24000)
        self.assertEqual(groups, [])
        self.assertEqual(counts["prose_assertions_seen"], 0)
        self.assertEqual(counts["exact_assertions_untouched"], 0)
        self.assertEqual(counts["skipped_infra_error_assertions"], 4)
        self.assertEqual(counts["generation_error_sides"], 2)

        audit_report = audit(
            self.root,
            live=True,
            key="fixture-key",
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            selection={
                "schema_version": 1,
                "status": "selected",
                "manifests": ["system-one/evals/evals.json"],
                "selected_count": 1,
                "expected_cases": {"system-one": ["test-case"]},
            },
        )
        summary = render_summary(audit_report)
        self.assertIn("Incomplete model generation", summary)
        self.assertIn("Generation-error sides: 2", summary)
        self.assertIn("Assertions skipped after generation errors: 4", summary)

    def test_budget_never_turns_omission_into_pass(self):
        result = audit(
            self.root,
            live=False,
            key=None,
            max_calls=1,
            max_assertions=1,
            max_response_chars=24000,
            timeout=12.0,
        )
        self.assertEqual(result["counts"]["groups_selected"], 0)
        self.assertEqual(result["counts"]["assertions_omitted_by_budget"], 2)
        self.assertEqual(result["results"], [])

    def test_budget_spreads_complete_pairs_across_skills_deterministically(self):
        for skill in ("alpha-skill", "beta-skill"):
            reports = self.root / skill / "reports"
            reports.mkdir(parents=True)
            for case_id in ("first-case", "second-case"):
                report = sample_report()
                report["skill_name"] = skill
                report["case_id"] = case_id
                (reports / f"{case_id}.comparison.json").write_text(
                    json.dumps(report), encoding="utf-8"
                )
        self.path.unlink()

        def run():
            return audit(
                self.root,
                live=False,
                key=None,
                max_calls=4,
                max_assertions=4,
                max_response_chars=24000,
                timeout=12.0,
            )

        result = run()
        self.assertEqual(result, run())
        self.assertEqual(result["budget_selection_policy"], "skill_round_robin_stable_hash_v1")
        self.assertEqual(result["counts"]["groups_selected"], 4)
        self.assertEqual(result["counts"]["assertions_omitted_by_budget"], 4)
        selected = {(row["skill"], row["case_id"], row["side"]) for row in result["results"]}
        for skill in ("alpha-skill", "beta-skill"):
            cases = {
                case_id for selected_skill, case_id, _side in selected if selected_skill == skill
            }
            self.assertEqual(len(cases), 1)
            case_id = next(iter(cases))
            self.assertIn((skill, case_id, "candidate"), selected)
            self.assertIn((skill, case_id, "baseline"), selected)

    def test_large_question_text_is_skipped_not_sent(self):
        report = sample_report()
        report["candidate"]["assertions"][0]["assertion"] = "x" * 2001
        self.path.write_text(json.dumps(report), encoding="utf-8")
        groups, counts = collect_groups(self.root, 24000)
        self.assertEqual(groups, [])
        self.assertEqual(counts["skipped_oversized_assertion"], 2)

    def test_unpaired_response_is_not_a_comparison(self):
        report = sample_report()
        report["baseline"] = {
            "assertions": report["baseline"]["assertions"],
            "manifest": {"status": "failed", "outputs": {"response": ""}},
        }
        self.path.write_text(json.dumps(report), encoding="utf-8")
        groups, counts = collect_groups(self.root, 24000)
        self.assertEqual(groups, [])
        self.assertEqual(counts["skipped_response"], 1)
        self.assertEqual(counts["skipped_unpaired_assertions"], 1)

    def test_benchmark_metrics_keep_abstentions_distinct(self):
        result = metrics(
            [
                {"prediction": "met", "label": "met", "met_probability": 0.9},
                {"prediction": "not_shown", "label": "not_met", "met_probability": 0.0},
            ]
        )
        self.assertEqual(result["accuracy"], 0.5)
        self.assertEqual(result["selective_met"][0]["accepted_met"], 1)
        self.assertEqual(result["selective_met"][0]["false_accepts"], 0)

    def test_summary_distinguishes_offline_complete_and_partial_coverage(self):
        selection = {
            "schema_version": 1,
            "status": "selected",
            "manifests": ["system-one/evals/evals.json"],
            "selected_count": 1,
            "expected_cases": {"system-one": ["test-case"]},
        }
        report = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            selection=selection,
        )
        self.assertIn("Offline contract check", render_summary(report))
        self.assertIn("0/2 prose assertions", render_summary(report))
        report["mode"] = "live"
        report["results"][0]["assertions"][0]["suggested_verdict"] = "met"
        report["results"][1]["assertions"][0]["suggested_verdict"] = "not_shown"
        self.assertIn("Complete selected-case advisory coverage", render_summary(report))
        report["results"][1]["assertions"] = []
        summary = render_summary(report)
        self.assertIn("Incomplete advisory coverage", summary)
        self.assertIn("1/2 prose assertions", summary)
        self.assertNotIn("A bounded answer", summary)

    def test_missing_expected_case_prevents_complete_coverage(self):
        selection = {
            "schema_version": 1,
            "status": "selected",
            "manifests": ["system-one/evals/evals.json"],
            "selected_count": 1,
            "expected_cases": {"system-one": ["test-case", "missing-case"]},
        }
        report = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            selection=selection,
        )
        self.assertEqual(report["selection_scope"]["missing_reports"], ["system-one/missing-case"])
        report["mode"] = "live"
        for row in report["results"]:
            row["assertions"][0]["suggested_verdict"] = "met"
        self.assertIn("Incomplete selected-case coverage", render_summary(report))
        self.assertIn("Missing case reports: 1", render_summary(report))

    def test_missing_whole_skill_and_unexpected_report_are_visible(self):
        selection = {
            "schema_version": 1,
            "status": "selected",
            "manifests": ["another-skill/evals/evals.json"],
            "selected_count": 1,
            "expected_cases": {"another-skill": ["other-case"]},
        }
        report = audit(
            self.root,
            live=False,
            key=None,
            max_calls=2,
            max_assertions=2,
            max_response_chars=24000,
            timeout=12.0,
            selection=selection,
        )
        self.assertEqual(report["selection_scope"]["missing_reports"], ["another-skill/other-case"])
        self.assertEqual(report["selection_scope"]["unexpected_reports"], ["system-one/test-case"])
        self.assertIn(
            "Selected-case coverage unknown",
            render_summary(
                {
                    **report,
                    "mode": "live",
                    "selection_scope": {**report["selection_scope"], "status": "not_provided"},
                }
            ),
        )

    def test_selection_evidence_rejects_unsafe_and_duplicate_ids(self):
        selection = {
            "schema_version": 1,
            "status": "selected",
            "manifests": ["../evals/evals.json"],
            "selected_count": 1,
            "expected_cases": {"..": ["test-case"]},
        }
        with self.assertRaisesRegex(ValueError, "unsafe selection manifest"):
            expected_report_ids(selection)
        selection = {
            "schema_version": 1,
            "status": "selected",
            "manifests": ["system-one/evals/evals.json"],
            "selected_count": 1,
            "expected_cases": {"system-one": ["test-case", "test-case"]},
        }
        with self.assertRaisesRegex(ValueError, "duplicate expected case ID"):
            expected_report_ids(selection)

    def test_audit_rejects_duplicate_comparison_identity(self):
        duplicate = self.reports / "another-run.comparison.json"
        duplicate.write_text(json.dumps(sample_report()), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate comparison report identity"):
            audit(
                self.root,
                live=False,
                key=None,
                max_calls=4,
                max_assertions=4,
                max_response_chars=24000,
                timeout=12.0,
            )

    def test_current_system_one_manifest_fits_ci_audit_budget(self):
        skill_root = Path(__file__).resolve().parent.parent
        workflow = (skill_root.parent / ".github" / "workflows" / "skill-eval.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("--max-calls 32", workflow)
        self.assertIn("--max-assertions 250", workflow)
        manifest = json.loads((skill_root / "evals" / "evals.json").read_text(encoding="utf-8"))
        cases = manifest["evals"]
        self.assertLessEqual(2 * len(cases), 32)
        self.assertLessEqual(2 * sum(len(case["assertions"]) for case in cases), 250)


if __name__ == "__main__":
    unittest.main()
