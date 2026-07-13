# Pricing Strategy

Pricing communicates value, segments customers, and changes acquisition, retention, and cash flow. Treat it as a hypothesis to test, not a formula that produces a universally correct price.

## Pricing Models

| Model | Basis | Useful when | Limitation |
|---|---|---|---|
| Value-based | Customer value created | Value can be measured and differentiated | Requires credible value evidence and segmentation |
| Cost-plus | Cost to serve plus margin | Cost establishes a viable floor | Does not measure willingness to pay |
| Competitive | Relative market position | Buyers compare alternatives directly | Can obscure differentiated value or start a price war |
| Freemium | Free access with paid upgrade | Marginal cost is low and upgrade triggers are clear | Free-serving cost and conversion must support the economics |
| Tiered or usage-based | Segment, feature, capacity, or consumption | Different customers receive different value | Packaging can become hard to understand |

For value-based pricing, identify the customer outcome, quantify the economic value where possible, and test willingness to pay by segment. Cost-plus pricing can set a floor but should not be the sole pricing decision. Enterprise contracts, multi-year commitments, compliance requirements, and services bundles require deal-specific analysis beyond a self-serve pricing framework.

## Packaging

Build tiers around distinct customer needs and clear upgrade triggers, such as users, usage, workflow complexity, support, or governance. Keep the price metric understandable and show material differences between packages. A three-tier structure and annual-billing discounts are common patterns, not rules; validate them with the target market and unit economics.

Bundling works when features create more value together. Unbundling can help when needs vary materially. Mixed bundles trade flexibility against complexity and possible cannibalization.

## Testing a Price Change

1. State the goal: conversion, margin, expansion, cash collection, or a target segment.
2. Define affected cohorts, existing-customer treatment, contract obligations, and the period to observe.
3. Test with new customers or a controlled segment where practical. Track conversion, sales cycle, discounting, activation, retention, support demand, and contribution margin.
4. Compare results against a contemporaneous control or historical baseline adjusted for seasonality and channel mix.
5. Decide using an explicit trade-off, then monitor the affected cohorts after rollout.

Surveys reveal stated preference and are weaker evidence than observed behavior. Conjoint studies and experiments can help, but their validity depends on sampling, design, and sufficient volume. For causal interpretation of price tests, use `data-scientist`.

## Hypothetical LTV Trade-off

With monthly units throughout, a price increase can reduce LTV if churn rises enough:

```
Current simple LTV = $100 monthly ARPU x 60% gross margin / 5% monthly churn = $1,200
New simple LTV = $120 monthly ARPU x 60% gross margin / 8% monthly churn = $900
```

These are hypothetical figures. This simple LTV formulation assumes stable monthly churn and ARPU; use cohort analysis for a more complete view. Evaluate revenue, contribution margin, conversion, retention, and cash timing together rather than using LTV alone.

## Common Pitfalls

- Raising prices without a clear customer-value narrative or contractual review.
- Treating a competitor's list price as evidence of willingness to pay.
- Measuring only initial conversion while missing discounting, churn, or support costs.
- Mixing monthly and annual prices, contract values, or churn rates in one comparison.
- Leaving old prices unchanged without periodically reassessing value and costs.
