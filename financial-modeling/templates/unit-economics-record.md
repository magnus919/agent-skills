# Unit Economics Record

Fill one record per customer segment or acquisition channel. A unit-economics
number without a stated segment, period, and definition is not comparable. If a
field does not apply, write `n/a` — do not leave it blank.

## Context

- Segment / channel: `[fill: e.g. self-serve SMB via paid search]`
- Currency: `[fill: e.g. USD]`
- Measurement period: `[fill: e.g. trailing 3 months ending 2026-06-30]`
- Accounting basis: `[fill: cash or accrual; revenue recognition convention]`
- Prepared by / date: `[fill: name or handle, YYYY-MM-DD]`

## Inputs

| Input | Value | Source / definition |
|---|---|---|
| Monthly ARPU (or annual contract value) | `[fill: amount]` | `[fill: how revenue per customer is measured; what is excluded]` |
| Gross margin % | `[fill: percent]` | `[fill: which costs are included in COGS]` |
| CAC | `[fill: amount]` | `[fill: blended or channel-specific; which spend is included]` |
| Monthly logo churn % | `[fill: percent]` | `[fill: population and period used]` |
| Monthly revenue churn % (if different) | `[fill: percent or n/a]` | `[fill: contraction and churn treatment]` |
| Expansion / upsell revenue | `[fill: amount per period or n/a]` | `[fill: what counts as expansion]` |
| Contribution margin % (if used) | `[fill: percent or n/a]` | `[fill: variable costs included]` |

## Calculations

- Simple LTV = monthly ARPU x gross margin % / monthly churn rate = `[fill: result]`
- LTV/CAC = `[fill: result]`
- CAC payback (gross-margin basis, months) = CAC / (monthly ARPU x gross margin %) = `[fill: result]`
- Contribution-margin payback (if used, months) = `[fill: result or n/a]`
- Cohort LTV (if computed) = `[fill: result and method or n/a]`

## Interpretation

- Where this segment sits vs. context-dependent heuristics for its stage and model: `[fill: assessment]`
- What the payback implies for financing needs: `[fill: assessment]`
- Risks to the inputs (churn stability, margin drift, channel mix): `[fill: risks]`

## Decisions & Follow-Ups

- Decision this record supports: `[fill: e.g. continue spending on channel, change price]`
- Next measurement date: `[fill: YYYY-MM-DD]`
- Open questions: `[fill: what to validate next]`
