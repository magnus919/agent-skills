#!/usr/bin/env python3
"""
Default Alive / Default Dead Calculator

Paul Graham's foundational startup diagnostic: given current revenue, burn rate,
cash on hand, and growth rate, determine whether a startup will reach
profitability before running out of money.

Usage:
  python default-alive.py --monthly-revenue 50000 --monthly-burn 120000 --cash-on-hand 800000 --monthly-growth 8
  python default-alive.py --monthly-revenue 30000 --monthly-burn 75000 --cash-on-hand 500000 --monthly-growth 10 --json
  python default-alive.py --monthly-revenue 50000 --monthly-burn 120000 --cash-on-hand 800000 --monthly-growth 8 --verbose

See SKILL.md for full documentation and methodology.
"""

import argparse
import json
import math
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

MAX_PROJECTION_MONTHS = 120  # 10 years — safety limit
SAFETY_BUFFER_MONTHS = 3     # months of runway required post-breakeven


def project_trajectory(
    monthly_revenue: float,
    monthly_burn: float,
    cash_on_hand: float,
    monthly_growth_pct: float,
    growth_decay_pct: float = 0.5,
    fixed_burn_pct: float = 70.0,
) -> dict:
    """Project month-by-month financial trajectory.

    Parameters
    ----------
    monthly_revenue : Current monthly recurring revenue (MRR)
    monthly_burn : Total monthly operating expenses
    cash_on_hand : Cash reserves
    monthly_growth_pct : Month-over-month revenue growth rate (%)
    growth_decay_pct : Monthly decay in growth rate (%) — models market saturation
    fixed_burn_pct : Percentage of burn that is fixed (vs. variable with revenue)

    Returns
    -------
    dict with trajectory, verdict, and diagnostic metrics
    """
    growth_rate = monthly_growth_pct / 100.0
    decay_rate = growth_decay_pct / 100.0
    fixed_burn = monthly_burn * (fixed_burn_pct / 100.0)
    variable_burn_ratio = (monthly_burn * (1 - fixed_burn_pct / 100.0)) / max(monthly_revenue, 1)

    revenue = monthly_revenue
    cash = cash_on_hand
    peak_revenue = revenue
    current_growth = growth_rate

    trajectory = []
    breakeven_month: Optional[int] = None
    cashout_month: Optional[int] = None

    for month in range(1, MAX_PROJECTION_MONTHS + 1):
        # Revenue grows (or decays) at current growth rate
        revenue = revenue * (1 + current_growth)

        # Growth rate decays toward zero
        current_growth = current_growth * (1 - decay_rate)

        # Burn: fixed component + variable component
        variable_burn = revenue * variable_burn_ratio
        total_burn = fixed_burn + variable_burn

        # Cash flow
        net_cash = revenue - total_burn
        cash += net_cash

        # Track peak revenue for decay modeling
        peak_revenue = max(peak_revenue, revenue)

        entry = {
            "month": month,
            "revenue": round(revenue, 2),
            "burn": round(total_burn, 2),
            "net_cash_flow": round(net_cash, 2),
            "cash": round(cash, 2),
            "growth_rate_pct": round(current_growth * 100, 2),
            "profitable": net_cash >= 0,
        }
        trajectory.append(entry)

        # Track first breakeven month
        if net_cash >= 0 and breakeven_month is None:
            breakeven_month = month

        # Track cash-out month
        if cash <= 0 and cashout_month is None:
            cashout_month = month
            cash = 0  # floor at zero

        # Stop if both conditions are met (or we've run out of cash with no hope)
        if breakeven_month is not None and cashout_month is not None:
            break

        # If we've been unprofitable for 5 years and cash is gone, stop
        if month > 60 and cash <= 0 and net_cash < 0:
            if cashout_month is None:
                cashout_month = month
            break

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    runway_months = cashout_month if cashout_month else MAX_PROJECTION_MONTHS
    net_burn = monthly_burn - monthly_revenue
    burn_multiple = round(net_burn / max(monthly_revenue, 1), 2) if monthly_revenue > 0 else None

    # Net new ARR (monthly growth in ARR terms)
    last_month_revenue = monthly_revenue
    current_arr = monthly_revenue * 12
    if monthly_growth_pct > 0 and monthly_revenue > 0:
        next_arr = (monthly_revenue * (1 + monthly_growth_pct / 100)) * 12
        net_new_arr = next_arr - current_arr
        arr_burn_multiple = round(net_burn / max(net_new_arr, 1), 2) if net_new_arr > 0 else None
    else:
        net_new_arr = 0
        arr_burn_multiple = None

    # Verdict
    if breakeven_month is not None and cashout_month is not None:
        if breakeven_month < cashout_month:
            post_breakeven_runway = cashout_month - breakeven_month
            if post_breakeven_runway >= SAFETY_BUFFER_MONTHS:
                verdict = "ALIVE"
            else:
                verdict = "MARGINAL"
        else:
            verdict = "DEAD"
    elif breakeven_month is not None and cashout_month is None:
        verdict = "ALIVE"
    elif cashout_month is not None and breakeven_month is None:
        verdict = "DEAD"
    else:
        verdict = "MARGINAL"

    # Levers
    levers = []
    if verdict == "DEAD" or verdict == "MARGINAL":
        if monthly_growth_pct < 15:
            levers.append({
                "name": "accelerate-growth",
                "description": "Increasing growth rate to 15%/month would reach breakeven sooner",
                "impact": "high",
            })
        if monthly_burn > monthly_revenue * 2:
            levers.append({
                "name": "reduce-burn",
                "description": "Burn is more than 2x revenue — cost reduction extends runway directly",
                "impact": "high",
            })
        levers.append({
            "name": "fundraising",
            "description": "Default Dead means fundraising is existential, not optional",
            "impact": "critical",
        })
        if monthly_revenue > 0:
            levers.append({
                "name": "pricing",
                "description": "20% price increase with <5% churn impact could shift trajectory significantly",
                "impact": "medium",
            })

    # Monthly gap
    gap_to_breakeven = monthly_burn - monthly_revenue
    months_of_gap = round(cash_on_hand / max(gap_to_breakeven, 1), 1) if gap_to_breakeven > 0 else None

    # ------------------------------------------------------------------
    # Assemble result
    # ------------------------------------------------------------------

    result = {
        "inputs": {
            "monthly_revenue": monthly_revenue,
            "monthly_burn": monthly_burn,
            "cash_on_hand": cash_on_hand,
            "monthly_growth_pct": monthly_growth_pct,
        },
        "diagnostics": {
            "net_monthly_burn": round(net_burn, 2),
            "burn_multiple": burn_multiple,
            "arr_burn_multiple": arr_burn_multiple,
            "current_arr": round(current_arr, 2),
            "net_new_arr": round(net_new_arr, 2),
            "runway_months": runway_months,
            "months_to_breakeven": breakeven_month,
            "cashout_month": cashout_month,
            "gap_to_breakeven": round(gap_to_breakeven, 2),
            "months_of_gap_remaining": months_of_gap,
            "months_projected": len(trajectory),
        },
        "verdict": verdict,
        "explanation": _generate_explanation(
            verdict, runway_months, breakeven_month, cashout_month,
            burn_multiple, arr_burn_multiple, monthly_revenue, monthly_burn,
            cash_on_hand,
        ),
        "levers": levers,
        "trajectory": trajectory if len(trajectory) <= 60 else trajectory[:60],
    }

    return result


