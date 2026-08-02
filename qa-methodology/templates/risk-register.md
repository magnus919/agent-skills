# Risk Register

> Record risk assessment results. Score each risk using the 5×5 P×I grid in [assets/risk-matrix-grid.md](../assets/risk-matrix-grid.md). See [risk-based-testing.md](../references/risk-based-testing.md) for scoring guidance and reassessment triggers.

## Metadata

| Field | Value |
|-------|-------|
| Project / Release | <name> |
| Workshop Date | <YYYY-MM-DD> |
| Facilitator | <name> |
| Participants | <names / roles> |
| Next Review Date | <YYYY-MM-DD> |

## Risk Items

| ID | Risk | Component | Probability (1–5) | Impact (1–5) | Score | Tier | Mitigation / Test Plan | Owner | Status | Last Reviewed | Reassessment Trigger |
|----|------|-----------|--------------------:|-------------:|------:|------|------------------------|-------|--------|---------------|----------------------|
| RISK-001 | <what could go wrong> | <affected area> | | | | P0 / P1 / P2 / P3 | <tests or controls> | <who> | Open / Mitigating / Closed | <YYYY-MM-DD> | <event that re-opens> |
| RISK-002 | <what could go wrong> | <affected area> | | | | P0 / P1 / P2 / P3 | <tests or controls> | <who> | Open / Mitigating / Closed | <YYYY-MM-DD> | <event that re-opens> |
| RISK-003 | <what could go wrong> | <affected area> | | | | P0 / P1 / P2 / P3 | <tests or controls> | <who> | Open / Mitigating / Closed | <YYYY-MM-DD> | <event that re-opens> |

### Column Guide

| Column | How to Fill |
|--------|-------------|
| ID | Sequential unique identifier (RISK-001, RISK-002, ...) |
| Risk | Plain-language description of the failure scenario |
| Component | System area or service affected |
| Probability (1–5) | 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain |
| Impact (1–5) | 1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic |
| Score | Probability × Impact (range 1–25) |
| Tier | From score: 20–25=P0, 12–19=P1, 6–11=P2, 1–5=P3 |
| Mitigation / Test Plan | Specific tests or controls that reduce this risk |
| Owner | Person accountable for implementing the mitigation |
| Status | Open (identified, no action) / Mitigating (in progress) / Closed (mitigated or accepted) |
| Last Reviewed | Date of most recent reassessment |
| Reassessment Trigger | Event that forces a re-score (incident, architecture change, release) |

## Scoring Anchors

| Rating | Probability | Impact |
|--------|-------------|--------|
| 5 | Will fail in production within a quarter | Data loss, security breach, revenue stoppage |
| 4 | Expected to fail within a year | Major feature outage, SLA breach |
| 3 | Could fail; uncertain | Degraded experience, workaround exists |
| 2 | Unlikely given current controls | Cosmetic, minor inconvenience |
| 1 | Extremely unlikely; well-understood code | No user-visible impact |

## Reassessment Triggers

Re-score the register when any of these events occur:

- [ ] Production incident in a registered area
- [ ] Architecture change (new dependency, refactor)
- [ ] New regulatory requirement
- [ ] Major release or migration
- [ ] Quarterly calendar review (default cadence)
- [ ] Team change (key engineer leaves)
- [ ] Customer escalation

## Summary

| Tier | Count | Total Test Hours (estimate) |
|------|------:|----------------------------:|
| P0 (20–25) | | |
| P1 (12–19) | | |
| P2 (6–11) | | |
| P3 (1–5) | | |
| **Total** | | |
