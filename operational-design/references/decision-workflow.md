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

## Worked example: qualify a service workflow by intent

A support team wants to automate delivery-status responses. A status request
can sound like a shipment-loss report, which requires timely human investigation.
Treat these as separate intents with different handling and consequences. Start
with shadow runs on approved cases, leaving live handling with the service team.

1. Record the owner, case boundary, human baseline, fallback, and the exact
   model, instructions, tools and policy under evaluation. Retain a separate
   human-adjudicated holdout that includes ambiguous and rare consequential cases.
2. Compare cost, timeliness and errors with the baseline per intent. If aggregate
   accuracy improves while loss-report recall drops below its agreed floor, route
   that intent and uncertain cases to staffed review. Evaluate the status intent
   independently. A judge's agreement can inform evaluation alongside independent
   labels. Use [evaluation design](../../agent-evals-and-observability/references/evaluation-design.md)
   and [judge stability](../../agent-evals-and-observability/references/judge-stability.md).
3. Record each intent's current authority, approved data, actions, owner,
   monitored error threshold and fallback. Route promotion or demotion to
   [earned autonomy](../../ai-governance/references/earned-autonomy.md).
   Keep any later system-of-record write behind a separate executor that
   revalidates eligibility, applies current authority, reconciles duplicate
   requests and records the outcome. Shadow success supports an evaluation
   decision. A write needs its own authorized qualification.

In the example, the loss intent remains on the human route even if the
routine status intent qualifies for a later tier. Recheck on policy, data or
model change. [The Counting House](https://yegge.ai/essays/the-counting-house/)

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

## Example: separate what a probe can settle from a product choice

In the [export brief](../../product-discovery/references/artifact-first-interview.md#example-turn-a-disputed-term-into-acceptance-evidence),
the membership criterion is accepted in revision 4. Two questions remain.
Does the current service hold a stable membership ID at download time? Use a
read-only trace or a reversible fixture in a disposable environment. The fixture
shows the ID is available. May a former member retrieve a previously issued
download link? Record that decision as D-12 with the product owner, the affected
acceptance criterion and the latest decision point. The fixture result answers
the first question. The second remains open until the owner decides.

Link the observed result and keep scope and decision revision on the
[project planning record](../../technical-project-management/references/flow-and-capacity.md#example-decisions-across-sessions).
Use [recorded design rationale](../../software-architecture-analysis/references/recorded-design-rationale.md)
where rationale matters. Runtime observation establishes behavior at the observed
revision. Rationale comes from the record of the decision.
