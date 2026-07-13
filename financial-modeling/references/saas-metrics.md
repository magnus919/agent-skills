# SaaS Metrics

SaaS metrics are useful operating measures only when their revenue definitions, customer population, and time periods are consistent. They are management heuristics, not accounting standards or universal thresholds.

## Growth and Retention

### ARR and MRR

```
ARR = recurring monthly revenue x 12
```

Alternatively, ARR can be the annualized committed recurring value of active subscriptions. State whether usage above committed minimums, services, one-time fees, credits, or foreign exchange effects are included. Do not add monthly and annual measures without converting them first.

```
Net new ARR = new ARR + expansion ARR - contraction ARR - churned ARR
```

### Logo Churn and Retention

```
Monthly logo churn = customers churned during month / customers at start of month
Annualized logo churn = 1 - (1 - monthly logo churn)^12
```

Annualization assumes a stable monthly rate. Segment churn by contract cadence, customer size, product, cohort, and channel before comparing it to a benchmark. Enterprise and SMB businesses can have materially different normal churn profiles.

### Net Dollar Retention (NDR)

```
NDR = (starting recurring revenue + expansion - contraction - churn)
      / starting recurring revenue
```

Use the same starting cohort and period for every component. NDR above or below 100% is informative, but its interpretation depends on segment, contract cadence, price changes, and whether expansion is durable. Do not use generic NDR bands as universal thresholds.

## Efficiency Metrics

### Rule of 40

```
Rule of 40 = revenue growth rate (%) + profit margin (%)
```

Specify the growth period and margin definition. EBITDA margin and free-cash-flow margin are common variants; neither is interchangeable with the other. The metric is generally more useful for scaled recurring-revenue businesses than for pre-revenue or early product-market-fit companies. Treat 40% and any score bands as contextual heuristics, and inspect the drivers and trend rather than optimizing one score.

### Magic Number

Magic Number compares sales and marketing investment with incremental recurring revenue. The numerator and denominator must represent compatible periods and units.

If the numerator is the increase in **quarterly recurring revenue** (a quarterly amount), annualize it before comparing it with prior-quarter sales and marketing spend:

```
Magic Number = quarterly recurring revenue increase x 4
               / prior-quarter sales and marketing spend
```

If the numerator is **net new ARR** (already an annualized contract-value measure), do **not** multiply it by four:

```
Magic Number = net new ARR for the quarter
               / prior-quarter sales and marketing spend
```

The `x 4` factor annualizes a quarterly revenue increment; it does not turn quarterly spend into annual spend and must not annualize ARR twice. Prior-quarter spend is a lagging convention, not a law. Use the same accounting classification and a stated attribution lag consistently. Magic Number thresholds are context-dependent heuristics, especially where sales cycles, ramping, channel mix, or capitalization policies differ.

### Burn Multiple

```
Burn multiple = net cash burn during a period / net new ARR during that period
```

Use positive cash burn and net new ARR from the same period. A ratio can be distorted by one-time cash events, large contracts, annual billing, and a very small denominator. Interpret it alongside cash flow, growth quality, gross margin, and retention rather than against a fixed universal band.

## Metric Discipline

- Keep bookings, billings, recognized revenue, cash collections, MRR, and ARR distinct.
- Use comparable period lengths and consistent cohorts in every ratio.
- Reconcile metric changes to customer-level or contract-level movements where possible.
- Inspect segments rather than allowing a blended average to hide poor retention or inefficient channels.
- Record definition changes, reclassifications, acquisitions, and currency effects alongside the metric trend.
