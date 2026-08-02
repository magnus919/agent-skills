# Risk, Decision, and Verification Record

> Complements the [implementation plan template](implementation-plan-template.md).
> Fill one record per implementation plan.

## Risk register

| ID | Risk description | Severity (1-5) | Likelihood (1-5) | Impact | Mitigation | Owner | Status |
|----|-----------------|---------------|-----------------|--------|-----------|-------|--------|
| RSK-1 | _[what could go wrong]_ | _[1-5]_ | _[1-5]_ | _[blast radius, what depends on this]_ | _[what reduces likelihood or impact]_ | _[name]_ | _[open / mitigated / accepted]_ |

### Risk heatmap notes

- **Severity 4-5**: requires explicit mitigation and escalation path.
- **Likelihood 4-5**: requires a contingency plan with trigger condition.
- **Both severity and likelihood >= 4**: flag for leadership review before plan
  approval.

## Decision log

### Resolved decisions

| ID | Decision | Options considered | Chosen | Rationale | Decided by | Date |
|----|----------|-------------------|--------|-----------|-----------|------|
| DEC-1 | _[what was decided]_ | _[A, B, C]_ | _[B]_ | _[why B over A and C]_ | _[name or role]_ | _[date]_ |

### Unresolved decisions

| ID | Decision needed | Options | Blocked by | Impact of delay | Owner | Deadline | Status |
|----|----------------|---------|-----------|----------------|-------|---------|--------|
| DEC-U1 | _[what must be decided]_ | _[A, B]_ | _[waiting on architecture review]_ | _[blocks WS-3 start]_ | _[name]_ | _[date]_ | _[open / escalated]_ |

## Assumptions register

| ID | Assumption | Basis (evidence or guess) | Valid until | Owner | If invalid... |
|----|-----------|--------------------------|-------------|-------|--------------|
| ASM-1 | _[what we assume to be true]_ | _[data, precedent, or explicit guess]_ | _[date or milestone]_ | _[name]_ | _[what changes]_ |

## Verification checklist

Trace every requirement from the approved input to a verification activity.

| Requirement ID | Requirement summary | Workstream | Acceptance criterion | Verification method | Verifier | Evidence artifact | Status |
|---------------|--------------------|-----------|--------------------|--------------------|---------|-------------------|--------|
| REQ-1 | _[from approved spec]_ | _[WS-1]_ | _[testable condition]_ | _[automated test / manual review / demo / monitoring]_ | _[name or role]_ | _[test report, review sign-off]_ | _[pending / passed / failed]_ |

### Verification methods reference

| Method | When to use | Evidence |
|--------|------------|----------|
| Automated test | Deterministic behavior | Test run output, CI pass |
| Manual review | Subjective quality, UX, docs | Reviewer sign-off |
| Demo / walkthrough | Integrated behavior across teams | Demo recording or notes |
| Production monitoring | Rollout health, SLO compliance | Dashboard screenshot, alert silence |
| Data reconciliation | Migration correctness | Row counts, checksums, diff report |

## Rollback verification

For each rollout stage, verify that rollback works before proceeding.

| Stage | Rollback test performed? | Rollback time (actual) | Data integrity verified? | Signed off by |
|-------|------------------------|----------------------|------------------------|--------------|
| Stage 1 | _[yes / no]_ | _[minutes]_ | _[yes / no]_ | _[name]_ |
