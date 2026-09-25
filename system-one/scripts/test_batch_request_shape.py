"""Focused tests for the offline batch/request-shape analyzer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from batch_request_shape import analyze, read_rows


def row(condition: str, request_id: str, batch_size: int, position: int,
        case: str, qid: str, label: str, prediction: str,
        probabilities: dict[str, float], request_hash: str) -> dict:
    return {
        "model": "test", "model_revision": "r1", "split": "test",
        "condition": condition, "request_id": request_id,
        "batch_size": batch_size, "position": position, "replicate": 0,
        "case_id": case, "question_id": qid, "label": label,
        "prediction": prediction, "probabilities": probabilities,
        "contract_sha256": "a" * 64, "state_sha256": ("b" if case.endswith("a") else "c") * 64,
        "question_sha256": ("d" if qid == "route" else "e") * 64,
        "request_sha256": request_hash * 64, "status": "ok",
    }


def two_question_study() -> list[dict]:
    # A Choice-like question and a binary Noul-like question have different
    # class spaces but share the same state and combined batch call.
    state_a = "b" * 64
    state_b = "c" * 64
    route_hash = "d" * 64
    refund_hash = "e" * 64
    questions = [
        row("solo", "s-route", 1, 0, "case-a", "route", "technical", "technical",
            {"billing": .05, "technical": .9, "other": .05}, "1"),
        row("solo", "s-refund", 1, 0, "case-a", "refund", "no", "no",
            {"yes": .1, "no": .9}, "2"),
        row("batch", "b1", 2, 0, "case-a", "route", "technical", "technical",
            {"billing": .1, "technical": .85, "other": .05}, "3"),
        row("batch", "b1", 2, 1, "case-a", "refund", "no", "yes",
            {"yes": .7, "no": .3}, "3"),
    ]
    for item in questions:
        item["state_sha256"] = state_a
        item["question_sha256"] = route_hash if item["question_id"] == "route" else refund_hash
        item["contract_sha256"] = route_hash if item["question_id"] == "route" else refund_hash
    return questions


class BatchRequestShapeTests(unittest.TestCase):
    def read_jsonl(self, rows: list[dict]) -> list[dict]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "cases.jsonl"
        path.write_text("".join(json.dumps(item) + "\n" for item in rows), encoding="utf-8")
        return read_rows(path)

    def test_heterogeneous_questions_are_calibrated_separately(self):
        report = analyze(two_question_study(), seed=17)
        comparison = report["comparisons"][0]
        self.assertEqual(comparison["paired_questions"], 2)
        self.assertEqual(set(comparison["solo_by_question"]), {"route", "refund"})
        self.assertEqual(comparison["solo_by_question"]["route"]["n_success"], 1)
        self.assertEqual(comparison["batch_by_question"]["refund"]["brier"], .98)

    def test_bootstrap_is_stable_for_a_fixed_seed(self):
        rows = two_question_study()
        first = analyze(rows, seed=23)
        second = analyze(rows, seed=23)
        self.assertEqual(first["comparisons"][0]["paired_accuracy_delta"],
                         second["comparisons"][0]["paired_accuracy_delta"])

    def test_hash_or_label_mismatch_is_rejected(self):
        rows = two_question_study()
        rows[-1]["state_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "state, question, contract hash"):
            analyze(rows)

    def test_probability_mass_and_class_set_are_validated(self):
        rows = two_question_study()
        rows[0]["probabilities"]["technical"] = .7
        with self.assertRaisesRegex(ValueError, "sum to 1"):
            self.read_jsonl(rows)

    def test_inconsistent_probability_class_set_is_rejected(self):
        rows = two_question_study()
        extra = row("solo", "s-route-2", 1, 0, "case-b", "route", "technical", "technical",
                    {"technical": .9, "billing": .05, "other": .05}, "4")
        extra["question_sha256"] = rows[0]["question_sha256"]
        extra["contract_sha256"] = rows[0]["contract_sha256"]
        # The second output drops a required class, even though the top answer is unchanged.
        rows[0]["probabilities"] = {"technical": .95, "billing": .05}
        rows.append(extra)
        with self.assertRaisesRegex(ValueError, "same class set"):
            self.read_jsonl(rows)

    def test_incomplete_pair_is_reported_and_not_hidden(self):
        rows = two_question_study()
        rows = [r for r in rows if not (r["condition"] == "solo" and r["question_id"] == "refund")]
        result = analyze(rows)["comparisons"][0]
        self.assertEqual(result["missing_solo"], 1)
        self.assertEqual(result["paired_questions"], 1)

    def test_request_membership_and_request_hash_consistency_are_validated(self):
        rows = two_question_study()
        rows[-1]["request_sha256"] = "f" * 64
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rows.jsonl"
            path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "share request_sha256"):
                read_rows(path)

    def test_live_capture_json_is_readable_without_flattening_metadata(self):
        payload = {"schema_version": 1, "captured_rows": two_question_study()}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "capture.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(len(read_rows(path)), 4)


if __name__ == "__main__":
    unittest.main()
