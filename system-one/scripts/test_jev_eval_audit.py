"""Contract checks for the advisory Jev eval artifact reader."""

import json
import tempfile
import unittest
from pathlib import Path

from jev_eval_audit import (
    _read_json,
    audit,
    build_request,
    collect_groups,
    expected_report_ids,
    render_summary,
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


if __name__ == "__main__":
    unittest.main()
