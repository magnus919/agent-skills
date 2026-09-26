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
