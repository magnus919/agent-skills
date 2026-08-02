# Migration Plan Template

Fill this template for every migration that crosses a system boundary.

## Migration identity

| Field | Value |
|---|---|
| Migration name | |
| Migration type(s) | Schema / Data / API / Infrastructure-Service |
| Current state | |
| Target state | |
| System boundary | |
| Risk class | Low / Medium / High |

## Expand/Contract sequence

| Phase | Description | Duration | Gate |
|---|---|---|---|
| Expand | | | |
| Compatibility window | | | |
| Dual-running (if applicable) | | | |
| Contract | | | |

## Backfill strategy (data migrations)

| Field | Value |
|---|---|
| Strategy | Full / Incremental / Streaming |
| Estimated volume | |
| Estimated duration | |
| Pre-conditions | |

## Reconciliation

| Field | Value |
|---|---|
| Strategy | Full / Incremental / Streaming |
| Frequency | Continuous / Hourly / Daily / Pre-cutover only |
| Coverage | All records / Statistical sample (size: ___) |
| Tolerance | |
| Failure action | Stop / Alert / Auto-reconcile |

## Cutover procedure

| Step | Action | Pre-condition | Post-condition | Interruption point? |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| ... | | | | |

| Field | Value |
|---|---|
| Cutover window duration | |
| Acceptable downtime | |
| Abort trigger | |

## Recovery paths

| Migration step | Recovery classification | Procedure | RTO | Tested? |
|---|---|---|---|---|
| | | | | |
| | | | | |

### Irreversible steps

| Step | Acceptance criteria | Stakeholder sign-off required | Contingency plan |
|---|---|---|---|
| | | | |

## Correctness evidence

| Field | Value |
|---|---|
| Comparison method | Dual-read / Shadow-traffic / Consumer-side test / Synthetic validation |
| Pass criteria | |
| Evidence artifact | |

## Observability

| Field | Value |
|---|---|
| Progress metrics | |
| Anomaly signals | |
| Dashboards and alerts | |
| On-call rotation | |

## Customer impact

| Phase | Visible change | Downtime | Performance impact | Communication |
|---|---|---|---|---|
| Expand | | | | |
| Compatibility window | | | | |
| Cutover | | | | |
| Contract | | | | |

## Ownership

| Role | Name / Team | Accountable for |
|---|---|---|
| Migration lead | | Overall plan and execution |
| Expand phase owner | | |
| Dual-running phase owner | | |
| Cutover phase owner | | |
| Deprecation phase owner | | |
| Communication owner | | Stakeholder and consumer notifications |
| Escalation decision-maker | | Pause, rollback, or abandon decisions |

## Deprecation and cleanup

| Activity | Target date | Owner | Dependencies |
|---|---|---|---|
| Deprecation announcement | | | |
| Consumer migration deadline | | | |
| Old system read-only | | | |
| Old system removal | | | |
| Code/flag cleanup | | | |
| Credential revocation | | | |

## Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Migration lead | | | |
| (Irreversible steps only) Stakeholder | | | |
