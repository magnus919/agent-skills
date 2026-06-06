#!/usr/bin/env python3
"""
Weekly Growth Compass

Paul Graham's "Startup = Growth" framework as a CLI tool. Computes weekly
growth rates, benchmarks against YC tiers, projects compound growth over time,
and evaluates whether decisions serve the target growth rate.

Usage:
  python growth-compass.py --current-value 1200 --previous-value 1000 --period weekly
  python growth-compass.py --series "1000,1050,1100,1200,1350" --period weekly
  python growth-compass.py --current-value 35000 --previous-value 32000 --period monthly --metric-name "MRR" --target-revenue 100000
  python growth-compass.py --current-value 1200 --previous-value 1000 --period weekly --json
"""

import argparse
import json
import math
import sys
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# YC Growth Benchmarks
# ---------------------------------------------------------------------------

# Paul Graham's empirical benchmarks from "Startup = Growth" (2012)
# and YC's internal coaching targets during batch programs.

YC_BENCHMARKS = [
    {"min_pct": 10.0, "label": "Outstanding", "color": "🟣",
     "assessment": "Breakout trajectory — extremely rare. This is the Stripe/Coinbase zone."},
    {"min_pct": 7.0, "label": "Very Good", "color": "🟢",
     "assessment": "Exceptional progress. Top quartile of YC companies."},
    {"min_pct": 5.0, "label": "Good", "color": "🟢",
     "assessment": "Solid trajectory. YC's target zone — keep pushing."},
    {"min_pct": 2.0, "label": "Below Average", "color": "🟡",
     "assessment": "Below YC average. Need significant acceleration — likely haven't found product-market fit."},
    {"min_pct": 0.0, "label": "Concerning", "color": "🔴",
     "assessment": "Very low growth. Haven't figured out what you're doing."},
]

# Compound multipliers at various rates
COMPOUND_MULTIPLIERS = {
    1: {"weekly": 1.01, "yearly": 1.68, "label": "Concerning"},
    2: {"weekly": 1.02, "yearly": 2.81, "label": "Below Average"},
    5: {"weekly": 1.05, "yearly": 12.64, "label": "Good"},
    7: {"weekly": 1.07, "yearly": 33.73, "label": "Very Good"},
    10: {"weekly": 1.10, "yearly": 142.04, "label": "Outstanding"},
}


def classify_growth(rate_pct: float) -> dict:
    """Classify a growth rate against YC benchmarks."""
    for bench in YC_BENCHMARKS:
        if rate_pct >= bench["min_pct"]:
            return bench
    return YC_BENCHMARKS[-1]


def period_normalizer(period: str) -> Tuple[str, int]:
    """Return (period_name, periods_per_year) for the given period."""
    period = period.lower()
    mapping = {
        "weekly": ("weekly", 52),
        "monthly": ("monthly", 12),
        "quarterly": ("quarterly", 4),
    }
    if period not in mapping:
        raise ValueError(f"Unknown period: {period}. Must be one of: weekly, monthly, quarterly")
    return mapping[period]


def weekly_equivalent(rate_pct: float, from_period: str) -> float:
    """Convert a growth rate from any period to its weekly equivalent."""
    if from_period == "weekly":
        return rate_pct
    periods_per_year = {"weekly": 52, "monthly": 12, "quarterly": 4}
    n = periods_per_year[from_period]
    # Convert: (1 + r_monthly)^(1/4.33) - 1  ≈ weekly rate
    weekly_rate = (1 + rate_pct / 100) ** (1 / (n / 52)) - 1
    return weekly_rate * 100


# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------


def compute_growth_rate(current: float, previous: float) -> float:
    """Compute growth rate as a percentage."""
    if previous <= 0:
        return 0.0
    return ((current - previous) / previous) * 100


