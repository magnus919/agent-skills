# Fitness-Function Record

Use one record per check or deliberately grouped family of checks. Keep this record near the project's architecture governance artifacts and link it from the ADR. It describes the operational contract; executable code and raw results remain in the owning system.

## Identity

- **Record ID:** [stable identifier]
- **Status:** proposed | active | paused | retired
- **Decision:** [ADR number and link]
- **Decision owner:** [person or team]
- **Function owner:** [person or team]
- **Evidence consumer:** [person, team, or queue]
- **Last reviewed:** [YYYY-MM-DD]
- **Next review:** [YYYY-MM-DD or trigger]

## Claim And Scope

- **Architectural characteristic:** [what quality or constraint matters]
- **Decision claim:** [one sentence stating what the ADR requires]
- **Scope type:** atomic | structural | scenario | holistic
- **Included boundary:** [components, paths, environments, and population]
- **Excluded boundary and blind spots:** [what this cannot establish]
- **Failure consequence:** [what risk or decision consequence follows]

## Measurement And Execution

- **Function description:** [test, query, rule, audit, or review]
- **Evidence type:** static | test | runtime | audit sample | expert review | mixed
- **Inputs and fixtures:** [source data, versions, scenarios, and sample size]
- **Invocation:** [command, job, dashboard, review process, or URL]
- **Cadence:** change-triggered | continuous | scheduled | event-triggered
- **Environment and timeout:** [where, when, and how long]
- **Missing or indeterminate result:** [fail, warn, escalate, or retry rule]
- **Observed evidence location:** [run ID, report, query, or review artifact]

## Threshold And Validity

- **Pass condition:** [unit, aggregation, window, and allowed range]
- **Warning condition:** [if applicable]
- **Threshold rationale:** [baseline, uncertainty, harm boundary, and why achievable]
- **Denominator and exclusions:** [how the population is counted]
- **False-positive controls:** [known benign cases and their evidence]
- **False-negative controls:** [coverage gaps and compensating checks]
- **Gaming or proxy risks:** [ways the score could improve while intent worsens]
- **Countermeasures:** [raw evidence, sampling, paired measure, review, or spot check]

## Exceptions And Response

- **Failure response:** [block, alert, ticket, review, or escalation]
- **Exception process:** [required fields, approver, expiry, and compensating control]
- **Current exceptions:** [links or `none`]
- **Evidence review notes:** [what the last meaningful result changed or confirmed]

## Lifecycle

- **Review triggers:** [ADR change, boundary change, incident, owner change, stale data, or calendar]
- **Retirement criteria:** [when this check no longer tests a live decision]
- **Replacement or successor:** [link, or `none`]
- **Retirement record:** [date, approver, reason, last evidence, and unresolved risk]

## ADR Link Text

Add a concise link in the ADR, for example:

`Confirmed by: [FF-042](../architecture/fitness/FF-042.md); latest evidence: [CI run 1842](...)`
