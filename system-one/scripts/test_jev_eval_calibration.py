"""Local calibration workflow: identity, blinding, pairing, and score tests."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jev_eval_audit import collect_groups
from jev_eval_calibration import compare_audits, compare_labels, prepare, read_audit, records_from_artifacts, score, select_records


class JevEvalCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        reports = self.root / "system-one" / "reports"
        reports.mkdir(parents=True)
        for case_id in ("case-a", "case-b"):
            assertions = ["Describes exact authorization", "Includes an unknown path"]
            def trial(side):
                return {
                    "assertions": [{"assertion": assertion, "verdict": "manual_review"} for assertion in assertions],
                    "manifest": {"status": "completed", "outputs": {"response": f"{case_id} {side} response"}},
                }
            report = {"skill_name": "system-one", "case_id": case_id,
                      "candidate": trial("candidate"), "baseline": trial("baseline")}
            (reports / f"{case_id}.comparison.json").write_text(json.dumps(report), encoding="utf-8")
        groups, _ = collect_groups(self.root, 24_000)
        rows = []
        for group in groups:
            rows.append({"skill": group["skill"], "case_id": group["case_id"],
                         "side": group["side"], "response_sha256": group["response_sha256"],
                         "assertions": [{"assertion": assertion, "suggested_verdict": "met",
                                         "met_probability": 0.9, "provider_confidence": 0.8}
                                        for assertion in group["assertions"]]})
        self.audit = {"schema_version": 1, "mode": "live", "advisory_only": True,
                      "model_requested": "jev-1.13.0", "counts": {
                          "prose_assertions_seen": 8, "assertions_selected": 8,
                          "groups_selected": 4,
                          "skipped_response": 0, "skipped_oversized_assertion": 0,
                          "skipped_oversized_group": 0, "skipped_unpaired_assertions": 0,
                          "assertions_omitted_by_budget": 0,
                          "groups_not_attempted_after_error": 0,
                          "assertions_not_attempted_after_error": 0, "provider_errors": 0},
                      "results": rows}
        self.audit_path = self.root / "audit.json"
        self.audit_path.write_text(json.dumps(self.audit), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_pair_sample_is_deterministic_and_blinded(self):
        records = records_from_artifacts(self.root, self.audit)
        selected = select_records(records, "frozen-seed", 2, 2)
        self.assertEqual(selected, select_records(records, "frozen-seed", 2, 2))
        population = [item for item in selected if item["sample_class"] == "population"]
        self.assertEqual(len(population), 4)
        by_assertion = {}
        for item in population:
            by_assertion.setdefault((item["case_id"], item["assertion"]), set()).add(item["side"])
        self.assertTrue(all(sides == {"candidate", "baseline"} for sides in by_assertion.values()))
        output = self.root / "private-review"
        summary = prepare(self.root, self.audit_path, output, "run-1", "frozen-seed", 2, 2)
        self.assertEqual(summary["total_review_items"], 6)
        packet = (output / "review-packet.md").read_text(encoding="utf-8")
        self.assertIn("case-a candidate response", packet)
        self.assertNotIn("suggested_verdict", packet)
        self.assertNotIn("met_probability", packet)
        private_map = (output / "private-map.json").read_text(encoding="utf-8")
        self.assertNotIn("case-a candidate response", private_map)
        self.assertEqual(os.stat(output).st_mode & 0o777, 0o700)
        self.assertEqual(os.stat(output / "review-packet.md").st_mode & 0o777, 0o600)

    def test_mismatched_or_partial_audit_is_rejected(self):
        self.audit["results"][0]["response_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "response identity"):
            records_from_artifacts(self.root, self.audit)
        self.audit["counts"]["provider_errors"] = 1
        self.audit_path.write_text(json.dumps(self.audit), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "coverage is incomplete"):
            read_audit(self.audit_path)

    def test_score_keeps_population_and_challenge_separate(self):
        records = records_from_artifacts(self.root, self.audit)
        selected = select_records(records, "frozen-seed", 2, 2)
        private_map = {"schema_version": 1, "source_run_id": "run-1", "model": "jev-1.13.0",
                       "items": selected}
        labels = {"schema_version": 1, "reviewer_id": "reviewer-a", "blind_to_predictions": True,
                  "labels": [{"id": item["id"], "label": "not_met" if index == 0 else "met",
                              "evidence": "Checked visible response against the assertion"}
                             for index, item in enumerate(selected)]}
        result = score(private_map, labels)
        self.assertEqual(result["population"]["selected"], 4)
        self.assertEqual(result["challenge_high_met"]["selected"], 2)
        self.assertEqual(result["population"]["resolved"] + result["challenge_high_met"]["resolved"], 6)
        labels["labels"][0]["label"] = ""
        with self.assertRaisesRegex(ValueError, "every review item needs"):
            score(private_map, labels)

    def test_blind_reviewer_comparison_has_no_jev_predictions(self):
        first = {"schema_version": 1, "reviewer_id": "a", "blind_to_predictions": True,
                 "labels": [{"id": "j1", "label": "met", "evidence": "visible contract"},
                            {"id": "j2", "label": "not_shown", "evidence": "missing evidence"}]}
        second = {"schema_version": 1, "reviewer_id": "b", "blind_to_predictions": True,
                  "labels": [{"id": "j2", "label": "not_met", "evidence": "incompatible shape"},
                             {"id": "j1", "label": "met", "evidence": "visible contract"}]}
        result = compare_labels(first, second)
        self.assertEqual((result["items"], result["agreements"], len(result["disagreements"])), (2, 1, 1))
        self.assertEqual(result["disagreements"][0]["id"], "j2")
        self.assertNotIn("suggested_verdict", json.dumps(result))
        second["reviewer_id"] = "a"
        with self.assertRaisesRegex(ValueError, "distinct reviewer IDs"):
            compare_labels(first, second)
        second["reviewer_id"] = "b"
        second["labels"][0]["id"] = "other"
        with self.assertRaisesRegex(ValueError, "same item IDs"):
            compare_labels(first, second)

    def test_compare_cli_writes_private_disagreement_file(self):
        first = {"schema_version": 1, "reviewer_id": "a", "blind_to_predictions": True,
                 "labels": [{"id": "j1", "label": "met", "evidence": "visible"}]}
        second = {"schema_version": 1, "reviewer_id": "b", "blind_to_predictions": True,
                  "labels": [{"id": "j1", "label": "not_shown", "evidence": "missing"}]}
        first_path, second_path, output = (self.root / name for name in ("first.json", "second.json", "comparison.json"))
        first_path.write_text(json.dumps(first), encoding="utf-8")
        second_path.write_text(json.dumps(second), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("jev_eval_calibration.py")), "compare",
             "--first", str(first_path), "--second", str(second_path), "--output", str(output)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.stat(output).st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["agreements"], 0)

    def test_stability_requires_identical_inputs_and_reports_flip(self):
        repeated = json.loads(json.dumps(self.audit))
        repeated["results"][0]["assertions"][0]["suggested_verdict"] = "not_shown"
        repeated["results"][0]["assertions"][0]["met_probability"] = 0.45
        result = compare_audits(self.audit, repeated)
        self.assertEqual((result["matched_groups"], result["matched_assertions"]), (4, 8))
        self.assertEqual(len(result["verdict_flips"]), 1)
        self.assertNotIn("Describes exact authorization", json.dumps(result))
        repeated["results"][0]["response_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "identical response groups"):
            compare_audits(self.audit, repeated)
        repeated["results"][0]["response_sha256"] = self.audit["results"][0]["response_sha256"]
        repeated["results"][0]["assertions"][0]["assertion"] = "changed criterion"
        with self.assertRaisesRegex(ValueError, "identical assertion text"):
            compare_audits(self.audit, repeated)


if __name__ == "__main__":
    unittest.main()