def _generate_explanation(
    verdict: str,
    runway_months: int,
    breakeven_month: Optional[int],
    cashout_month: Optional[int],
    burn_multiple: Optional[float],
    arr_burn_multiple: Optional[float],
    monthly_revenue: float,
    monthly_burn: float,
    cash_on_hand: float,
) -> str:
    """Generate plain-English explanation of the verdict."""
    lines = []

    if verdict == "ALIVE":
        lines.append(f"✅ DEFAULT ALIVE — You will reach profitability before running out of cash.")
        if breakeven_month:
            lines.append(f"  Breakeven projected at month {breakeven_month}.")
    elif verdict == "DEAD":
        lines.append(f"❌ DEFAULT DEAD — You will run out of cash before reaching profitability.")
        if cashout_month:
            lines.append(f"  Cash runs out at month {cashout_month}.")
        if breakeven_month:
            lines.append(f"  Breakeven would require {breakeven_month} months — too late.")
    else:
        lines.append(f"⚠️  MARGINAL — Breakeven is possible but dangerously close to cash-out.")
        if breakeven_month and cashout_month:
            lines.append(f"  Breakeven at month {breakeven_month}, cash-out at month {cashout_month}.")
            lines.append(f"  Only {cashout_month - breakeven_month} months of post-breakeven buffer (need {SAFETY_BUFFER_MONTHS}+).")

    lines.append("")
    if burn_multiple is not None:
        lines.append(f"  Burn Multiple: {burn_multiple}x  ({'efficient' if burn_multiple < 2 else 'inefficient' if burn_multiple < 3 else 'critical'})")
    if arr_burn_multiple is not None:
        lines.append(f"  ARR Burn Multiple: {arr_burn_multiple}x  (net burn / net new ARR)")
    lines.append(f"  Runway: {runway_months} months")
    lines.append(f"  Monthly gap: ${monthly_burn - monthly_revenue:,.0f}")
    lines.append(f"  Cash: ${cash_on_hand:,.0f}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def format_output(result: dict, verbose: bool) -> str:
    """Format the result as a human-readable report."""
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append("  DEFAULT ALIVE / DEFAULT DEAD ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    # Inputs
    inputs = result["inputs"]
    lines.append("── Inputs ──────────────────────────────────────────────")
    lines.append(f"  Monthly revenue:     ${inputs['monthly_revenue']:>8,.0f}")
    lines.append(f"  Monthly burn:        ${inputs['monthly_burn']:>8,.0f}")
    lines.append(f"  Cash on hand:        ${inputs['cash_on_hand']:>8,.0f}")
    lines.append(f"  Monthly growth:      {inputs['monthly_growth_pct']:>7.1f}%")
    lines.append("")

    # Verdict
    diag = result["diagnostics"]
    lines.append("── Verdict ─────────────────────────────────────────────")
    lines.append(f"  {result['verdict']}")
    lines.append("")
    lines.append(result["explanation"])
    lines.append("")

    # Diagnostics
    lines.append("── Diagnostics ─────────────────────────────────────────")
    lines.append(f"  Net monthly burn:    ${diag['net_monthly_burn']:>8,.0f}")
    if diag["burn_multiple"] is not None:
        lines.append(f"  Burn Multiple:        {diag['burn_multiple']:>8.2f}x")
    if diag["arr_burn_multiple"] is not None:
        lines.append(f"  ARR Burn Multiple:    {diag['arr_burn_multiple']:>8.2f}x  (net burn ÷ net new ARR)")
    lines.append(f"  Current ARR:         ${diag['current_arr']:>8,.0f}")
    if diag["net_new_arr"]:
        lines.append(f"  Net new ARR/month:   ${diag['net_new_arr']:>8,.0f}")
    lines.append(f"  Runway:               {diag['runway_months']:>8} months")
    lines.append(f"  Months to breakeven:  {diag['months_to_breakeven'] or 'never':>8}")
    if diag["months_of_gap_remaining"]:
        lines.append(f"  Cash gap coverage:    {diag['months_of_gap_remaining']:>8.1f} months at current spend")
    lines.append("")

    # Levers
    if result["levers"]:
        lines.append("── Levers ───────────────────────────────────────────────")
        for lever in result["levers"]:
            icon = {"high": "🔴", "medium": "🟡", "critical": "🚨"}.get(lever["impact"], "⚪")
            lines.append(f"  {icon} {lever['name']}: {lever['description']}")
        lines.append("")

    # Trajectory (verbose only)
    if verbose and result.get("trajectory"):
        lines.append("── Monthly Trajectory ───────────────────────────────────")
        lines.append(f"  {'Mo':>4} {'Revenue':>10} {'Burn':>10} {'Net Cash':>10} {'Cash':>12} {'Growth':>7} {'Prof?':>5}")
        lines.append("  " + "-" * 60)
        for entry in result["trajectory"][:36]:  # First 3 years
            flag = "✓" if entry["profitable"] else "✗"
            lines.append(
                f"  {entry['month']:>4} "
                f"${entry['revenue']:>8,.0f} "
                f"${entry['burn']:>8,.0f} "
                f"${entry['net_cash_flow']:>8,.0f} "
                f"${entry['cash']:>10,.0f} "
                f"{entry['growth_rate_pct']:>5.1f}% "
                f"{flag:>4}"
            )
        if len(result["trajectory"]) > 36:
            lines.append(f"  ... ({len(result['trajectory']) - 36} more months projected)")
        lines.append("")

    lines.append("=" * 60)
    lines.append("  Paul Graham's Default Alive/Dead Framework")
    lines.append("  paulgraham.com/default.html")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Default Alive / Default Dead Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python default-alive.py --monthly-revenue 50000 --monthly-burn 120000 --cash-on-hand 800000 --monthly-growth 8
  python default-alive.py --monthly-revenue 30000 --monthly-burn 75000 --cash-on-hand 500000 --monthly-growth 10 --json
  python default-alive.py --monthly-revenue 50000 --monthly-burn 120000 --cash-on-hand 800000 --monthly-growth 8 --verbose
        """,
    )
    parser.add_argument("--monthly-revenue", type=float, required=True, help="Current monthly recurring revenue")
    parser.add_argument("--monthly-burn", type=float, required=True, help="Total monthly operating expenses")
    parser.add_argument("--cash-on-hand", type=float, required=True, help="Current cash reserves")
    parser.add_argument("--monthly-growth", type=float, required=True, help="Month-over-month revenue growth rate (%)")
    parser.add_argument("--growth-decay", type=float, default=0.5, help="Monthly growth deceleration (%%, default: 0.5)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", action="store_true", help="Show monthly projection")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and show what would be computed")

    args = parser.parse_args()

    # Validate
    if args.monthly_revenue < 0:
        parser.error("monthly-revenue must be >= 0")
    if args.monthly_burn <= 0:
        parser.error("monthly-burn must be > 0")
    if args.cash_on_hand < 0:
        parser.error("cash-on-hand must be >= 0")
    if args.monthly_growth < 0:
        parser.error("monthly-growth must be >= 0")
    if args.growth_decay < 0 or args.growth_decay > 10:
        parser.error("growth-decay should be between 0 and 10")

    if args.dry_run:
        print(json.dumps({
            "status": "valid",
            "inputs": {
                "monthly_revenue": args.monthly_revenue,
                "monthly_burn": args.monthly_burn,
                "cash_on_hand": args.cash_on_hand,
                "monthly_growth": args.monthly_growth,
            },
            "message": "Inputs validated. Run without --dry-run to compute.",
        }, indent=2))
        return

    result = project_trajectory(
        monthly_revenue=args.monthly_revenue,
        monthly_burn=args.monthly_burn,
        cash_on_hand=args.cash_on_hand,
        monthly_growth_pct=args.monthly_growth,
        growth_decay_pct=args.growth_decay,
    )

    if args.json:
        # Strip trajectory unless verbose requested it
        output = result.copy()
        if not args.verbose and "trajectory" in output:
            output["trajectory"] = f"{len(result['trajectory'])} months projected (use --verbose to show)"
        print(json.dumps(output, indent=2))
    else:
        print(format_output(result, verbose=args.verbose))


if __name__ == "__main__":
    main()
