# Financial Modeling

Build clearer financial scenarios, pricing decisions, and operating-metric analyses from stated assumptions.

## Why Install This Skill

Business decisions often depend on numbers that look precise but rest on hidden assumptions. This skill gives your agent a practical method for making revenue, costs, cash, customer economics, and SaaS metrics explicit so you can test what changes when the assumptions change.

It covers the questions teams repeatedly face: whether acquisition pays back, what a price change could do to retention, how long cash may last under different cases, and how to prepare a financing model or cap-table discussion. The material emphasizes traceable calculations and context rather than universal scorecards.

It is an analytical aid, not financial, investment, tax, accounting, or legal advice. Use qualified professionals where those disciplines are required.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Scope, trigger boundaries, and a concise assumptions-led working method. |
| `references/financial-modeling.md` | Linked statements, revenue and cost drivers, scenarios, and runway analysis. |
| `references/unit-economics.md` | CAC, LTV, payback, contribution margin, and segmentation guidance. |
| `references/pricing-strategy.md` | Pricing models, packaging, price-change tests, and trade-off analysis. |
| `references/fundraising.md` | Valuation methods, cap tables, term-sheet concepts, and fundraising preparation. |
| `references/saas-metrics.md` | ARR, retention, efficiency metrics, period alignment, and metric limitations. |
| `references/source-index.md` | Source provenance, review date, and authoritative reference links. |
| `templates/` | Fillable records: unit-economics record, pricing decision record, fundraising scenario, and model sanity checklist. |
| `scripts/` | `saas-metrics.py` — computes ARR, monthly and annualized logo churn, NDR, and Rule of 40 from stated inputs. |
| `evals/` | Output-quality eval manifest for the skill's methodology cases. |

## Quick Start

Compute the headline SaaS operating metrics in one command. The script needs only Python 3 (standard library) and takes stated inputs, so the same numbers you would put in a spreadsheet produce a consistent result:

```bash
python3 financial-modeling/scripts/saas-metrics.py \
  --mrr 120000 --customers 480 --churned-customers 10 \
  --expansion 9000 --contraction 3000 --churned-mrr 4200 \
  --growth-pct 38 --margin-pct 6
```

Output:

```text
ARR (annualized recurring revenue): $1,440,000.00
Monthly logo churn: 2.08%
Annualized logo churn: 22.33%
NDR (net dollar retention): 101.50%
Rule of 40 (growth + margin): 44.00
```

Add `--json` for machine-readable output, pass `--churn-pct 2.1` instead of customer counts when churn is already known, and omit the `--expansion`/`--contraction`/`--churned-mrr` group (or the growth/margin pair) when those metrics are not in scope. The script exits 2 on inconsistent inputs, so it can gate a report or CI step. Load `SKILL.md` for the methodology and reference table, then use the templates to record unit economics, pricing decisions, fundraising scenarios, or a model sanity check.

## Triggers

- Build or review a financial model, forecast, budget, scenario, or runway analysis.
- Calculate CAC, LTV, payback, contribution margin, ARR, churn, NDR, Rule of 40, Magic Number, or burn multiple.
- Evaluate a pricing change, packaging model, fundraising scenario, cap table, valuation method, or term-sheet concept.

## Requirements

No API keys or credentials. The `saas-metrics.py` script needs only Python 3 (standard library). Useful analysis requires reliable business inputs with a defined currency, time period, and accounting basis.

## Source and Maintenance

This skill was ported from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). See [`references/source-index.md`](references/source-index.md) for the portability boundary and source review details.
