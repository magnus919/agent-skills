#!/usr/bin/env python3
"""SaaS operating-metrics calculator for financial-modeling.

Computes the headline SaaS operating metrics from stated inputs:

  ARR        = monthly recurring revenue x 12
  logo churn = monthly rate (customers churned / starting customers, or given
               directly as a percentage), annualized as 1 - (1 - monthly)^12
  NDR        = (starting MRR + expansion - contraction - churned MRR)
               / starting MRR
  Rule of 40 = revenue growth rate (%) + profit margin (%)

The tool is a computation aid, not financial advice. Every result is only as
trustworthy as the input definitions and period alignment: state the revenue
definition, customer population, and period for each input before acting on a
number. All monetary inputs are in the same currency and period.

Exit codes:
  0  success
  2  usage or validation error
"""

import argparse
import json
import sys

ANNUAL_MONTHS = 12


def annualize_monthly_rate(monthly_fraction):
    """Annualize a stable monthly rate: 1 - (1 - monthly) ** 12."""
    return 1.0 - (1.0 - monthly_fraction) ** ANNUAL_MONTHS


def compute_metrics(
    mrr,
    customers=None,
    churned_customers=None,
    churn_pct=None,
    expansion=None,
    contraction=None,
    churned_mrr=None,
    growth_pct=None,
    margin_pct=None,
):
    """Compute the requested SaaS metrics from validated inputs."""
    metrics = {"mrr": mrr, "arr": mrr * ANNUAL_MONTHS}

    if churn_pct is not None:
        monthly_fraction = churn_pct / 100.0
        metrics["churn_source"] = "churn-pct"
    elif customers is not None and churned_customers is not None:
        monthly_fraction = churned_customers / customers
        metrics["churn_source"] = "customers"
    else:
        monthly_fraction = None

    if monthly_fraction is not None:
        metrics["monthly_logo_churn_pct"] = round(monthly_fraction * 100.0, 4)
        metrics["annualized_logo_churn_pct"] = round(
            annualize_monthly_rate(monthly_fraction) * 100.0, 4
        )

    if expansion is not None:
        ndr = (mrr + expansion - contraction - churned_mrr) / mrr
        metrics["ndr_pct"] = round(ndr * 100.0, 4)

    if growth_pct is not None and margin_pct is not None:
        metrics["rule_of_40"] = round(growth_pct + margin_pct, 4)

    return metrics


def build_parser():
    parser = argparse.ArgumentParser(
        prog="saas-metrics.py",
        description=(
            "Compute SaaS operating metrics from stated inputs: ARR (monthly recurring "
            "revenue annualized), monthly and annualized logo churn, net dollar "
            "retention (NDR), and the Rule of 40 (revenue growth plus profit margin). "
            "Exit 0 on success, 2 on usage or validation errors."
        ),
        epilog=(
            "Example: python3 saas-metrics.py --mrr 120000 --customers 480 "
            "--churned-customers 10 --expansion 9000 --contraction 3000 "
            "--churned-mrr 4200 --growth-pct 38 --margin-pct 6 --json"
        ),
    )
    parser.add_argument(
        "--mrr",
        type=float,
        required=True,
        metavar="AMOUNT",
        help="starting monthly recurring revenue, the basis for ARR and NDR (required)",
    )
    churn_group = parser.add_mutually_exclusive_group()
    churn_group.add_argument(
        "--churn-pct",
        type=float,
        metavar="PCT",
        help="monthly logo churn rate as a percentage, e.g. 2.1 for 2.1%%",
    )
    churn_group.add_argument(
        "--churned-customers",
        type=float,
        metavar="COUNT",
        help="customers churned in the period (requires --customers)",
    )
    parser.add_argument(
        "--customers",
        type=float,
        metavar="COUNT",
        help="starting customer count, the denominator for monthly logo churn",
    )
    parser.add_argument(
        "--expansion",
        type=float,
        metavar="AMOUNT",
        help="expansion (upsell) revenue in the period, for NDR",
    )
    parser.add_argument(
        "--contraction",
        type=float,
        metavar="AMOUNT",
        help="contraction (downgrade) revenue in the period, for NDR",
    )
    parser.add_argument(
        "--churned-mrr",
        type=float,
        metavar="AMOUNT",
        help="recurring revenue lost to churn in the period, for NDR",
    )
    parser.add_argument(
        "--growth-pct",
        type=float,
        metavar="PCT",
        help="recurring revenue growth rate as a percentage, for Rule of 40",
    )
    parser.add_argument(
        "--margin-pct",
        type=float,
        metavar="PCT",
        help="profit margin (EBITDA or free cash flow) as a percentage, for Rule of 40",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    return parser


def validate_inputs(args):
    """Return an error message, or None when the inputs are consistent."""
    if args.mrr < 0:
        return "--mrr must be non-negative"

    if args.churn_pct is not None:
        if not 0 <= args.churn_pct <= 100:
            return "--churn-pct must be between 0 and 100"
    elif args.churned_customers is not None or args.customers is not None:
        if args.churned_customers is None or args.customers is None:
            return "--churned-customers and --customers must be provided together"
        if args.customers <= 0:
            return "--customers must be positive"
        if args.churned_customers < 0 or args.churned_customers > args.customers:
            return "--churned-customers must be between 0 and --customers"

    ndr_inputs = (args.expansion, args.contraction, args.churned_mrr)
    if any(value is not None for value in ndr_inputs):
        if not all(value is not None for value in ndr_inputs):
            return "--expansion, --contraction, and --churned-mrr must be provided together"
        if any(value < 0 for value in ndr_inputs):
            return "NDR components must be non-negative"
        if args.mrr == 0:
            return "NDR requires --mrr greater than 0"
        if args.churned_mrr > args.mrr:
            return "--churned-mrr cannot exceed --mrr"

    if (args.growth_pct is None) != (args.margin_pct is None):
        return "--growth-pct and --margin-pct must be provided together"

    return None


def build_report(args, metrics):
    inputs = {
        "mrr": args.mrr,
        "customers": args.customers,
        "churned_customers": args.churned_customers,
        "churn_pct": args.churn_pct,
        "expansion": args.expansion,
        "contraction": args.contraction,
        "churned_mrr": args.churned_mrr,
        "growth_pct": args.growth_pct,
        "margin_pct": args.margin_pct,
    }
    return {"tool": "saas-metrics.py", "inputs": inputs, "metrics": metrics}


def format_money(value):
    return f"${value:,.2f}"


def print_human(report):
    metrics = report["metrics"]
    print(f"ARR (annualized recurring revenue): {format_money(metrics['arr'])}")
    if "monthly_logo_churn_pct" in metrics:
        print(f"Monthly logo churn: {metrics['monthly_logo_churn_pct']:.2f}%")
        print(f"Annualized logo churn: {metrics['annualized_logo_churn_pct']:.2f}%")
    if "ndr_pct" in metrics:
        print(f"NDR (net dollar retention): {metrics['ndr_pct']:.2f}%")
    if "rule_of_40" in metrics:
        print(f"Rule of 40 (growth + margin): {metrics['rule_of_40']:.2f}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    error = validate_inputs(args)
    if error is not None:
        parser.error(error)

    metrics = compute_metrics(
        mrr=args.mrr,
        customers=args.customers,
        churned_customers=args.churned_customers,
        churn_pct=args.churn_pct,
        expansion=args.expansion,
        contraction=args.contraction,
        churned_mrr=args.churned_mrr,
        growth_pct=args.growth_pct,
        margin_pct=args.margin_pct,
    )
    report = build_report(args, metrics)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
