#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from cascade_economics import evaluate, read_cases


ROOT = Path(__file__).resolve().parents[1]


class CascadeEconomicsTests(unittest.TestCase):
    def test_synthetic_fixture_counts_full_fallback_cost_and_abstention(self):
        rows = read_cases(ROOT / "examples" / "cascade.synthetic.jsonl")
        result = evaluate(rows, "best_single")
        cascade = result["policies"]["full_cascade"]
        self.assertEqual(cascade["n"], 6)
        self.assertEqual(cascade["correct"], 5)
        self.assertEqual(cascade["abstained"], 1)
        self.assertEqual(cascade["accuracy_all_cases"], 0.833333)
        self.assertEqual(cascade["fallback_cases"], 2)
        self.assertEqual(cascade["stages"]["fallback"]["calls"], 4)
        self.assertAlmostEqual(cascade["total_cost_usd"], 0.0028)
        self.assertEqual(result["paired_vs_baseline"]["full_cascade"]["paired_correctness_wins"], 2)
        self.assertEqual(result["paired_vs_baseline"]["full_cascade"]["paired_correctness_losses"], 1)
        self.assertEqual(result["slices"]["email-es"]["full_cascade"]["n"], 2)
        self.assertIn("mechanics checks only", result["bootstrap"]["warning"])

    def test_bootstrap_is_deterministic_and_reports_paired_deltas(self):
        rows = read_cases(ROOT / "examples" / "cascade.synthetic.jsonl")
        result = evaluate(rows, "best_single", bootstrap_replicates=400, seed=73)
        repeated = evaluate(rows, "best_single", bootstrap_replicates=400, seed=73)
        pair = result["paired_vs_baseline"]["full_cascade"]
        interval = pair["paired_bootstrap_95"]
        self.assertEqual(interval, repeated["paired_vs_baseline"]["full_cascade"]["paired_bootstrap_95"])
        self.assertAlmostEqual(interval["delta_accuracy_all_cases"]["estimate"], 1 / 6, places=6)
        self.assertAlmostEqual(interval["delta_mean_cost_per_case_usd"]["estimate"], 0.001 / 6, places=9)
        self.assertAlmostEqual(interval["delta_mean_latency_ms"]["estimate"], 29 + 1 / 3, places=6)
        for metric in interval.values():
            self.assertLessEqual(metric["low"], metric["high"])
        self.assertEqual(result["bootstrap"]["seed"], 73)
        self.assertEqual(result["bootstrap"]["resamples"], 400)

    def test_rejects_invalid_bootstrap_configuration(self):
        rows = read_cases(ROOT / "examples" / "cascade.synthetic.jsonl")
        with self.assertRaisesRegex(ValueError, "positive integer"):
            evaluate(rows, "best_single", bootstrap_replicates=0)
        with self.assertRaisesRegex(ValueError, "seed must be an integer"):
            evaluate(rows, "best_single", seed=1.5)

    def test_rejects_cost_that_omits_a_pipeline_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.jsonl"
            path.write_text(
                '{"id":"x","label":"yes","policies":{"p":{"decision":"yes",'
                '"cost_usd":0.1,"latency_ms":10,"stages":[{"name":"primary",'
                '"calls":1,"cost_usd":0.05,"latency_ms":5}]}}}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "sum of stage costs"):
                read_cases(path)

    def test_requires_same_policy_set_for_paired_comparison(self):
        base = {"id": "x", "label": "yes", "policies": {"base": {"decision": "yes", "cost_usd": 0, "latency_ms": 1, "stages": []}}}
        other = {"id": "y", "label": "no", "policies": {"candidate": {"decision": "no", "cost_usd": 0, "latency_ms": 1, "stages": []}}}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.jsonl"
            path.write_text(json.dumps(base) + "\n" + json.dumps(other) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "same policy names"):
                read_cases(path)

    def test_rejects_nonzero_cost_for_unchosen_branch(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.jsonl"
            path.write_text(
                '{"id":"x","label":"yes","policies":{"p":{"decision":null,'
                '"cost_usd":0.01,"latency_ms":1,"stages":[{"name":"fallback",'
                '"calls":0,"cost_usd":0.01,"latency_ms":0}]}}}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "uncalled stage"):
                read_cases(path)

    def test_unpriced_cost_remains_unknown_and_bootstrap_uses_paired_priced_cases(self):
        rows = []
        for case_id, label, base_cost, candidate_cost, input_tokens in (
            ("priced", "yes", 0.1, 0.2, 12),
            ("unpriced", "no", None, None, None),
        ):
            rows.append({
                "id": case_id, "label": label,
                "policies": {
                    "base": {"decision": label, "cost_usd": base_cost, "latency_ms": 10,
                             "stages": [{"name": "model", "calls": 1, "cost_usd": base_cost,
                                         "latency_ms": 10, "input_tokens": input_tokens,
                                         "output_tokens": 3 if input_tokens is not None else None,
                                         "total_tokens": 15 if input_tokens is not None else None}]},
                    "candidate": {"decision": label, "cost_usd": candidate_cost, "latency_ms": 20,
                                  "stages": [{"name": "model", "calls": 1, "cost_usd": candidate_cost,
                                              "latency_ms": 20, "input_tokens": input_tokens,
                                              "output_tokens": 3 if input_tokens is not None else None,
                                              "total_tokens": 15 if input_tokens is not None else None}]},
                },
            })
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "traces.json"
            path.write_text(json.dumps({"cases": rows, "metadata": {"private": True}}), encoding="utf-8")
            parsed = read_cases(path)
        result = evaluate(parsed, "base", bootstrap_replicates=200, seed=5)
        candidate = result["policies"]["candidate"]
        pair = result["paired_vs_baseline"]["candidate"]
        self.assertEqual(candidate["priced_cases"], 1)
        self.assertEqual(candidate["unpriced_cases"], 1)
        self.assertIsNone(candidate["total_cost_usd"])
        self.assertAlmostEqual(candidate["known_total_cost_usd"], 0.2)
        self.assertEqual(candidate["stages"]["model"]["tokens"]["input_tokens"],
                         {"known_total": None, "partial_total": 12, "calls_missing_usage": 1})
        self.assertEqual(pair["paired_priced_cases"], 1)
        cost_ci = pair["paired_bootstrap_95"]["delta_mean_cost_per_case_usd"]
        self.assertEqual(cost_ci["n_paired_priced_cases"], 1)
        self.assertEqual((cost_ci["low"], cost_ci["high"]), (0.1, 0.1))

    def test_cost_per_resolved_case_includes_spend_on_abstained_cases(self):
        rows = [{
            "id": "resolved", "label": "yes",
            "policies": {"p": {"decision": "yes", "cost_usd": 0.01, "latency_ms": 5,
                                "stages": [{"name": "model", "calls": 1, "cost_usd": 0.01, "latency_ms": 5}]}}},
            {"id": "abstained", "label": "no",
             "policies": {"p": {"decision": None, "cost_usd": 0.02, "latency_ms": 6,
                                 "stages": [{"name": "model", "calls": 1, "cost_usd": 0.02, "latency_ms": 6}]}}},
        ]
        summary = evaluate(rows, "p")["policies"]["p"]
        self.assertAlmostEqual(summary["mean_cost_per_case_usd"], 0.015)
        self.assertAlmostEqual(summary["mean_cost_per_resolved_case_usd"], 0.03)


if __name__ == "__main__":
    unittest.main()
