# Operational Design Decision Workflow

Use this workflow to choose a process, control, metric, or vendor operating model; route technical implementation elsewhere.

## Repeatable Method

1. **Frame inputs:** customer/value outcome, current workflow, volume and variability, owners, constraints, failure modes, service level, compliance obligations, and baseline measures.
2. **Map and compare:** capture handoffs and queues, identify the bottleneck, compare simplification, staffing, vendor, and automation options, and state assumptions.
3. **Decide with gates:** select an operating model only with a named accountable owner, measurable KPI, control, escalation path, capacity/cost guardrail, and review cadence.
4. **Validate:** pilot the smallest reversible change, compare throughput/quality/lead time and control exceptions to baseline, then scale or rollback.
5. **Package evidence:** retain current/future map, RACI, KPI definitions, vendor scorecard or control matrix, decision log, and review date in an artifact pyramid.

## Worked Example

A support process misses its 24-hour SLA. Mapping shows a vendor handoff queue is the constraint. The decision is to add a triage owner and vendor escalation tier for 30 days, not automate first. Success requires 95% first response within 24 hours, fewer than 2% reopens, and zero critical control exceptions; the weekly review either scales the model or reverts it.

## Reusable Artifact

```text
Operating model decision record
Outcome / process boundary / owner / date / review date
Baseline (volume, lead time, quality, cost):
Bottleneck and failure modes:
Options, assumptions, and evidence:
Decision / RACI / KPI and control:
Capacity, cost, SLA, and escalation guardrails:
Pilot, stop rule, result, and next action:
```

## Routing Matrix

| Need | Route to | Handoff in / out |
|---|---|---|
| Strategic priority | [strategy-frameworks](../../strategy-frameworks/SKILL.md) | Operating constraint in; priority choice out |
| Cost or unit economics | [financial-modeling](../../financial-modeling/SKILL.md) | Volume/cost assumptions in; scenario model out |
| Technology/vendor feasibility | [technology-radar](../../technology-radar/SKILL.md) | Capability need in; evaluated option out |
| Delivery work breakdown | [implementation-planning](../../implementation-planning/SKILL.md) | Approved model in; sequenced work out |
| Evidence structure | [artifact-pyramids](../../artifact-pyramids/SKILL.md) | Maps and measures in; indexed evidence out |
| Team topology or role design | [org-design](../../org-design/SKILL.md) | Capacity/role constraint in; people design out |

Do not create an operations sibling for a narrow tool or department: use the named tool owner or existing methodology and preserve this boundary.
