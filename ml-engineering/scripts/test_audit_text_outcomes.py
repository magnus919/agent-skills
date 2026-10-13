import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit_text_outcomes as audit


def extraction():
    text = "Aé B"
    span = {"label": "name", "start": 1, "end": 2, "text": "é"}
    return {
        "schema_version": 1,
        "source": text,
        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "labels": ["name"],
        "gold_provenance": {"kind": "reference", "evidence": "authored synthetic fixture"},
        "gold_entities": [span],
        "entities": [{**span, "score": 0.8}],
    }


def summary():
    text = "Approved action with a strict deadline."
    return {
        "schema_version": 1,
        "source": text,
        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "summary": "Action is approved; the deadline remains strict.",
        "summary_sha256": hashlib.sha256(
            b"Action is approved; the deadline remains strict."
        ).hexdigest(),
        "expected_fact_ids": ["action", "deadline"],
        "assessments": [
            {
                "fact_id": f,
                "relation": "supported",
                "critical": True,
                "reviewer_kind": "reference",
                "evidence": "authored synthetic receipt; no model execution",
            }
            for f in ("action", "deadline")
        ],
    }


class Tests(unittest.TestCase):
    def test_unicode_offsets_and_no_calibration_claim(self):
        r = audit.spans(extraction())
        self.assertTrue(r["checks_clear"])
        self.assertEqual(r["score_calibration"], "not_assessed")

    def test_wrong_or_missing_spans(self):
        r = extraction()
        r["entities"][0]["start"] = 0
        x = audit.spans(r)
        self.assertFalse(x["checks_clear"])
        self.assertIn("missing_gold_spans", {f["code"] for f in x["findings"]})

    def test_duplicate_and_nonfinite_prediction(self):
        r = extraction()
        r["entities"] *= 2
        self.assertFalse(audit.spans(r)["checks_clear"])
        r = extraction()
        r["entities"][0]["score"] = float("nan")
        self.assertFalse(audit.spans(r)["checks_clear"])

    def test_wrong_hash_and_teacher_gold(self):
        for change in (
            lambda r: r.update(source_sha256="wrong"),
            lambda r: r["gold_provenance"].update(kind="model_teacher"),
        ):
            r = extraction()
            change(r)
            with self.assertRaises(ValueError):
                audit.spans(r)

    def test_summary_receipts_not_semantic_execution(self):
        r = audit.summaries(summary())
        self.assertTrue(r["checks_clear"])
        self.assertEqual(r["semantic_execution"], "not_performed")

    def test_summary_missing_critical_and_provenance(self):
        r = summary()
        r["assessments"][0].update(relation="missing", reviewer_kind="model_teacher")
        r["assessments"].pop()
        x = audit.summaries(r)
        self.assertTrue(
            {"fact_missing", "unresolved_provenance", "missing_assessments"}
            <= {f["code"] for f in x["findings"]}
        )

    def test_cli_privacy_and_optimized_python(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            r = summary()
            r["source"] = "private person"
            r["source_sha256"] = "wrong"
            p.write_text(json.dumps(r))
            x = subprocess.run(
                [sys.executable, "-O", audit.__file__, "summary", str(p)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(x.returncode, 1)
            self.assertNotIn("private person", x.stdout + x.stderr)


if __name__ == "__main__":
    unittest.main()
