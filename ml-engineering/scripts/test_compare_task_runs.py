"""Challenge incomparable budgets, omitted tasks, dependence and failures."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import compare_task_runs as compare


def record():
    return {
        "schema_version": 1,
        **dict.fromkeys((*compare.PINS, "artifact_sha256"), "a" * 64),
        "expected_case_ids": ["a", "b", "c"],
        "cases": [
            {
                "id": i,
                "group_id": i,
                "status": "failed",
                "critical_failure": False,
                "latency_seconds": n + 1,
            }
            for n, i in enumerate(("a", "b", "c"))
        ],
    }


class ComparisonTests(unittest.TestCase):
    def test_identical_matched_reports(self):
        report = compare.compare(record(), record(), 100)
        self.assertEqual(report["solve_rate_delta"], 0)
        self.assertEqual(report["release"], "not_assessed")
        self.assertEqual(report["uncertainty"]["delta_interval_95"], [0, 0])

    def test_paired_gains_losses_and_timeouts(self):
        left, right = record(), record()
        left["cases"][0]["status"] = "passed"
        right["cases"][1]["status"] = "passed"
        right["cases"][2].update(status="timeout", critical_failure=True)
        report = compare.compare(left, right, 100)
        self.assertEqual((report["paired_gains"], report["paired_losses"]), (1, 1))
        self.assertEqual(report["candidate"]["timeouts"], 1)
        self.assertEqual(report["candidate"]["critical_failures"], 1)
        self.assertAlmostEqual(report["candidate"]["solve_rate"], 1 / 3)

    def test_every_pin_must_match(self):
        for pin in compare.PINS:
            right = record()
            right[pin] = "b" * 64
            report = compare.compare(record(), right, 100)
            self.assertEqual(report["comparison_status"], "inconclusive")
            self.assertNotIn("solve_rate_delta", report)

    def test_omission_infrastructure_and_not_run_block_comparison(self):
        for status in ("infrastructure_error", "not_run", "omit"):
            right = record()
            if status == "omit":
                right["cases"].pop()
            else:
                right["cases"][0].update(status=status, latency_seconds=None)
            self.assertEqual(
                compare.compare(record(), right, 100)["comparison_status"], "inconclusive"
            )

    def test_group_bootstrap_reproducible_and_one_group_unassessed(self):
        left, right = record(), record()
        right["cases"][0]["status"] = "passed"
        self.assertEqual(compare.compare(left, right, 100, 7), compare.compare(left, right, 100, 7))
        for item in (left, right):
            for c in item["cases"]:
                c["group_id"] = "same-repo"
        self.assertEqual(compare.compare(left, right, 100)["uncertainty"]["status"], "not_assessed")

    def test_bad_receipts_rejected(self):
        for change in (
            lambda r: r["cases"].append(copy.deepcopy(r["cases"][0])),
            lambda r: r["cases"][0].update(latency_seconds=float("nan")),
            lambda r: r["cases"][0].update(latency_seconds=True),
            lambda r: r.update(expected_case_ids=[]),
            lambda r: r.pop("budget_sha256"),
        ):
            item = record()
            change(item)
            with self.assertRaises(ValueError):
                compare.validate(item)

    def test_group_mismatch_and_roster_mismatch(self):
        right = record()
        right["cases"][0]["group_id"] = "other"
        self.assertEqual(compare.compare(record(), right, 100)["comparison_status"], "inconclusive")
        right = record()
        right["expected_case_ids"].append("missing")
        self.assertEqual(compare.compare(record(), right, 100)["comparison_status"], "inconclusive")

    def test_cli_fails_under_python_optimized_without_private_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            left, right = Path(tmp) / "a.json", Path(tmp) / "b.json"
            left.write_text(json.dumps(record()))
            item = record()
            item["cases"][0]["status"] = "not_run"
            item["cases"][0]["latency_seconds"] = None
            item["private_text"] = "secret ticket"
            right.write_text(json.dumps(item))
            run = subprocess.run(
                [sys.executable, "-O", str(Path(compare.__file__)), str(left), str(right)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(run.returncode, 1)
            self.assertNotIn("secret", run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
