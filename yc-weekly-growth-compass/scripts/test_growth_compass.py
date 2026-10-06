"""Regression tests for period conversion and weekly YC benchmark selection."""
import json
import math
import os
import runpy
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "growth-compass.py"
COMPASS = runpy.run_path(str(SCRIPT))


class GrowthCompassConversionTests(unittest.TestCase):
    def test_weekly_conversion_is_identity(self):
        self.assertEqual(COMPASS["weekly_equivalent"](5.25, "weekly"), 5.25)

    def test_monthly_and_quarterly_conversion_preserve_annual_multiplier(self):
        for period, periods_per_year, rate in (("monthly", 12, 9.375), ("quarterly", 4, 30.0)):
            with self.subTest(period=period):
                weekly_rate = COMPASS["weekly_equivalent"](rate, period)
                self.assertTrue(math.isclose(
                    (1 + weekly_rate / 100) ** 52,
                    (1 + rate / 100) ** periods_per_year,
                    rel_tol=1e-12,
                ))

    def test_zero_and_negative_rates_convert_without_inversion(self):
        weekly = COMPASS["weekly_equivalent"](0, "monthly")
        negative = COMPASS["weekly_equivalent"](-10, "monthly")
        self.assertEqual(weekly, 0)
        self.assertLess(negative, 0)
        self.assertGreater(negative, -100)
        self.assertTrue(math.isclose((1 + negative / 100) ** 52, 0.9 ** 12, rel_tol=1e-12))

    def test_monthly_example_uses_weekly_benchmark_and_assessment(self):
        result = COMPASS["analyze_growth"](35000, previous_value=32000, period="monthly")
        self.assertAlmostEqual(result["growth_rate"]["period_rate_pct"], 9.38)
        self.assertAlmostEqual(result["growth_rate"]["weekly_equivalent_pct"], 2.09, places=2)
        self.assertEqual(result["benchmark"]["label"], "Below Average")
        self.assertEqual(result["benchmark"]["rate_basis"], "weekly_equivalent")
        self.assertIn("2.09% weekly equivalent", result["assessment_text"])
        self.assertIn("weekly benchmark is Below Average", result["assessment_text"])
        self.assertNotIn("good-to-outstanding", result["assessment_text"])

    def test_tier_comparison_rates_are_weekly_thresholds(self):
        result = COMPASS["analyze_growth"](35000, previous_value=32000, period="monthly")
        five_pct_weekly = result["tier_comparison"]["5"]
        self.assertEqual(five_pct_weekly["weekly_rate_pct"], 5)
        self.assertAlmostEqual(five_pct_weekly["period_rate_pct"], 23.54, places=2)
        self.assertEqual(five_pct_weekly["doubling_weeks"], 14.2)

    def test_cli_json_and_human_output_agree_on_weekly_classification(self):
        command = [sys.executable, str(SCRIPT), "--current-value", "35000", "--previous-value", "32000",
                   "--period", "monthly"]
        env = dict(os.environ)
        json_proc = subprocess.run(command + ["--json"], capture_output=True, text=True, env=env, check=True)
        text_proc = subprocess.run(command, capture_output=True, text=True, env=env, check=True)
        result = json.loads(json_proc.stdout)
        self.assertEqual(result["benchmark"]["label"], "Below Average")
        self.assertIn("YC Weekly Tier:", text_proc.stdout)
        self.assertIn("Below Average", text_proc.stdout)
        self.assertIn("2.09%", text_proc.stdout)


if __name__ == "__main__":
    unittest.main()
