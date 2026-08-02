# Implementation Plan: _[plan name]_

> Based on approved _[spec / requirement / decision record]_,
> approved by _[approver name or role]_ on _[approval date]_.

## 1. Work Breakdown

### Workstreams and vertical slices

Each workstream is a vertical slice — an end-to-end deliverable that provides
independent value. Prefer vertical slices over horizontal layers.

| ID | Workstream | Description | Completion criterion | Owner | Estimated effort |
|----|-----------|-------------|---------------------|-------|-----------------|
| WS-1 | _[name]_ | _[what this delivers, end to end]_ | _[observable condition that means it is done]_ | _[name or role]_ | _[team-weeks]_ |
| WS-2 | _[name]_ | _[...]_ | _[...]_ | _[...]_ | _[...]_ |

### Workstream detail

#### WS-1: _[workstream name]_

- **Scope**: _[what is in and explicitly out of scope]_
- **Dependencies**: _[what this workstream needs from others, with owners]_
- **Acceptance criteria**: _[testable conditions that define done]_
- **Verification**: _[how completion will be verified against the original requirement]_

## 2. Dependency Map

Complete the [dependency record](dependency-record.md) for the full dependency
graph. Summarize key dependencies here.

### Critical path

The critical path is the longest chain of dependent work that determines the
earliest possible completion.

```
_[WS-A] → [WS-B] → [WS-C] = critical path of N team-weeks_
```

### Dependency interfaces

| From | To | What | Contract (API, schema, event) | Hard or soft |
|------|----|------|-------------------------------|-------------|
| _[WS-X]_ | _[WS-Y]_ | _[description]_ | _[the interface artifact]_ | _[hard / soft]_ |

## 3. Sequencing and Parallelism

| Phase | Workstreams (concurrent) | Depends on | Duration | Synchronization gate |
|-------|--------------------------|------------|----------|---------------------|
| Phase 1 | _[WS-1, WS-2 (parallel)]_ | _[none]_ | _[N weeks]_ | _[what must be true to exit phase 1]_ |
| Phase 2 | _[WS-3 (sequential after WS-1)]_ | _[WS-1]_ | _[N weeks]_ | _[...]_ |

## 4. Ownership and Coordination

| Role / Team | Owner | Workstreams owned | Coordination mechanism |
|-------------|-------|-------------------|----------------------|
| _[team name]_ | _[name]_ | _[WS-1, WS-3]_ | _[sync meeting, Slack channel, dashboard]_ |

### Cross-team coordination

- **Integration checkpoints**: _[when cross-team work is verified together]_
- **Escalation path**: _[who to escalate to if a dependency is blocked]_
- **Communication cadence**: _[how often teams sync, what artifact tracks status]_

## 5. Rollout Strategy

### Rollout stages

| Stage | Scope (who gets it) | Duration | Gate (condition to proceed) | Observability signal | Rollback trigger |
|-------|---------------------|----------|-----------------------------|---------------------|-----------------|
| Stage 1 | _[internal / 1% / single region]_ | _[N days]_ | _[e.g., error rate < 0.1%, p95 latency < baseline +10%]_ | _[dashboard, alert]_ | _[specific condition]_ |
| Stage 2 | _[10% / beta users]_ | _[N days]_ | _[...]_ | _[...]_ | _[...]_ |
| Stage N | _[100%]_ | — | — | _[...]_ | — |

### Rollback plan per stage

| Stage | Rollback procedure | Data rollback | Time to rollback | Post-rollback state |
|-------|-------------------|---------------|-----------------|--------------------|
| Stage 1 | _[how to revert]_ | _[yes/no, how]_ | _[minutes]_ | _[what the system looks like after rollback]_ |

### For data migrations

- **Dual-write / backfill strategy**: _[how the transition period works]_
- **Schema compatibility**: _[forward-compatible, backward-compatible, or breaking]_
- **Cutover procedure**: _[step-by-step cutover]_
- **Reconciliation**: _[how to verify old and new data match before cleanup]_

## 6. Verification Traceability

| Requirement (from approved input) | Workstream | Acceptance criterion | Verification method | Verified by |
|-----------------------------------|------------|---------------------|--------------------|-------------|
| _[REQ-1 from spec]_ | _[WS-1]_ | _[testable condition]_ | _[test, demo, review]_ | _[name or role]_ |

## 7. Unresolved Decisions and Risks

| ID | Description | Impact | Owner | Resolution deadline | Status |
|----|-------------|--------|-------|--------------------|--------|
| DEC-1 | _[open decision]_ | _[what depends on it]_ | _[name]_ | _[date]_ | _[open]_ |
| RSK-1 | _[risk]_ | _[severity, likelihood]_ | _[name]_ | _[date]_ | _[open / mitigated / accepted]_ |

## 8. Assumptions

| Assumption | Made by | Date | Valid until | If invalid... |
|------------|---------|------|-------------|---------------|
| _[assumption]_ | _[name]_ | _[date]_ | _[date or event]_ | _[what changes in the plan]_ |
