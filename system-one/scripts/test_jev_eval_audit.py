"""Contract checks for the advisory Jev eval artifact reader."""

import json
import tempfile
import unittest
from pathlib import Path

from jev_eval_audit import _read_json, audit, build_request, collect_groups
from jev_eval_benchmark import metrics


def sample_report(response="A bounded answer"):
    trial = {
        "assertions": [
            {"assertion": "Explains the boundary", "verdict": "manual_review"},
            {"assertion": "exit_code == 0", "verdict": "pass"},
        ],
        "manifest": {"status": "completed", "outputs": {"response": response}},
    }
    return {"skill_name": "system-one", "case_id": "test-case", "candidate": trial, "baseline": trial}


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
        self.assertEqual((len(groups), counts["prose_assertions_seen"], counts["exact_assertions_untouched"]), (2, 2, 2))
        self.assertEqual(groups[0]["assertions"], ["Explains the boundary"])
        request = build_request(groups[0])
        self.assertEqual(request["model"], "jev-1.13.0")
        result = audit(self.root, live=False, key=None, max_calls=2, max_assertions=2,
                       max_response_chars=24000, timeout=12.0)
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
        result = audit(self.root, live=False, key=None, max_calls=1, max_assertions=1,
                       max_response_chars=24000, timeout=12.0)
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
        report["baseline"] = {"assertions": report["baseline"]["assertions"],
                              "manifest": {"status": "failed", "outputs": {"response": ""}}}
        self.path.write_text(json.dumps(report), encoding="utf-8")
        groups, counts = collect_groups(self.root, 24000)
        self.assertEqual(groups, [])
        self.assertEqual(counts["skipped_response"], 1)
        self.assertEqual(counts["skipped_unpaired_assertions"], 1)

    def test_benchmark_metrics_keep_abstentions_distinct(self):
        result = metrics([
            {"prediction": "met", "label": "met", "met_probability": 0.9},
            {"prediction": "not_shown", "label": "not_met", "met_probability": 0.0},
        ])
        self.assertEqual(result["accuracy"], 0.5)
        self.assertEqual(result["selective_met"][0]["accepted_met"], 1)
        self.assertEqual(result["selective_met"][0]["false_accepts"], 0)


if __name__ == "__main__":
    unittest.main()
