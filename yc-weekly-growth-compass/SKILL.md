---
name: yc-weekly-growth-compass
description: Paul Graham's "Startup = Growth" framework as an operational tool. Computes
  weekly growth rates, benchmarks against YC tiers (1% concerning, 5-7% good, 10%+
  exceptional), projects compound growth over time, and frames every startup decision
  through the question "does this serve your target growth rate?" Ships a deterministic
  CLI calculator. Load when founders ask about growth rate, weekly growth, startup
  traction, metrics, or whether they're moving fast enough.
license: MIT
compatibility: Python 3.9+ with standard library only (no external dependencies).
  The growth-compass.py script uses only math, json, and sys.
metadata:
  spec-version: '1.0'
  tags: startup-growth, growth-rate, ycombinator, paul-graham, startup-metrics, weekly-growth,
    traction, compound-growth, startup-compass
  sources: https://paulgraham.com/growth.html, https://paulgraham.com/ds.html, https://www.ycombinator.com/about
  skills: yc-default-alive-calculator
  requires-toolsets: terminal
---

# Weekly Growth Compass

> "If there's one number every founder should always know, it's the company's growth rate. That's the measure of a startup. If you don't know that number, you don't even know if you're doing well or badly."
> — Paul Graham, "Startup = Growth" (September 2012)

This skill operationalizes Y Combinator's core growth philosophy into a repeatable weekly practice. The growth rate is not just a metric — it's a **compass** for every decision a founder makes.

## When to Load

| Trigger | Example |
|---------|---------|
| "What's my growth rate?" | Routine founder check-in |
| "Are we growing fast enough?" | Trajectory anxiety |
| "Should we prioritize feature X or growth Y?" | Decision framing |
| "Where will we be in a year?" | Projection/planning |
| "How does our growth compare to YC benchmarks?" | Benchmarking |
| "Is this initiative worth doing?" | Growth compass check |
| "How long to double our revenue?" | Milestone planning |

## How to Use

### Quick Rule of Thumb (No Script)

YC's empirical benchmarks, based on measuring thousands of startups:

| Weekly Growth | Annualized | YC Assessment |
|--------------|------------|---------------|
| 1% | 1.7x | Concerning — haven't found product-market fit |
| 2% | 2.8x | Below average — need significant acceleration |
| 5% | 12.6x | **Good** — solid trajectory, keep pushing |
| 7% | 33.7x | **Very good** — exceptional progress |
| 10% | 142.0x | **Outstanding** — rare breakout trajectory |

The inflection point: **5-7% weekly is the target zone YC coaches for.**

### Growth Compass Exercise (No Script)

Use this heuristic for any strategic decision:

1. State your target weekly growth rate (e.g., "7%")
2. For any proposed initiative, ask: *"Does this serve our target growth rate?"*
3. If yes → do it. If no → defer or drop it.
4. At end of week, measure actual growth. If you missed target, something else matters more than the thing you did.

This transforms the bewildering complexity of startup building into a single optimization problem, exactly as Graham intended.

### Full Analysis (Script)

```bash
python scripts/growth-compass.py \
  --current-value 1200 \
  --previous-value 1000 \
  --period weekly
```

Or with a full series for trending:

```bash
python scripts/growth-compass.py \
  --series "1000,1050,1100,1200,1350,1420" \
  --period weekly
```

#### Required inputs

| Flag | Description | Example |
|------|-------------|---------|
| `--current-value` | Metric value this period | `1200` |
| `--previous-value` | Metric value last period | `1000` |
| Or `--series` | Comma-separated values over time | `"1000,1050,1100"` |
| `--period` | `weekly`, `monthly`, or `quarterly` | `weekly` |

#### Optional inputs

| Flag | Description | Example |
|------|-------------|---------|
| `--project-weeks` | Weeks to project forward (default: 52) | `104` |
| `--target-revenue` | Target metric to reach | `100000` |
| `--metric-name` | Label for the metric (default: "users/revenue") | `"MRR"` |
| `--json` | Machine-readable JSON output | |
| `--add-to-weekly` | After computation, log this week's value for next check | |

#### Output fields

| Field | Meaning |
|-------|---------|
| `growth_rate_pct` | Calculated growth rate for the period |
| `yc_assessment` | Benchmark label (Concerning/Below Average/Good/Very Good/Outstanding) |
| `projected_1yr` | Value after 52 weeks at current rate |
| `projected_2yr` | Value after 104 weeks at current rate |
| `doubling_time` | Periods to double at current rate |
| `time_to_target` | If target set, periods to reach it |
| `assessment` | Plain-English interpretation |

## Methodology

### Growth Rate Calculation

```
growth_rate = ((current_value - previous_value) / previous_value) × 100
```

For series with 3+ data points, the script computes:
- **Period-over-period rates** for each interval
- **Mean growth rate** (arithmetic average)
- **Median growth rate** (robust to outliers)
- **Compound weekly growth rate (CWGR)** — fitted from first to last value

### The Compass Principle

From Graham's essay: "We usually advise startups to pick a growth rate they think they can hit, and then just try to hit it every week. If they decide to grow at 7% a week and they hit that number, they're successful for that week. There's nothing more they need to do. But if they don't hit it, they've failed in the only thing that mattered."

The script operationalizes this by:
1. Computing whether you hit your target
2. Projecting forward at current rate vs. target rate
3. Showing the gap in absolute terms so founders feel the urgency

### Compound Growth Projection

```
future_value = current_value × (1 + growth_rate/100)^periods
```

**The magic of compound growth at YC benchmarks:**

Starting from $1,000/month MRR:

| Weekly Growth | Month 12 | Month 24 | Month 36 |
|--------------|----------|----------|----------|
| 1% | $1,700 | $2,900 | $4,900 |
| 5% | $12,600 | $159,000 | $2.0M |
| 7% | $33,700 | $1.1M | $38M |
| 10% | $142,000 | $20.2M | $2.9B |

The difference between 5% and 7% weekly is the difference between a lifestyle business and a category-defining company. Small variations in growth rate produce qualitatively different outcomes.

## The Decision Framework

### For the Founder

1. **Monday**: Set this week's growth target
2. **Every decision**: "Does this serve the target?"
3. **Friday**: Measure actual growth
4. **If hit**: Successful week, nothing else matters
5. **If missed**: Alarmed. What went wrong? Adjust.

### For the Investor/Advisor

Use YC's diagnostic frame:

```
What's your weekly growth rate?  ─→  < 5%: Founders aren't doing
    ↓                                    unscalable things
    ↓                                5-7%: Good, keep pushing
    ↓                                10%+: Exceptional
What's your growth rate trend?     ─→  Accelerating: product-market fit
    ↓                                    Decelerating: market saturation or churn
    ↓                                    Flat: plateau, needs intervention
Is revenue growing same as users?  ─→  No: monetization gap
```

## Example: Early YC Company Assessment

```bash
python scripts/growth-compass.py \
  --current-value 35000 \
  --previous-value 32000 \
  --period monthly \
  --metric-name "MRR" \
  --target-revenue 100000
```

Growth rate: 9.4% monthly (~2.3% weekly)
YC assessment: Below average weekly, solid monthly
1-year projection: ~$107K MRR
Doubling time: ~7.7 months
Months to $100K MRR: ~12 months

## References

- `references/growth-compass-framework.md` — Full essay breakdown with quotes
- `assets/compound-growth-table.md` — Reference table for quick lookup
- `yc-default-alive-calculator` companion skill — For financial sustainability analysis
