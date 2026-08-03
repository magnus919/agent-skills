"""Tests for saas-metrics.py.

Covers: ARR derivation from MRR, monthly and annualized logo churn from
customers, churn from a direct percentage, NDR computation, Rule of 40,
JSON report shape, churn/NDR omitted when inputs are absent, validation
errors (exit 2), and --help.

Discoverable by both pytest and unittest (unittest.TestCase classes) and
runnable standalone: python3 financial-modeling/scripts/test_saas_metrics.py
"""

import importlib.util
import json
import os
import subprocess
import sys
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(SCRIPTS_DIR, "saas-metrics.py")


def load_module():
    """Load saas-metrics.py (hyphenated name is not importable directly)."""
    spec = importlib.util.spec_from_file_location("saas_metrics_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


saas_metrics = load_module()


def run_script(args):
    proc = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestCliBasics(unittest.TestCase):
    def test_help_exits_zero_and_covers_metrics(self):
        rc, stdout, _ = run_script(["--help"])
        self.assertEqual(rc, 0)
        lowered = stdout.lower()
        for term in ("arr", "churn", "ndr", "rule of 40"):
            self.assertIn(term, lowered, f"--help must mention {term}")

    def test_mrr_is_required(self):
        rc, _, stderr = run_script([])
        self.assertEqual(rc, 2)
        self.assertIn("--mrr", stderr)

    def test_full_report_human_readable(self):
        rc, stdout, _ = run_script(
            [
                "--mrr", "120000",
                "--customers", "480",
                "--churned-customers", "10",
                "--expansion", "9000",
                "--contraction", "3000",
                "--churned-mrr", "4200",
                "--growth-pct", "38",
                "--margin-pct", "6",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertIn("ARR (annualized recurring revenue): $1,440,000.00", stdout)
        self.assertIn("Monthly logo churn: 2.08%", stdout)
        self.assertIn("NDR (net dollar retention): 101.50%", stdout)
        self.assertIn("Rule of 40 (growth + margin): 44.00", stdout)


class TestComputeMetrics(unittest.TestCase):
    def test_arr_is_mrr_times_twelve(self):
        metrics = saas_metrics.compute_metrics(mrr=100000)
        self.assertEqual(metrics["arr"], 1200000)
        self.assertEqual(metrics["mrr"], 100000)

    def test_churn_from_customers(self):
        metrics = saas_metrics.compute_metrics(
            mrr=100000, customers=400, churned_customers=20
        )
        self.assertAlmostEqual(metrics["monthly_logo_churn_pct"], 5.0, places=4)

    def test_annualized_churn_matches_compounding(self):
        metrics = saas_metrics.compute_metrics(
            mrr=100000, customers=1000, churned_customers=10
        )
        expected = (1 - (1 - 0.01) ** 12) * 100
        self.assertAlmostEqual(metrics["annualized_logo_churn_pct"], expected, places=4)

    def test_churn_from_direct_percentage(self):
        metrics = saas_metrics.compute_metrics(mrr=100000, churn_pct=2.1)
        self.assertAlmostEqual(metrics["monthly_logo_churn_pct"], 2.1, places=4)

    def test_ndr_uses_expansion_contraction_churn(self):
        metrics = saas_metrics.compute_metrics(
            mrr=120000, expansion=9000, contraction=3000, churned_mrr=4200
        )
        self.assertAlmostEqual(metrics["ndr_pct"], 101.5, places=4)

    def test_rule_of_40_sums_growth_and_margin(self):
        metrics = saas_metrics.compute_metrics(mrr=100000, growth_pct=38, margin_pct=-4)
        self.assertAlmostEqual(metrics["rule_of_40"], 34.0, places=4)

    def test_churn_omitted_when_no_churn_inputs(self):
        metrics = saas_metrics.compute_metrics(mrr=100000)
        self.assertNotIn("monthly_logo_churn_pct", metrics)
        self.assertNotIn("annualized_logo_churn_pct", metrics)

    def test_ndr_omitted_when_no_ndr_inputs(self):
        metrics = saas_metrics.compute_metrics(mrr=100000)
        self.assertNotIn("ndr_pct", metrics)


class TestJsonOutput(unittest.TestCase):
    def test_json_report_shape(self):
        rc, stdout, _ = run_script(
            ["--mrr", "50000", "--churn-pct", "1", "--growth-pct", "30",
             "--margin-pct", "10", "--json"]
        )
        self.assertEqual(rc, 0)
        report = json.loads(stdout)
        self.assertEqual(report["tool"], "saas-metrics.py")
        self.assertEqual(report["inputs"]["mrr"], 50000.0)
        self.assertEqual(report["metrics"]["arr"], 600000.0)
        self.assertAlmostEqual(report["metrics"]["monthly_logo_churn_pct"], 1.0)
        self.assertAlmostEqual(report["metrics"]["rule_of_40"], 40.0)
        self.assertNotIn("ndr_pct", report["metrics"])


class TestValidationErrors(unittest.TestCase):
    def test_negative_mrr_rejected(self):
        rc, _, stderr = run_script(["--mrr", "-1"])
        self.assertEqual(rc, 2)
        self.assertIn("--mrr", stderr)

    def test_churned_exceeding_customers_rejected(self):
        rc, _, stderr = run_script(
            ["--mrr", "10000", "--customers", "10", "--churned-customers", "11"]
        )
        self.assertEqual(rc, 2)
        self.assertIn("--churned-customers", stderr)

    def test_partial_ndr_inputs_rejected(self):
        rc, _, stderr = run_script(["--mrr", "10000", "--expansion", "500"])
        self.assertEqual(rc, 2)
        self.assertIn("--expansion", stderr)

    def test_partial_rule_of_40_rejected(self):
        rc, _, stderr = run_script(["--mrr", "10000", "--growth-pct", "30"])
        self.assertEqual(rc, 2)
        self.assertIn("--growth-pct", stderr)

    def test_churned_mrr_above_mrr_rejected(self):
        rc, _, stderr = run_script(
            ["--mrr", "10000", "--expansion", "0", "--contraction", "0",
             "--churned-mrr", "12000"]
        )
        self.assertEqual(rc, 2)
        self.assertIn("--churned-mrr", stderr)

    def test_customers_without_churned_rejected(self):
        rc, _, stderr = run_script(["--mrr", "10000", "--customers", "100"])
        self.assertEqual(rc, 2)
        self.assertIn("--customers", stderr)


if __name__ == "__main__":
    unittest.main()
