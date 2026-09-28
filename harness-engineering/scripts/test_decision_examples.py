"""Regression tests for offline System One decision examples."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("decision_examples.py")
SPEC = importlib.util.spec_from_file_location("decision_examples", SCRIPT)
examples_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(examples_module)


class DecisionExampleTests(unittest.TestCase):
    def test_canned_cases_cover_match_no_match_unavailable_and_action_outcomes(self):
        output = examples_module.examples()
        self.assertEqual(output["selection"]["cases"]["satisfying"]["route"], "select")
        self.assertEqual(output["selection"]["cases"]["near_miss_no_match"]["route"], "no_match")
        self.assertEqual(output["selection"]["cases"]["unavailable"]["route"], "escalate")
        self.assertEqual(output["action"]["cases"]["satisfying"]["status"], "verified")
        self.assertFalse(output["action"]["cases"]["stale_evidence"]["simulated_executor_fixture_used"])
        self.assertEqual(output["action"]["cases"]["no_effect"]["status"], "failed")
        self.assertTrue(all("SYNTHETIC OFFLINE FIXTURE" in x["provenance"] for x in output.values()))

    def test_invalid_finite_probabilities_rejected(self):
        candidates = [{"id": "a"}]
        for value in (float("nan"), float("inf"), float("-inf"), -0.01, 1.01, True, "0.9"):
            with self.subTest(value=value), self.assertRaises(examples_module.ContractError):
                examples_module.select_candidate(candidates, {"outcome": "candidate", "candidate_id": "a", "p_applicable": value}, 0.5)

    def test_cutoff_must_be_finite_probability(self):
        with self.assertRaises(examples_module.ContractError):
            examples_module.select_candidate([{"id": "a"}], {"outcome": "no_match", "candidate_id": None}, float("nan"))

    def test_candidate_ids_must_be_unique_and_selected_candidate_must_exist(self):
        answer = {"outcome": "candidate", "candidate_id": "a", "p_applicable": 0.9}
        with self.assertRaisesRegex(examples_module.ContractError, "unique"):
            examples_module.select_candidate([{"id": "a"}, {"id": "a"}], answer, 0.5)
        answer["candidate_id"] = "unlisted"
        with self.assertRaisesRegex(examples_module.ContractError, "supplied candidate"):
            examples_module.select_candidate([{"id": "a"}], answer, 0.5)

    def test_action_must_be_allowlisted_and_bound_to_current_revision(self):
        proposal = {"action_id": "write", "evidence_revision": "r1", "expected_effect": "done"}
        allowed = [{"id": "write"}]
        result = examples_module.select_and_check_action(proposal, allowed, {"revision": "r1"}, "r2", {"effect": "done", "outcome": "pass"})
        self.assertEqual(result["reason"], "stale_evidence")
        self.assertFalse(result["simulated_executor_fixture_used"])
        proposal["action_id"] = "other"
        with self.assertRaisesRegex(examples_module.ContractError, "allowed action"):
            examples_module.select_and_check_action(proposal, allowed, {"revision": "r1"}, "r1", {"effect": "done", "outcome": "pass"})
        for invalid in ([{"id": None}], [{"id": ""}], [{"id": 4}]):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(examples_module.ContractError, "ids"):
                examples_module.select_and_check_action({**proposal, "action_id": "write"}, invalid, {"revision": "r1"}, "r1", {"effect": "done", "outcome": "pass"})

    def test_action_error_unknown_outcome_and_no_effect_are_not_success(self):
        allowed = [{"id": "refresh"}]
        proposal = {"action_id": "refresh", "evidence_revision": "r1", "expected_effect": "changed"}
        self.assertEqual(examples_module.select_and_check_action(proposal, allowed, {"revision": "r1"}, "r1", {"error": "timeout"})["status"], "unknown")
        self.assertEqual(examples_module.select_and_check_action(proposal, allowed, {"revision": "r1"}, "r1", {"effect": "changed", "outcome": "unknown"})["status"], "incomplete")
        self.assertEqual(examples_module.select_and_check_action(proposal, allowed, {"revision": "r1"}, "r1", {"effect": None, "outcome": "fail"})["status"], "failed")
        self.assertNotEqual(examples_module.select_and_check_action(proposal, allowed, {"revision": "r1"}, "r1", {"outcome": "pass"})["status"], "verified")
        with self.assertRaisesRegex(examples_module.ContractError, "expected_effect"):
            examples_module.select_and_check_action({"action_id": "refresh", "evidence_revision": "r1"}, allowed, {"revision": "r1"}, "r1", {"outcome": "pass"})

    def test_review_requires_current_known_evidence_and_does_not_grant_authority(self):
        evidence = {"e1": "matching host record"}
        review = {"revision": "r1", "disposition": "supported", "evidence_ids": ["e1"], "findings": []}
        result = examples_module.review_proposal(review, evidence, "r1")
        self.assertEqual(result["permission"], "not_granted")
        self.assertEqual(examples_module.deterministic_policy(result, False)["authorization"], "denied_by_host")
        self.assertEqual(examples_module.deterministic_policy(result, True)["authorization"], "granted_by_host")
        review["evidence_ids"] = []
        with self.assertRaisesRegex(examples_module.ContractError, "at least one"):
            examples_module.review_proposal(review, evidence, "r1")
        review["evidence_ids"] = ["invented"]
        with self.assertRaisesRegex(examples_module.ContractError, "outside"):
            examples_module.review_proposal(review, evidence, "r1")

    def test_stale_or_uncertain_semantic_review_holds(self):
        for status, disposition in (("rejected", "supported"), ("reviewed", "uncertain"), ("reviewed", "unsupported")):
            policy = examples_module.deterministic_policy({"status": status, "disposition": disposition}, True)
            self.assertEqual(policy["decision"], "hold")
            self.assertEqual(policy["authorization"], "not_granted")

    def test_cli_is_offline_machine_readable_and_scenario_scoped(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "selection", "--json"], capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(set(result), {"selection"})
        self.assertIn("SYNTHETIC OFFLINE FIXTURE", result["selection"]["provenance"])


if __name__ == "__main__":
    unittest.main()
