# Unit Economics

Unit economics asks whether a customer or transaction creates value after the costs required to acquire and serve it. Define the customer segment, channel, currency, and measurement period before comparing metrics.

## Core Metrics

### Customer Acquisition Cost (CAC)

```
CAC = sales and marketing acquisition spend during a period
      / new customers acquired during the same period
```

State whether CAC is blended, paid, or channel-specific. Acquisition spend can include sales and marketing compensation, commissions, advertising, acquisition tools, and attributable programs. Exclude R&D and retain/support costs unless the stated definition intentionally includes them. Align the spend window with the acquisition cohort and account for long sales cycles.

### Lifetime Value (LTV)

For a simple monthly subscription estimate with monthly ARPU and monthly logo churn:

```
Simple LTV = monthly ARPU x gross margin percentage / monthly churn rate
```

This assumes stable price, margin, and churn. Cohort LTV, calculated from actual customer revenue and service costs over time, is more reliable when history is available because it captures retention curves, expansion, contraction, and segment differences.

### CAC Payback

```
Gross-margin payback (months) = CAC / (monthly ARPU x gross margin percentage)
```

This common measure uses gross margin. For a more conservative cash or operating view, substitute monthly contribution margin if its variable costs are defined consistently. Do not divide a CAC measured over a quarter by annual ARPU; convert both numerator and denominator to comparable units first.

### Contribution Margin

```
Contribution margin = customer revenue - COGS - variable operating costs
```

Variable costs may include account-specific infrastructure, payment processing, support, onboarding, and per-seat licenses. Fixed R&D, G&A, and acquisition expense are normally analyzed separately.

## Interpretation

```
LTV/CAC = LTV / CAC
```

LTV/CAC, payback, churn, and margin bands are context-dependent heuristics, not universal thresholds. A long payback can be reasonable for contracted enterprise customers; a high LTV/CAC ratio can also signal underinvestment in growth. Stage, contract duration, gross margin, channel mix, financing constraints, and retention quality determine the useful range.

Segment analysis is essential. Calculate CAC, ARPU, margin, churn, LTV, and payback by meaningful customer segment and acquisition channel. Avoid averages that hide materially different enterprise, mid-market, SMB, self-serve, or partner economics.

## Common Pitfalls

- Mixing monthly churn with annual ARPU, or expenses from one period with customers from another.
- Treating simple LTV as a forecast despite changing retention or expansion behavior.
- Counting only current customers and omitting customers that already churned.
- Treating all sales and marketing spend as short-term acquisition spend when brand investment has a longer horizon.
- Applying VC-backed SaaS benchmarks to bootstrapped, usage-based, marketplace, services, or other business models without adjustment.
- Failing to refresh definitions and cohorts as pricing, channel mix, and customer mix change.
