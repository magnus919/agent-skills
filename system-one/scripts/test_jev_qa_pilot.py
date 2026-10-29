"""Contract checks for the synthetic, advisory Jev QA pilot."""

import importlib.util
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("jev_qa_pilot.py")
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("jev_qa_pilot", SCRIPT)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    def test_fixture_has_unique_ids_and_all_lanes(self):
        ids = [case_id for _, case_id, _, _ in pilot.CASES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({kind for kind, _, _, _ in pilot.CASES}, {"triage", "test_choice", "semantic_grade"})
        self.assertEqual(len(ids), 22)

    def test_offline_baseline_is_reproducible(self):
        output = io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPT)]), redirect_stdout(output):
            self.assertEqual(pilot.main(), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["calls_attempted"], 0)
        self.assertEqual(sum(group["baseline_correct"] for group in report["by_kind"].values()), 17)

    def test_live_requires_secret(self):
        with patch.object(sys, "argv", [str(SCRIPT), "--live"]), patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as caught:
                pilot.main()
        self.assertEqual(caught.exception.code, 2)

    def test_label_is_not_sent_to_provider(self):
        import systemone_probe

        sent = []

        def fake_call(url, request, key, timeout):
            sent.append(request)
            self.assertEqual(key, "test-secret")
            answer = {
                "type": "choice",
                "choice": "code",
                "confidence": 1.0,
                "probabilities": {name: float(name == "code") for name in pilot.TRIAGE},
            }
            return 200, {"model": "jev-1.13.0", "answers": {"judgment": answer}}, 1.0

        output = io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPT), "--live", "--max-calls", "1"]), patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-secret"}), patch.object(systemone_probe, "live_call", fake_call), redirect_stdout(output):
            self.assertEqual(pilot.main(), 0)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["model"], "jev-latest")
        self.assertEqual(json.loads(output.getvalue())["model_requested"], "jev-latest")
        self.assertEqual(json.loads(output.getvalue())["cases"][0]["model"], "jev-1.13.0")
        self.assertNotIn("label", json.dumps(sent[0]))
        self.assertNotIn("test-secret", output.getvalue())
        row = json.loads(output.getvalue())["cases"][0]
        self.assertEqual(row["selected_option_probability"], 1.0)
        self.assertEqual(row["provider_confidence"], 1.0)
        self.assertNotIn("noul_yes_probability", row)

    def test_alias_resolution_and_pinned_mismatch(self):
        import systemone_probe

        for requested, returned, expected in [
            ("jev-preview", "jev-1.14.0", 0),
            ("jev-latest", "jev-1.14.0", 0),  # Future stable promotion.
            ("jev-1.14.0", "jev-1.14.0", 0),
            ("jev-1.14.0", "jev-1.13.0", 1),
            ("jev-preview", "jev-preview", 1),  # Missing resolved identity.
            ("jev-latest", "clm-latest", 1),
        ]:
            with self.subTest(requested=requested, returned=returned):
                answer = {"type": "choice", "choice": "code", "confidence": 1.0,
                          "probabilities": {name: float(name == "code") for name in pilot.TRIAGE}}
                output = io.StringIO()
                with patch.object(sys, "argv", [str(SCRIPT), "--live", "--max-calls", "1", "--model", requested]), patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-secret"}), patch.object(systemone_probe, "live_call", return_value=(200, {"model": returned, "answers": {"judgment": answer}}, 1.0)), redirect_stdout(output):
                    self.assertEqual(pilot.main(), expected)
                report = json.loads(output.getvalue())
                self.assertEqual(report["calls_attempted"], 1)
                self.assertEqual(report["model_requested"], requested)
                self.assertEqual("jev_error" in report["cases"][0], bool(expected))


if __name__ == "__main__":
    unittest.main()
