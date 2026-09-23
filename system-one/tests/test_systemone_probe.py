#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("systemone_probe", ROOT / "scripts" / "systemone_probe.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ProbeValidationTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            "state": {"text": "Refund requested"},
            "questions": {
                "queue": {
                    "type": "choice",
                    "instructions": "Which queue?",
                    "criteria": {"billing": "Payments", "other": "Unknown"},
                },
                "refund": {"type": "noul", "instructions": "Is a refund requested?"},
            },
        }

    def test_request_accepts_choice_and_noul(self):
        self.assertEqual(MODULE.validate_request(self.request), self.request)

    def test_request_rejects_duplicate_options(self):
        self.request["questions"]["queue"]["criteria"] = ["billing", "billing"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.validate_request(self.request)

    def test_request_accepts_structured_criteria(self):
        self.request["questions"]["queue"]["instructions"] = {"task": "Route this ticket"}
        self.request["questions"]["queue"]["criteria"] = {"billing": ["payments", "refunds"], "other": {"reason": "fallback"}}
        self.request["questions"]["urgency"] = {"type": "score", "instructions": ["Assess urgency"], "criteria": [{"level": "routine"}, ["soon"], "blocking"]}
        self.assertEqual(MODULE.validate_request(self.request), self.request)

    def test_score_matches_probability_weighted_level(self):
        self.request["questions"] = {"urgency": {"type": "score", "instructions": "How urgent?", "criteria": ["routine", "soon", "blocking"]}}
        response = {"answers": {"urgency": {"type": "score", "score": 1.8, "legend": {"0": "routine", "1": "soon", "2": "blocking"}, "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7}, "confidence": 0.7}}}
        with self.assertRaisesRegex(ValueError, "probability-weighted"):
            MODULE.validate_response(self.request, response)

    def test_response_accepts_valid_contract(self):
        response = {
            "model": "test",
            "answers": {
                "queue": {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.8, "other": 0.2}, "confidence": 0.8},
                "refund": {"type": "noul", "noul": 0.9},
            },
        }
        self.assertEqual(MODULE.validate_response(self.request, response), response)

    def test_response_rejects_unknown_choice(self):
        response = {
            "answers": {
                "queue": {"type": "choice", "choice": "sales", "probabilities": {"billing": 0.2, "other": 0.8}, "confidence": 0.8},
                "refund": {"type": "noul", "noul": 0.1},
            }
        }
        with self.assertRaisesRegex(ValueError, "not in the request"):
            MODULE.validate_response(self.request, response)

    def test_response_rejects_wrong_probability_labels(self):
        response = {"answers": {
            "queue": {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.8, "sales": 0.2}, "confidence": 0.8},
            "refund": {"type": "noul", "noul": 0.9},
        }}
        with self.assertRaisesRegex(ValueError, "probability keys"):
            MODULE.validate_response(self.request, response)

    def test_response_rejects_extra_answer(self):
        response = {"answers": {
            "queue": {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.8, "other": 0.2}, "confidence": 0.8},
            "refund": {"type": "noul", "noul": 0.9},
            "unexpected": {"type": "noul", "noul": 0.1},
        }}
        with self.assertRaisesRegex(ValueError, "answer IDs"):
            MODULE.validate_response(self.request, response)

    def test_response_rejects_score_out_of_bounds(self):
        self.request["questions"] = {"urgency": {"type": "score", "instructions": "How urgent?", "criteria": ["routine", "soon", "blocking"]}}
        response = {"answers": {"urgency": {"type": "score", "score": 3.0, "legend": {"0": "routine", "1": "soon", "2": "blocking"}, "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7}, "confidence": 0.6}}}
        with self.assertRaisesRegex(ValueError, "within the rubric"):
            MODULE.validate_response(self.request, response)

    def test_offline_cli_does_not_call_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text(json.dumps(self.request), encoding="utf-8")
            self.assertEqual(MODULE.main(["--request", str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
