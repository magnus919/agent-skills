# Dependency and Handoff Record

> Complements the [implementation plan template](implementation-plan-template.md).
> Fill one record per implementation plan. Each dependency must have an owner
> and a handoff contract.

## Dependency inventory

### Hard dependencies (blockers)

A hard dependency blocks progress: the dependent workstream cannot start or
complete until the dependency is satisfied.

| ID | Dependent workstream | Depends on (workstream / team / system) | What is needed | Owner of dependency | Needed by date | Status |
|----|---------------------|----------------------------------------|----------------|--------------------|---------------|--------|
| DEP-H1 | _[WS-N]_ | _[WS-M / team-X / service-Y]_ | _[specific artifact or condition]_ | _[name or role]_ | _[date]_ | _[on-track / at-risk / blocked]_ |

### Soft dependencies (preferences)

A soft dependency is preferred but not blocking: the work can proceed without
it, but quality, efficiency, or risk profile improves if it is satisfied.

| ID | Dependent workstream | Preferred input | Why it helps | Owner | Desired by | Fallback if unsatisfied |
|----|---------------------|----------------|-------------|-------|-----------|------------------------|
| DEP-S1 | _[WS-N]_ | _[design review from team-X]_ | _[reduces rework risk]_ | _[name]_ | _[date]_ | _[proceed without review; accept rework risk]_ |

## Critical path

The critical path is the longest chain of hard dependencies from start to
completion.

```
Start → [WS-A] → [WS-B (depends on WS-A)] → [WS-C (depends on WS-A, WS-B)] → Complete
        2 tw          3 tw (blocked without WS-A)        4 tw (blocked without WS-B)
Total critical path: 9 team-weeks
```

### Critical path shifts

| Shift | Trigger | New critical path | Impact |
|-------|---------|------------------|--------|
| _[DEP-H3 delayed by 2 weeks]_ | _[team-Y unavailable]_ | _[path shifts through WS-D]_ | _[+2 weeks to total]_ |

## Handoff contracts

A handoff contract defines what one team delivers to another and how the
recipient verifies it.

| Handoff ID | From (team / owner) | To (team / owner) | Artifact | Delivery date | Acceptance criteria | Verification |
|-----------|---------------------|-------------------|----------|--------------|--------------------|-------------|
| HND-1 | _[Team A / name]_ | _[Team B / name]_ | _[API spec, schema, library, config]_ | _[date]_ | _[what makes it acceptable]_ | _[how the recipient verifies]_ |

## Cross-repository dependencies

When work spans multiple repositories, each repository boundary is a dependency
interface.

| Repository | Owned by | Depends on (repository) | Interface contract | Version / SHA | Coordinated release? |
|------------|----------|------------------------|--------------------|--------------|---------------------|
| _[repo-a]_ | _[team]_ | _[repo-b]_ | _[API v2, shared schema v3]_ | _[tag or SHA]_ | _[yes — coordinated / no — independent]_ |

## External dependencies

Dependencies on teams, vendors, or services outside the plan's direct control.

| Dependency | Provider | Contact | SLA or commitment | Escalation contact | Contingency if unavailable |
|------------|----------|---------|------------------|-------------------|--------------------------|
| _[third-party API]_ | _[vendor]_ | _[email / Slack]_ | _[uptime SLA]_ | _[contact]_ | _[degrade gracefully, cache fallback]_ |
