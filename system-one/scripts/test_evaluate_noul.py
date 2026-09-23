#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from evaluate_noul import evaluate, read_cases


class EvaluationTests(unittest.TestCase):
    def test_metrics_and_slices(self):
        rows = [{"id": "a", "probability": 0.9, "label": 1, "slice": "en"},
                {"id": "b", "probability": 0.8, "label": 0, "slice": "es"}]
        result = evaluate(rows, 0.85)
        self.assertEqual(result["overall"]["accepted"], 1)
        self.assertEqual(result["overall"]["accepted_precision"], 1)
        self.assertEqual(result["overall"]["false_accepts"], 0)
        self.assertEqual(set(result["slices"]), {"en", "es"})

    def test_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.jsonl"
            path.write_text('{"id":"a","probability":0.2,"label":0}\n'
                            '{"id":"a","probability":0.8,"label":1}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique ids"):
                read_cases(path)

    def test_rejects_nan(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.jsonl"
            path.write_text('{"id":"a","probability":NaN,"label":0}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "finite"):
                read_cases(path)


if __name__ == "__main__":
    unittest.main()
