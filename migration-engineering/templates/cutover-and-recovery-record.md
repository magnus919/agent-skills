# Cutover and Recovery Record Template

Record the cutover procedure, recovery paths per step, and irreversible-step
acknowledgments for a migration.

## Cutover sequence

| Step # | Action | Performed by | Pre-condition | Expected result | Actual result | Interruption possible? | Rollback action |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| ... | | | | | | | |

## Cutover gate checklist

- [ ] Reconciliation passed for all data domains (see reconciliation plan).
- [ ] All consumers confirmed ready (see compatibility matrix).
- [ ] Observability dashboards deployed and verified.
- [ ] On-call responder briefed on cutover procedure and abort triggers.
- [ ] Rollback procedure tested (where applicable).
- [ ] Irreversible steps acknowledged (see below).
- [ ] Communication sent to stakeholders and consumers.

## Abort triggers

| Trigger | Threshold | Action |
|---|---|---|
| Error rate exceeds | | |
| Latency exceeds | | |
| Reconciliation drift detected | | |
| Consumer-reported issue | | |

## Recovery classification per step

| Step | Classification | Procedure | RTO | Tested date |
|---|---|---|---|---|
| | Rollback / Roll-forward / Restore / Irreversible | | | |

## Irreversible step acknowledgment

For each step classified as **Irreversible**:

### Step: [step description]

| Field | Value |
|---|---|
| Why is this step irreversible? | |
| Acceptance criteria that must be met before execution | |
| Stakeholders notified | |
| Stakeholder approval obtained from | |
| Contingency plan if migration fails after this step | |

### Sign-off

| Name | Role | Date | Signature |
|---|---|---|---|
| | Migration lead | | |
| | Stakeholder | | |

## Cutover execution log

| Timestamp | Step | Performed by | Result | Notes |
|---|---|---|---|---|
| | | | | |
