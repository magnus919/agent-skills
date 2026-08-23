# Structured Planning Fields

Load this file when drafting or reviewing a migration plan: every plan must
address these fields. They may appear as checklist items, template fields,
table columns, or labeled section headers — not only as prose. The
[`../templates/migration-plan.md`](../templates/migration-plan.md) template
provides the ready-made structure that instantiates these fields.

## Reconciliation

| Field | Question to answer |
|---|---|
| Strategy | Full, incremental, or streaming reconciliation? |
| Frequency | Continuous, hourly, daily, or pre-cutover only? |
| Coverage | All records or a statistical sample? |
| Tolerance | What divergence is acceptable? |
| Failure action | Stop, alert, or automatically re-reconcile? |

## Correctness evidence

| Field | Question to answer |
|---|---|
| Comparison method | Dual-read, shadow-traffic, consumer-side test, or synthetic validation? |
| Pass criteria | What measurements confirm correctness (e.g., "100% record match," "error rate < 0.01%," "p95 latency within 10% of baseline")? |
| Evidence artifact | Where is the evidence recorded (dashboard link, test report, reconciliation log)? |

## Observability

| Field | Question to answer |
|---|---|
| Progress metrics | Bytes migrated, records processed, consumers cut over? |
| Anomaly signals | Error-rate spikes, latency degradation, reconciliation drift? |
| Dashboards and alerts | Where are migration-specific metrics visible, and who is on-call? |

## Customer impact

| Field | Question to answer |
|---|---|
| Visible change | What does the customer experience during each phase? |
| Downtime | Is any downtime expected, and how is it communicated? |
| Performance | Could latency, throughput, or error rates change during the migration? |
| Support | How are customer issues triaged and escalated during the migration window? |

## Ownership

| Field | Question to answer |
|---|---|
| Migration lead | Who owns the overall migration plan and its execution? |
| Phase owners | Who is accountable for expand, dual-running, cutover, deprecation, and cleanup? |
| Communication owner | Who owns stakeholder and consumer notifications? |
| Escalation path | Who is the decision-maker if the migration must be paused, rolled back, or abandoned? |
