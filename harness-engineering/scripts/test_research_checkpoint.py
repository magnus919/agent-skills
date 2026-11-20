"""Offline challenges: artificial records, no retrieval or model call."""

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("research_checkpoint.py")
SPEC = importlib.util.spec_from_file_location("research_checkpoint", SCRIPT)
checkpoint_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checkpoint_module)
screen = checkpoint_module.screen


def example():
    return {
        "claims": {"C": {"primary_required": True, "min_independent_origins": 2}},
        "sources": {i: {"retrieval": "captured", "revision": "r1"} for i in ("primary", "summary")},
        "links": [
            {"source": "primary", "claim": "C", "relation": "supports", "review": "verified",
             "source_revision": "r1", "locator": "row 3", "origin": "study-a", "primary_for_claim": True},
            {"source": "summary", "claim": "C", "relation": "supports", "review": "verified",
             "source_revision": "r1", "locator": "paragraph 4", "origin": "study-a"},
        ],
        "followup_budget": 1,
        "reserved_followups": [],
    }


class ResearchCheckpointTest(unittest.TestCase):
    def test_duplicate_origin_does_not_corroborate(self):
        r = screen(example())
        self.assertEqual(r["captures"], 2)
        self.assertEqual(r["verified_links"], 2)
        self.assertEqual(r["disposition"], "targeted_followup_available")
        self.assertEqual(r["next_candidate"]["reservation_key"], "C:insufficient_independent_origins")

    def test_candidate_is_not_support_and_primary_is_missing(self):
        x = example()
        x["links"][0]["review"] = "proposed"
        r = screen(x)
        self.assertEqual(r["proposed_links"], 1)
        self.assertIn({"claim": "C", "reason": "missing_primary"}, r["material_gaps"])

    def test_reviewed_independent_sources_only_ready_for_review(self):
        x = example()
        x["links"][1]["origin"] = "study-b"
        self.assertEqual(screen(x)["disposition"], "ready_for_acceptance_review")

    def test_unknown_origin_has_no_independence_credit(self):
        for value in ("", "  ", None, "unknown", "  UnKnOwN  "):
            with self.subTest(value=value):
                x = example()
                x["links"][1]["origin"] = value
                self.assertEqual(screen(x)["next_candidate"]["reason"], "insufficient_independent_origins")

    def test_whitespace_cannot_split_one_origin(self):
        x = example()
        x["links"][1]["origin"] = "  study-a  "
        self.assertEqual(screen(x)["next_candidate"]["reason"], "insufficient_independent_origins")

    def test_potential_contradiction_holds_even_when_support_sufficient(self):
        x = example()
        x["links"][1]["origin"] = "study-b"
        x["links"].append({"source": "summary", "claim": "C", "relation": "contradicts", "review": "proposed"})
        self.assertEqual(screen(x)["disposition"], "needs_review")
        self.assertIsNone(screen(x)["next_candidate"])
        x["links"][-1]["review"] = "rejected"
        self.assertEqual(screen(x)["disposition"], "ready_for_acceptance_review")

    def test_restored_reservation_does_not_offer_duplicate_and_exhausts_budget(self):
        x = example()
        x["reserved_followups"] = [screen(x)["next_candidate"]["reservation_key"]]
        r = screen(x)
        self.assertEqual(r["disposition"], "incomplete")
        self.assertIsNone(r["next_candidate"])

    def test_resumed_gap_not_reissued_even_with_remaining_budget(self):
        x = example()
        x["followup_budget"] = 2
        x["reserved_followups"] = [screen(x)["next_candidate"]["reservation_key"]]
        r = screen(x)
        self.assertEqual(r["disposition"], "incomplete")
        self.assertIsNone(r["next_candidate"])

    def test_uncaptured_or_changed_source_invalidates_review(self):
        for key, value in (("revision", "r2"), ("retrieval", "unavailable")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                x = example()
                x["sources"]["primary"][key] = value
                screen(x)
