---
name: yc-default-alive-calculator
description: >-
  Evaluate whether a startup is on a trajectory to profitability before running
  out of cash — Paul Graham's "Default Alive / Default Dead" framework. Takes
  revenue, burn rate, cash on hand, and growth rate; computes runway, burn
  multiple, and months to breakeven. Ships a deterministic CLI calculator.
  Load when founders ask about runway, burn rate, default alive, whether they
  need to raise money, or financial sustainability analysis.
license: MIT
compatibility: Python 3.9+ with standard library only (no external dependencies).
  The default-alive.py script uses only math, json, and sys.
metadata:
  spec-version: "1.0"
  tags: [startup-finance, runway-analysis, ycombinator, paul-graham, fundraising,
         financial-modeling, default-alive, burn-rate, startup-metrics]
  sources:
    - https://paulgraham.com/default.html
    - https://paulgraham.com/die.html
    - https://www.ycombinator.com/about
  skills: [yc-weekly-growth-compass]
  requires-toolsets: [terminal]
---

# Default Alive / Default Dead Calculator

A startup is "default alive" if its current revenue trajectory will reach profitability before it runs out of cash — without additional funding. It is "default dead" if it will run out of money first. This is the single most important financial diagnostic Paul Graham developed at Y Combinator.

**This is not a fundraising model.** It's a reality check. The answer determines whether fundraising is optional or existential.

## When to Load

| Trigger | Example |
|---------|---------|
| "Am I default alive?" | Founder asking about runway |
| "How much runway do I have?" | Financial planning |
| "Should I raise money?" | Strategic decision |
| "What's my burn multiple?" | Investor-ready metrics |
| "How long until we break even?" | Trajectory check |
| "Default alive/dead analysis" | Explicit framework request |

## How to Use

### Quick Answer (No Script)

For a quick check without running the calculator, use the simplified heuristic:

```
Burn Multiple = Net Burn / Net New ARR
```

| Burn Multiple | Signal |
|--------------|--------|
| < 1x | Default Alive — growing efficiently |
| 1x–2x | Healthy — capital-efficient growth |
| 2x–3x | Warning — burning faster than growing |
| 3x+ | Default Dead — cash crisis without funding |

### Full Analysis (Script)

Run the CLI calculator for a precise analysis:

```bash
python scripts/default-alive.py \
  --monthly-revenue 50000 \
  --monthly-burn 120000 \
  --cash-on-hand 800000 \
  --monthly-growth 8
```

Output shows: runway (months), burn multiple, months to breakeven extrapolated, default alive/dead verdict, and the key levers available.

#### Required inputs

| Flag | Description | Example |
|------|-------------|---------|
| `--monthly-revenue` | Current monthly recurring revenue (MRR) | `50000` |
| `--monthly-burn` | Total monthly operating expenses | `120000` |
| `--cash-on-hand` | Cash remaining in bank account | `800000` |
| `--monthly-growth` | Month-over-month revenue growth rate (%) | `8` |

#### Optional inputs

| Flag | Description | Example |
|------|-------------|---------|
| `--revenue-growth-deceleration` | Annual growth deceleration rate (%/month, default: 0.5) | `0.3` |
| `--json` | Machine-readable JSON output | |
| `--verbose` | Show detailed month-by-month projection | |

#### Output fields

| Field | Meaning |
|-------|---------|
| `runway_months` | Months until cash runs out (at current burn) |
| `burn_multiple` | Net burn ÷ net new ARR |
| `months_to_breakeven` | Months until revenue ≥ expenses (extrapolated) |
| `default_verdict` | `ALIVE`, `DEAD`, or `MARGINAL` |
| `revenue_at_breakeven` | Projected revenue when/if breakeven reached |
| `gap_to_breakeven` | Monthly shortfall remaining |
| `levers` | What can change the outcome (increase price, cut costs, etc.) |

## Methodology

### The Core Calculation

The model projects month-by-month:

```
month_n_revenue = previous_revenue × (1 + growth_rate/100)
month_n_burn = fixed_burn + (variable_burn_ratio × month_n_revenue)
month_n_cash = previous_cash + month_n_revenue - month_n_burn
```

Growth rate decays over time (default: 0.5% per month) to model market saturation — startups don't grow at a constant rate forever.

### Default Alive Test

The startup is **Default Alive** if:
```
projected_revenue > projected_expenses
```
at some point *before* cumulative cash goes negative, *and* the crossover happens with at least 3 months of remaining runway (safety buffer).

It is **Default Dead** if cash runs out first.

It is **Marginal** if breakeven happens with less than 3 months of runway remaining — technically possible but dangerously tight.

### Burn Multiple

A metric Graham began tracking at YC to measure capital efficiency:

```
Burn Multiple = Net Burn / Net New ARR
```

Where:
- Net Burn = cash spent per month (total expenses minus revenue)
- Net New ARR = new annual recurring revenue added that month

A burn multiple below 1x means the company is generating more than it spends in new ARR terms — the strongest default-alive signal.

## Levers

When the verdict is DEAD or MARGINAL, evaluate these levers (in rough order of impact):

1. **Revenue growth** — 10% faster growth compounds dramatically over 18 months
2. **Cost reduction** — Every dollar cut extends runway by one dollar
3. **Pricing** — A 20% price increase with minimal churn impact is often the fastest lever
4. **Gross margin** — Reducing COGS improves unit economics without topline change
5. **Funding** — Default dead means fundraising is existential, not optional

## Examples

### YC Typical Profile (Default Alive)

```bash
python scripts/default-alive.py \
  --monthly-revenue 30000 \
  --monthly-burn 75000 \
  --cash-on-hand 500000 \
  --monthly-growth 10
```

- Runway: ~11 months
- Burn multiple: 1.5x
- Breakeven: ~14 months (3 months short on runway → MARGINAL)
- Verdict: **MARGINAL** — needs faster growth, cost cuts, or funding

### Pre-Revenue Startup (Default Dead)

```bash
python scripts/default-alive.py \
  --monthly-revenue 0 \
  --monthly-burn 80000 \
  --cash-on-hand 400000 \
  --monthly-growth 0
```

- Runway: 5 months
- Burn multiple: undefined (no revenue)
- Verdict: **DEAD** — fundraising is existential

### Capital-Efficient SaaS (Default Alive)

```bash
python scripts/default-alive.py \
  --monthly-revenue 150000 \
  --monthly-burn 180000 \
  --cash-on-hand 2000000 \
  --monthly-growth 7
```

- Runway: ~66 months (effectively infinite)
- Burn multiple: 0.2x
- Breakeven: ~3 months
- Verdict: **ALIVE**

## References

- `references/default-alive-framework.md` — Paul Graham's original framework with essay excerpts
- `references/yc-fundraising-context.md` — How default state drives fundraising strategy
- `yc-weekly-growth-compass` companion skill — For growth rate analysis
