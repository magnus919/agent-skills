"""Meaningful schema, leakage, bounded scanning and privacy challenges."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import decision_audit as audit


def row(state="private invoice text", group="source-a"):
    return {
        "state": state,
        "group_id": group,
        "questions": {
            "team": {
                "type": "choice",
                "instructions": "Owner?",
                "criteria": {"billing": "Payments", "tech": "Bugs"},
            },
            "refund": {"type": "noul", "instructions": "Refund?"},
            "urgency": {
                "type": "score",
                "instructions": "Urgent?",
                "criteria": ["routine", "today"],
            },
        },
        "gold": {"team": "billing", "refund": True, "urgency": 1},
    }


class DecisionAuditTests(unittest.TestCase):
    def write(self, directory, name, rows):
        path = Path(directory) / name
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        return path

    def test_valid_three_types(self):
        self.assertEqual(audit.validate_row(row()), {"choice": 1, "noul": 1, "score": 1})

    def test_wrong_hard_labels(self):
        for key, value in [
            ("team", "absent"),
            ("refund", 1),
            ("urgency", True),
            ("urgency", 2),
            ("urgency", -1),
            ("urgency", 0.5),
            ("team", {"probabilities": {"billing": 1.0}}),
        ]:
            with self.subTest(key=key, value=value):
                item = row()
                item["gold"][key] = value
                with self.assertRaises(ValueError):
                    audit.validate_row(item)

    def test_missing_extra_gold(self):
        for change in (lambda g: g.pop("refund"), lambda g: g.update(extra=True)):
            item = row()
            change(item["gold"])
            with self.assertRaises(ValueError):
                audit.validate_row(item)

    def test_question_shapes(self):
        for value in (
            {"type": "unknown", "instructions": "X"},
            {"type": "choice", "instructions": "X", "criteria": {"billing": "Only"}},
            {"type": "choice", "instructions": "X", "criteria": ["billing", "tech"]},
            {"type": "noul", "instructions": ""},
            {"type": "noul", "instructions": "X", "criteria": {"yes": "Yes"}},
        ):
            item = row()
            item["questions"]["refund"] = value
            with self.assertRaises(ValueError):
                audit.validate_row(item)

    def test_string_columns_explicitly_rejected(self):
        item = row()
        item["questions"] = json.dumps(item["questions"])
        with self.assertRaises(ValueError):
            audit.validate_row(item)

    def test_changed_labels_do_not_hide_state_leakage(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = row(), row(group="source-b")
            b["gold"]["refund"] = False
            report = audit.audit(
                {"train": self.write(d, "a", [a]), "test": self.write(d, "b", [b])}
            )
            self.assertFalse(report["ok"])
            self.assertEqual(report["overlap"][0]["field"], "state")
            self.assertNotIn("private invoice text", json.dumps(report))
            self.assertNotIn("source-a", json.dumps(report))

    def test_group_leakage_across_different_states(self):
        with tempfile.TemporaryDirectory() as d:
            report = audit.audit(
                {
                    "train": self.write(d, "a", [row()]),
                    "calibration": self.write(d, "b", [row("paraphrase")]),
                }
            )
            self.assertEqual(report["overlap"][0]["field"], "group_id")

    def test_metadata_does_not_hide_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            a = row()
            b = copy.deepcopy(a)
            b.update(id="different", group_id="different")
            result, _, _ = audit.scan(self.write(d, "a", [a, b]))
            self.assertEqual(result["findings"][0]["code"], "duplicate_content")

    def test_empty_and_missing_inputs_fail(self):
        with tempfile.TemporaryDirectory() as d:
            empty = self.write(d, "empty", [])
            for path in (empty, Path(d) / "missing"):
                with self.subTest(path=path):
                    self.assertFalse(audit.audit({"train": path})["ok"])

    def test_row_and_line_limits_stop_scanning(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.write(d, "a", [row(), row("other", "other")])
            for limits in ({"max_rows": 1}, {"max_line_bytes": 10}):
                result, _, _ = audit.scan(path, **limits)
                self.assertFalse(result["complete"])
                self.assertIn("scan_limit", [f["code"] for f in result["findings"]])

    def test_duplicate_keys_and_nonfinite_values_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for text in (
                '{"state":"a","state":"b"}\n',
                '{"state":NaN}\n',
                '{"state":Infinity}\n',
                "\xff\n",
                "\n",
            ):
                path = Path(d) / "bad"
                path.write_text(text)
                self.assertEqual(audit.scan(path)[0]["valid_rows"], 0)

    def test_unicode_surrogate_and_deep_json_report_findings(self):
        with tempfile.TemporaryDirectory() as d:
            bad = row()
            bad["state"] = "\ud800"
            path = self.write(d, "surrogate", [bad])
            self.assertFalse(audit.audit({"train": path})["ok"])
            path.write_text("[" * 2000 + "]" * 2000 + "\n")
            self.assertFalse(audit.audit({"train": path})["ok"])

    def test_overflow_number_is_rejected_even_in_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.write(d, "a", [row()])
            path.write_text(path.read_text().rstrip()[:-1] + ', "metadata": 1e999}\n')
            self.assertFalse(audit.audit({"train": path})["ok"])

    def test_bundled_three_splits_pass_without_runtime_claim(self):
        base = Path(__file__).resolve().parents[1] / "assets"
        report = audit.audit(
            {s: base / f"decision-{s}.jsonl" for s in ("train", "calibration", "test")}
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["runtime_status"], "not_run")
        self.assertEqual(
            report["splits"]["train"]["questions"], {"choice": 2, "noul": 2, "score": 2}
        )


if __name__ == "__main__":
    unittest.main()