def compute_series_rates(
    values: List[float],
) -> Tuple[List[float], float, float, float]:
    """Compute growth rates from a time series of values.

    Returns
    -------
    (period_rates, mean_rate, median_rate, cwgr)
    where cwgr is the compound weekly growth rate fitted from first to last value.
    """
    if len(values) < 2:
        return [], 0.0, 0.0, 0.0

    rates = []
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            rates.append(((values[i] - values[i - 1]) / values[i - 1]) * 100)

    if not rates:
        return [], 0.0, 0.0, 0.0

    mean_rate = sum(rates) / len(rates)
    sorted_rates = sorted(rates)
    n = len(sorted_rates)
    if n % 2 == 0:
        median_rate = (sorted_rates[n // 2 - 1] + sorted_rates[n // 2]) / 2
    else:
        median_rate = sorted_rates[n // 2]

    # Compound rate from first to last value
    if len(values) >= 2 and values[0] > 0:
        total_growth = values[-1] / values[0]
        cwgr = (total_growth ** (1 / (len(values) - 1)) - 1) * 100
    else:
        cwgr = 0.0

    return rates, mean_rate, median_rate, cwgr


def project_value(
    current: float,
    growth_rate_pct: float,
    periods: int,
) -> float:
    """Project future value given a constant growth rate."""
    return current * ((1 + growth_rate_pct / 100) ** periods)


def doubling_time(growth_rate_pct: float) -> float:
    """Compute the number of periods to double at the given growth rate."""
    if growth_rate_pct <= 0:
        return float("inf")
    return math.log(2) / math.log(1 + growth_rate_pct / 100)


def time_to_target(
    current: float,
    target: float,
    growth_rate_pct: float,
) -> Optional[float]:
    """Compute periods needed to reach target at given growth rate."""
    if current >= target:
        return 0.0
    if growth_rate_pct <= 0:
        return None
    return math.log(target / current) / math.log(1 + growth_rate_pct / 100)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


def analyze_growth(
    current_value: float,
    previous_value: Optional[float] = None,
    series: Optional[List[float]] = None,
    period: str = "weekly",
    project_periods: int = 52,
    target_value: Optional[float] = None,
    metric_name: str = "users/revenue",
) -> dict:
    """Full growth analysis.

    Parameters
    ----------
    current_value : Current period's metric value
    previous_value : Previous period's metric value (optional if series provided)
    series : Full time series of values (optional, overrides previous_value)
    period : 'weekly', 'monthly', or 'quarterly'
    project_periods : Number of periods to project forward (default: 52)
    target_value : Optional target metric to compute time-to-target
    metric_name : Human-readable name for the metric

    Returns
    -------
    dict with all computed fields
    """
    period_name, periods_per_year = period_normalizer(period)

    # Compute rate
    if series and len(series) >= 2:
        rates, mean_rate, median_rate, cwgr = compute_series_rates(series)
        growth_rate = mean_rate if mean_rate != 0 else cwgr
        series_info = {
            "num_data_points": len(series),
            "rates": [round(r, 2) for r in rates],
            "mean_rate": round(mean_rate, 2),
            "median_rate": round(median_rate, 2),
            "cwgr": round(cwgr, 2),
            "first_value": series[0],
            "last_value": series[-1],
        }
    elif previous_value is not None:
        growth_rate = compute_growth_rate(current_value, previous_value)
        series_info = {
            "num_data_points": 2,
            "rate": round(growth_rate, 2),
        }
    else:
        return {"error": "Either --previous-value or --series is required."}

    # Classify
    benchmark = classify_growth(growth_rate)
    weekly_rate = weekly_equivalent(growth_rate, period)
    weekly_benchmark = classify_growth(weekly_rate)

    # Projections
    projected_1yr = project_value(current_value, growth_rate, periods_per_year)
    projected_2yr = project_value(current_value, growth_rate, periods_per_year * 2)
    projected_N = project_value(current_value, growth_rate, project_periods)

    # Doubling and target
    double_p = doubling_time(growth_rate)
    time_to_t = (time_to_target(current_value, target_value, growth_rate)
                 if target_value is not None else None)

    # Growth rate tier table (what other rates would do)
    tier_projections = {}
    for rate_pct in [1, 2, 5, 7, 10]:
        tier_projections[str(rate_pct)] = {
            "label": COMPOUND_MULTIPLIERS.get(rate_pct, {}).get("label", ""),
            "yearly_multiple": round((1 + rate_pct / 100) ** periods_per_year, 2),
            "projected_1yr": round(project_value(current_value, rate_pct, periods_per_year), 2),
            "doubling_periods": round(doubling_time(rate_pct), 1),
        }

    # Assessment text
    if growth_rate >= 5:
        assessment_text = (
            f"At {growth_rate:.1f}% {period_name} growth, you're in YC's good-to-outstanding range. "
            f"Keep pushing — compound growth at this rate transforms the business."
        )
    elif growth_rate >= 2:
        assessment_text = (
            f"At {growth_rate:.1f}% {period_name} growth, you're below YC's target zone. "
            f"Paul Graham's advice: start doing things that don't scale. Recruit users manually, "
            f"delight early customers, measure what works, and compound from there."
        )
    else:
        assessment_text = (
            f"At {growth_rate:.1f}% {period_name} growth, this is concerning. "
            f"You haven't yet figured out what you're doing. Focus on finding something "
            f"that a small number of users genuinely love — then grow from there."
        )

    result = {
        "inputs": {
            "current_value": current_value,
            "previous_value": previous_value,
            "metric_name": metric_name,
            "period": period_name,
            "project_periods": project_periods,
            "target_value": target_value,
        },
        "series_info": series_info,
        "growth_rate": {
            "period_rate_pct": round(growth_rate, 2),
            "weekly_equivalent_pct": round(weekly_rate, 2),
            "period_name": period_name,
        },
        "benchmark": {
            "label": benchmark["label"],
            "icon": benchmark["color"],
            "assessment": benchmark["assessment"],
            "weekly_benchmark_label": weekly_benchmark["label"],
        },
        "projections": {
            f"projected_{project_periods}_periods": round(projected_N, 2),
            "projected_1_year": round(projected_1yr, 2),
            "projected_2_years": round(projected_2yr, 2),
            "doubling_time_periods": round(double_p, 1),
            "time_to_target_periods": round(time_to_t, 1) if time_to_t is not None else None,
            "target_value": target_value,
        },
        "tier_comparison": tier_projections,
        "assessment_text": assessment_text,
    }

    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_output(result: dict) -> str:
    """Format the analysis as a human-readable report."""
    if "error" in result:
        return f"Error: {result['error']}"

    lines = []
    inputs = result["inputs"]
    rate = result["growth_rate"]
    bench = result["benchmark"]
    proj = result["projections"]
    series = result["series_info"]

    # Header
    lines.append("=" * 60)
    lines.append(f"  WEEKLY GROWTH COMPASS — {bench['icon']} {bench['label']}")
    lines.append("=" * 60)
    lines.append("")

    # Inputs
    lines.append("── Inputs ──────────────────────────────────────────────")
    lines.append(f"  Metric:         {inputs['metric_name']}")
    lines.append(f"  Current value:  {inputs['current_value']:>10,.0f}")
    if inputs.get("previous_value"):
        lines.append(f"  Previous value: {inputs['previous_value']:>10,.0f}")
    lines.append(f"  Period:         {inputs['period']}")
    lines.append(f"  Data points:    {series.get('num_data_points', 2)}")
    lines.append("")

    # Growth rate
    lines.append("── Growth Rate ──────────────────────────────────────────")
    lines.append(f"  Period growth:  {rate['period_rate_pct']:>7.2f}% ({rate['period_name']})")
    lines.append(f"  Weekly equiv:   {rate['weekly_equivalent_pct']:>7.2f}%")
    lines.append(f"  YC Benchmark:   {bench['icon']} {bench['label']}")
    lines.append("")

    if series.get("rates"):
        rates = series["rates"]
        lines.append(f"  Period-over-period rates:")
        for i, r in enumerate(rates):
            arrows = "↑" if r > 0 else "↓" if r < 0 else "→"
            lines.append(f"    Period {i+1}-{i+2}: {r:>6.2f}% {arrows}")
        lines.append(f"  Mean rate:      {series['mean_rate']:>7.2f}%")
        lines.append(f"  Median rate:    {series['median_rate']:>7.2f}%")
        lines.append(f"  CWGR:           {series['cwgr']:>7.2f}% (compound from first to last)")
        lines.append("")

    # Assessment
    lines.append("── Assessment ───────────────────────────────────────────")
    lines.append(f"  {result['assessment_text']}")
    lines.append("")

    # Projections
    lines.append("── Projections ─────────────────────────────────────────")
    lines.append(f"  Doubling time:     {proj['doubling_time_periods']:>7.1f} {rate['period_name']} periods")
    lines.append(f"  Projected 1 year:  {proj['projected_1_year']:>10,.0f}")
    lines.append(f"  Projected 2 years: {proj['projected_2_years']:>10,.0f}")
    if proj.get("time_to_target_periods") is not None and proj.get("target_value"):
        lines.append(f"  Time to target:    {proj['time_to_target_periods']:>7.1f} {rate['period_name']} periods")
        lines.append(f"  Target value:      {proj['target_value']:>10,.0f}")
    lines.append("")

    # Tier comparison
    lines.append("── Growth Rate Comparison ──────────────────────────────")
    lines.append(f"  {'Rate':>6} {'Label':>18} {'1-Year Multiple':>18} {'1-Year Value':>16} {'Double In':>12}")
    lines.append(f"  {'-'*6} {'-'*18} {'-'*18} {'-'*16} {'-'*12}")
    for rate_pct_str, tier in result["tier_comparison"].items():
        rate_pct = int(rate_pct_str)
        marker = "◀" if rate_pct == round(rate["period_rate_pct"]) else ""
        lines.append(
            f"  {rate_pct:>5}% {tier['label']:>18} "
            f"{tier['yearly_multiple']:>17.1f}x "
            f"{tier['projected_1yr']:>14,.0f} "
            f"{tier['doubling_periods']:>7.1f}p  {marker}"
        )
    lines.append("")

    # Compass question
    lines.append("── The Compass Question ────────────────────────────────")
    lines.append(f"  Your target growth rate: {rate['period_rate_pct']:.1f}% {rate['period_name']}")
    lines.append(f"  For every decision this week, ask:")
    lines.append(f"  \"Does this serve our {rate['period_rate_pct']:.1f}% {rate['period_name']} growth target?\"")
    lines.append(f"  If yes → do it. If no → defer it.")
    lines.append("")
    lines.append(f"  At end of week, measure actual growth against target.")
    lines.append(f"  If you missed, something else matters more than what you did.")

    lines.append("")
    lines.append("=" * 60)
    lines.append("  Paul Graham, \"Startup = Growth\" (September 2012)")
    lines.append("  paulgraham.com/growth.html")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Weekly Growth Compass — YC's growth rate framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python growth-compass.py --current-value 1200 --previous-value 1000 --period weekly
  python growth-compass.py --series "1000,1050,1100,1200,1350" --period weekly
  python growth-compass.py --current-value 35000 --previous-value 32000 --period monthly --metric-name "MRR" --target-revenue 100000
  python growth-compass.py --current-value 1200 --previous-value 1000 --period weekly --json
        """,
    )
    parser.add_argument("--current-value", type=float, help="Current period metric value")
    parser.add_argument("--previous-value", type=float, help="Previous period metric value")
    parser.add_argument("--series", type=str, help="Comma-separated time series (overrides --current/--previous)")
    parser.add_argument("--period", type=str, default="weekly", choices=["weekly", "monthly", "quarterly"],
                        help="Period type (default: weekly)")
    parser.add_argument("--project-periods", type=int, default=52,
                        help="Periods to project forward (default: 52)")
    parser.add_argument("--target-value", type=float, help="Target metric value to compute time-to-target")
    parser.add_argument("--metric-name", type=str, default="users/revenue",
                        help="Human-readable metric name (default: 'users/revenue')")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and show what would be computed")

    args = parser.parse_args()

    # Parse series if provided
    series = None
    if args.series:
        try:
            series = [float(x.strip()) for x in args.series.split(",")]
        except ValueError:
            parser.error("--series must be comma-separated numbers")
        if len(series) < 2:
            parser.error("--series must have at least 2 values")

    # Validate
    if not series and args.current_value is None:
        parser.error("Either --current-value (with --previous-value) or --series is required")
    if not series and args.previous_value is None:
        parser.error("--previous-value is required when using --current-value")
    if args.current_value is not None and args.current_value < 0:
        parser.error("--current-value must be >= 0")
    if args.previous_value is not None and args.previous_value < 0:
        parser.error("--previous-value must be >= 0")
    if args.target_value is not None and args.target_value < 0:
        parser.error("--target-value must be >= 0")
    if args.project_periods < 1:
        parser.error("--project-periods must be >= 1")

    if args.dry_run:
        if series:
            print(json.dumps({
                "status": "valid",
                "data_points": len(series),
                "first_value": series[0],
                "last_value": series[-1],
                "period": args.period,
            }, indent=2))
        else:
            print(json.dumps({
                "status": "valid",
                "current_value": args.current_value,
                "previous_value": args.previous_value,
                "period": args.period,
            }, indent=2))
        return

    current_val: float = series[-1] if series else (args.current_value or 0.0)
    result = analyze_growth(
        current_value=current_val,
        previous_value=args.previous_value,
        series=series,
        period=args.period,
        project_periods=args.project_periods,
        target_value=args.target_value,
        metric_name=args.metric_name,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
