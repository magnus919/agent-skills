# SLO-Cost Tradeoff Record

Fill this template to make an SLO-cost tradeoff explicit with evidence, ownership, and an accountable decision. An implicit acceptance of a lower SLO due to budget is not a decision — it is a gap.

## SLO under discussion

- **Service:** _[fill: service name]_
- **Current SLO:** _[fill: e.g., 99.9% availability, P99 latency < 200ms]_
- **SLO owner:** _[fill: name or team accountable for the SLO]_

## Cost of meeting the SLO

- **Current demand:** _[fill: e.g., 500 req/s]_
- **Capacity required at current SLO:** _[fill: e.g., 12 instances, 2-region]_
- **Current monthly cost:** _[fill: $X/month]_
- **Evidence:** _[fill: link to capacity model, unit-economics record, load-test report]_

## Projected cost at demand forecast

- **Projected demand (horizon):** _[fill: e.g., 1200 req/s in 6 months]_
- **Capacity required at projected demand:** _[fill: e.g., 28 instances, 2-region]_
- **Projected monthly cost:** _[fill: $Y/month]_
- **Evidence:** _[fill: link to capacity model]_

## Budget constraint (if applicable)

- **Budget cap (period):** _[fill: $B/month or "no explicit cap"]_
- **Gap:** _[fill: e.g., projected cost exceeds budget by 40% — $Z/month gap]_
- **Gap trigger:** _[fill: at what point does the gap become material? e.g., when projected cost exceeds budget by >10%]_

## Alternative SLO under consideration

- **Proposed alternative SLO:** _[fill: e.g., 99.5% availability, P99 latency < 500ms]_
- **Capacity required at alternative SLO:** _[fill: e.g., 8 instances, single-region]_
- **Projected monthly cost at alternative SLO:** _[fill: $C/month]_
- **Cost difference:** _[fill: $Y - $C = $D saved per month]_
- **Evidence:** _[fill: load test at alternative capacity, capacity model for alternative SLO]_

## Degradation path

If the alternative SLO is chosen, what does the degradation path look like?

- **What degrades:** _[fill: e.g., P99 latency increases; single-region means no cross-region failover]_
- **User impact:** _[fill: e.g., users in distant regions see higher latency; region outage → full service unavailability]_
- **Maximum degraded-operation window:** _[fill: e.g., degraded mode is acceptable for 6 months while budget is renegotiated; escalation after that]_
- **Recovery path:** _[fill: how does the service return to the original SLO? budget increase, architecture optimization, demand management?]_

## Error budget impact

- **Current error budget (at current SLO):** _[fill: e.g., 43.2 minutes/month downtime at 99.9%]_
- **Error budget at alternative SLO:** _[fill: e.g., 216 minutes/month downtime at 99.5%]_
- **Error budget burn-down risk:** _[fill: is the alternative SLO's error budget sufficient for expected incident frequency and duration?]_

## Decision

- **Chosen SLO:** _[fill: current SLO / alternative SLO / other]_
- **Rationale:** _[fill: why this choice — cost, reliability, user impact, business priority]_
- **Accountable owner:** _[fill: name — the person who owns this decision, not a team or role]_
- **Approver:** _[fill: name of person who approved — may differ from accountable owner]_
- **Decision date:** _[fill: YYYY-MM-DD]_
- **Review date:** _[fill: when this decision is re-evaluated — e.g., after 3 months or when demand reaches 80% of projected]_

## Guardrails

- [ ] **Cost optimization must not degrade reliability, privacy, or user outcomes.** If the tradeoff violates this principle, it is escalated — not accepted.
- [ ] The chosen SLO has been reviewed by the SLO owner and the cost owner.
- [ ] Load-test evidence exists for the chosen capacity at the chosen SLO.
- [ ] The degradation path (if applicable) has been reviewed and accepted.

## Assumptions

- [ ] _[fill: demand forecast is accurate — state assumption or evidence]_
- [ ] _[fill: unit costs are stable — state assumption or evidence]_
- [ ] _[fill: no architecture changes that would alter the capacity/SLO relationship]_
- [ ] _[fill: any other unverified assumption]_

## Tradeoffs

- _[fill: e.g., lower SLO → lower cost but increased risk of user-visible degradation]_
- _[fill: e.g., multi-region cost vs single-region risk — what is the business cost of a region-wide outage?]_
- _[fill: e.g., faster recovery (lower MTTR) can compensate for lower SLO — is the MTTR target achievable?]_
