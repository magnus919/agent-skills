# Model Sanity Checklist

Run this checklist before a model is shared with a board, investor, or decision
maker. The goal is to catch structural breaks, driver inconsistencies, and
hidden assumptions — not to bless the forecast. Any unchecked item that is
material must be resolved or explicitly accepted with a note.

## Scope

- Model name / version: `[fill: name and version or date]`
- Currency and period convention: `[fill: e.g. USD, monthly]`
- Accounting basis: `[fill: cash or accrual]`
- Reviewer / date: `[fill: name or handle, YYYY-MM-DD]`

## Structure and Linkage

- [ ] Income statement, balance sheet, and cash-flow statement are present
- [ ] Ending cash on the cash-flow statement reconciles to the balance sheet
- [ ] One currency and one period convention used throughout
- [ ] Supporting schedules (revenue build, headcount, capex/debt, equity) feed the statements
- [ ] Bookings, recognized revenue, invoicing, and cash collections are kept distinct where timing differs

## Driver Consistency

- [ ] Revenue is built from operational drivers (customers x ARPU, expansion, usage, etc.), not a single growth-rate line
- [ ] Churn and retention assumptions are explicit and consistent with the revenue build
- [ ] Headcount, capacity, or COGS assumptions are consistent with the revenue trajectory
- [ ] Gross margin is tested against cost drivers rather than accepted as a constant
- [ ] Top-down market sizing is used only as a reasonableness check, not as the primary forecast
- [ ] No automatic expansion or linear-growth assumptions hidden in formulas

## Scenarios and Sensitivity

- [ ] Base, upside, and downside cases exist and differ in observable drivers
- [ ] Sensitivity analysis covers the inputs that most change ending cash or profitability
- [ ] Runway (if used) is computed from a cash-flow forecast and a stated burn definition
- [ ] One-time costs, slower collections, and delayed revenue are tested
- [ ] Illustrative percentages and amounts are labeled as hypothetical

## Documentation and Limits

- [ ] Input sources and assumptions are listed separately from calculated outputs
- [ ] Segment and channel differences are not hidden by blended averages
- [ ] Limitations and items needing professional review are stated
- [ ] Model outputs reconcile to the relevant statements where possible

## Verdict

- Result: `[fill: pass, pass with notes, or fail]`
- Blocking items: `[fill: list any unchecked items that are material and why they matter]`
- Recommended actions: `[fill: fixes to make before sharing]`
