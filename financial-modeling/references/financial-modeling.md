# Financial Modeling

Financial models translate assumptions into projected statements. Their value is making assumptions explicit and internally consistent, not predicting the future.

## Model Structure

A complete model links three statements and the schedules that drive them.

| Statement | What it shows | Key line items |
|---|---|---|
| Income statement (P&L) | Profitability over a period | Revenue, COGS, gross profit, operating expenses, net income |
| Balance sheet | Assets, liabilities, and equity at a point in time | Cash, receivables, payables, debt, equity |
| Cash-flow statement | Cash sources and uses over a period | Operating, investing, financing cash flows, net change in cash |

| Supporting schedule | Feeds into | Contents |
|---|---|---|
| Revenue build | P&L revenue and receivables | Customers, conversion, pricing, collections |
| Headcount plan | P&L operating expenses | Roles, start dates, compensation, benefits |
| Capex and debt | Fixed assets, depreciation, debt, interest | Purchases, useful lives, principal, rates, terms |
| Equity | Equity and financing cash flow | Rounds, options, dilution |

Use one currency and a stated period convention throughout. Reconcile ending cash on the cash-flow statement to the balance sheet. Accounting classification and recognition require the applicable accounting framework and professional review.

## Revenue and Costs

Build the base case from operational drivers. Use top-down market sizing as a reasonableness check, not the primary forecast.

```
Bottom-up revenue = customers x revenue per customer + expansion revenue
```

For a monthly subscription model, if all inputs are monthly:

```
Month N recurring revenue =
  (prior-month customers x (1 - monthly logo churn) x monthly ARPU)
  + (new customers x monthly ARPU)
  + expansion revenue for the month
```

For usage-based revenue, model active accounts, usage per account, price per unit, and seasonality. For services, model billable headcount, utilization, billable rate, and billable days. Keep bookings, recognized revenue, invoicing, and cash collections separate when timing differs.

| Cost type | Examples | Modeling approach |
|---|---|---|
| Fixed | Base salaries, rent, subscriptions | Step changes at hiring or capacity thresholds |
| Variable | Hosting, payment processing, commissions | Per unit or percentage of the relevant driver |
| Semi-variable | Support and sales capacity | Fixed base plus staffing tiers triggered by volume |

Ratios such as R&D, sales and marketing, G&A, and gross margin as a percentage of revenue are context-dependent heuristics. Compare like-for-like business models, maturity, and accounting treatment rather than treating ranges as targets.

## Scenarios and Sensitivity

Always show a base, upside, and downside case. Change observable drivers, such as customer additions, churn, price, sales capacity, collection timing, headcount, and variable cost, rather than only changing the final revenue number.

Use one- or two-way sensitivity tables to identify inputs that materially change ending cash, profitability, or a financing need. Label every illustrative percentage or dollar amount as hypothetical; do not mistake a scenario for a forecast.

Common errors include linear growth assumptions, hidden customer concentration, automatic expansion assumptions, omitted churn, and confusing revenue timing with cash timing.

## Runway

Define monthly net cash burn as a positive cash outflow before calculating runway:

```
Net monthly cash burn = cash operating outflows - cash operating inflows
Runway (months) = available cash / net monthly cash burn
```

Use a cash-flow forecast, not P&L loss, when receivables, payables, deferred revenue, capex, debt service, financing, or taxes are material. If the business is cash-generative, runway is not meaningful as a finite quotient; model the cash balance and liquidity risks instead.

Runway bands, such as when to reduce spending or begin financing conversations, are management heuristics. They depend on financing access, contractual commitments, volatility, and the time needed to execute a contingency plan. Include one-time costs and test slower collections, delayed revenue, and higher spend.
