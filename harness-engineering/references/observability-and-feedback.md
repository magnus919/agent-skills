# Make behavior inspectable and feed it back into engineering

A runtime signal is useful when it distinguishes a competing hypothesis and can
be correlated with the task, action, source revision, and user outcome. A large
log stream without those links wastes context and can leak data.

## Minimum event vocabulary

Use task/run ID, candidate revision, phase, event ID, parent/correlation ID,
timestamp, bounded status, authority decision reference, resource/operation ID,
latency, and evidence reference. Minimize payloads; exclude secrets, PII, and raw
prompts/tool outputs by default. Define retention and access before export.

Capture: readiness failure, context source/version, tool requested/authorized,
action result/partial effect, checkpoint written, check outcome, termination
reason, handoff, and human intervention. Do not record hidden reasoning to get
observability; explicit actions and decisions usually provide the needed evidence.

### Optional typed intervention detail

The run record keeps `human_interventions` as its required, nonnegative integer
aggregate. It remains the count of human intervention events for that case; do
not replace it with a count of all actors. Record a count only when it is known:
never fill an unknown count with `0`. The optional `intervention_detail` object
adds bounded typed events when a question or evaluation needs to distinguish
what happened. The default run record remains aggregate-only; collecting event
detail is an explicit, question-scoped choice, not automatic instrumentation or
an export policy.

When included, `intervention_detail` has `coverage` (`complete`, `partial`, or
`not_collected`) and `events`. Each event has only these fields: `id`, `actor`,
`kinds`, `target`, `boundary_reference`, `changes`, `outcome`, and
`evidence_reference`. Actor is `human`, `orchestrator`, or `system`. `kinds` is
a nonempty list of unique, extensible short codes. Actor describes the input
origin: a person coordinating work is still `human`; `orchestrator` means an
automated coordinator. The target contains
`run_id`, `task_id`, and optionally `workstream_id`; `changes` contains
`goal`, `constraints`, and `authority`, each `true`, `false`, or `null` when
unknown. Outcomes and kinds are bounded codes, not prose. Example kind codes
include `information_decision`, `authorization_gate`, and `resume_recovery`;
they illustrate an extensible vocabulary, not a required taxonomy. References
are opaque, bounded printable IDs without whitespace. Event IDs and codes use at
most 64 characters matching `[A-Za-z0-9][A-Za-z0-9_.:-]*`; reference IDs use at
most 256 characters.

Count each input event once even when its `kinds` contains multiple codes. Only
events with `actor: human` contribute to `human_interventions`; orchestrator and
system resumption events do not. With `complete` coverage, the scalar equals the
number of human events. With `partial` coverage, the listed human events are a
subset and their count cannot exceed the scalar. With `not_collected`, `events`
is empty; absence of the detail object likewise means detail was not collected,
not that the count is zero. Keep an independently known aggregate when detail is
absent or partial. If the aggregate itself is unknown, do not fabricate zero or
present the record as a measured intervention count.

Allow only the listed event fields. Do not include raw human messages, prompts,
hidden reasoning, or unbounded free text. Use an event once at its owning/common
parent task; when it applies to several child cases, reference that event rather
than duplicating it. The uniqueness boundary is `(run_id, event.id)`. Typed
events describe observed changes; they do not grant authority, authorize an
action, or establish that an intervention improved productivity. A lower
intervention count alone is not a success claim.

Bounded opaque identifiers and codes can still contain sensitive or identifying
information; inspect their values under the same privacy policy as other
telemetry. Schema validation checks structure and bounds, not whether an ID or
code leaks sensitive data. If the task only needs correctness evidence and does
not ask about interventions or recovery, keep event detail out of the record.

## Golden journey debugging

1. Choose a real user journey with observable acceptance and a candidate revision.
2. Capture initial state; trigger one reproducible path.
3. Query logs/metrics/traces using run and operation IDs.
4. Find the first divergence and owning subsystem; compare alternatives.
5. Apply the smallest repair, restart affected owned services, rerun the same path.
6. Check expected output, side effects, and failure/recovery behavior.
7. Record the result at the real surface; do not substitute a mock or local
   simulation for deployed behavior requested by the user.

For UI: initial DOM/screenshot, action, resulting DOM/visible output, request/
console signals, and persisted state may each observe a different property.
A screenshot cannot prove data durability. Clearing console noise must not erase
the evidence of the original failure before recording it.

## Measures with explicit denominators

| Measure | Meaning and limitation |
|---|---|
| Accepted tasks / attempted tasks | Depends on pinned acceptance and task mix |
| False completion claims / completion claims | Requires checking claims independently |
| Human interventions / run | Lower is useful only with quality/authority guardrails |
| Recovery succeeded / injected interruptions | Define interruption boundaries and effects |
| Cost / accepted task | Include failed attempts and review cost |
| Retry count and tool-error categories | Diagnostic, not a final user outcome |
| Review/integration time | Exposes orchestration overhead hidden by parallel generation |

Do not compute a verified completion rate from mutable self-reported status alone.
An all-verified aggregate can hide a violated mandatory constraint; report critical
failures separately and invalidate conclusions when required reports are missing.

## Feedback promotion

A runtime incident can become a challenge case, a better tool error, a corrected
source, or an executable invariant. Choose the mechanism from failure attribution,
not from the availability of a logger. Record source revision and privacy/
contamination handling before reusing a trace in an eval dataset.

Harness engineering owns the runtime-to-action loop. For dataset design, grader
validation, statistical evidence and telemetry semantics, hand off to
agent-evals-and-observability. For Collector/Prometheus/Loki configuration use
telemetry; for dashboards use grafana. See the catalog-composition reference for
exact input and return contracts.

Use [templates/observability-plan.md](../templates/observability-plan.md) and
[templates/acceptance-contract.md](../templates/acceptance-contract.md).
