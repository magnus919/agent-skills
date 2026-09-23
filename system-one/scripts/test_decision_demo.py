#!/usr/bin/env python3
import unittest

from decision_demo import policy


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.request = {"state": {}, "questions": {
            "queue": {"type": "choice", "instructions": "Which?", "criteria": ["billing", "other"]},
            "refund_requested": {"type": "noul", "instructions": "Refund?"},
        }}
        self.response = {"answers": {
            "queue": {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.9, "other": 0.1}, "confidence": 0.8},
            "refund_requested": {"type": "noul", "noul": 0.9},
        }}

    def test_routes_without_approving_refund(self):
        self.assertEqual(policy(self.request, self.response)["lane"], "route_only")
        self.assertTrue(policy(self.request, self.response)["refund_flag"])

    def test_uncertain_goes_to_review(self):
        self.response["answers"]["queue"]["confidence"] = 0.2
        self.assertEqual(policy(self.request, self.response)["lane"], "human_review")

    def test_bad_answer_cannot_reach_policy(self):
        self.response["answers"]["queue"]["probabilities"]["sales"] = 0.0
        with self.assertRaises(ValueError):
            policy(self.request, self.response)


if __name__ == "__main__":
    unittest.main()
