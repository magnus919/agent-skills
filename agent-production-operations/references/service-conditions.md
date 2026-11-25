# Service conditions and runtime quality

Load this reference before expanding traffic or changing batching, streaming, cache,
retry, or fallback behavior. It consumes an evaluation report and the approved
production contract; it does not design graders or authorize a release.

## Record the operating envelope

Use `templates/service-condition-record.md` from the skill root. Bind evidence to
model, prompt, retrieval snapshot, tool/schema, policy and evaluator versions. Record
request mix, input/output lengths, concurrency, arrival pattern, queue discipline,
resource limits, cache state, retry budget, tool latency and failure injection.
A result at one concurrency and warm-cache condition does not establish performance
at another. Separate observations from extrapolations and missing measurements.

Before changing external state, confirm the target, scope, and rollback path. Read-only
discovery may proceed without confirmation. An approved production contract can supply
this confirmation when it covers the exact operation and operating envelope.

## Measure the whole task

Consume task-quality evidence from `agent-evals-and-observability`; agree measurement
boundaries with `site-reliability-engineering`. Distinguish:

- First visible output: evidence of responsiveness, not useful completion.
- First usable result: a task-specific event, such as an answer with verified supporting
  records. Define this event before measuring it.
- Terminal outcome: completed, rejected, timed out, cancelled, partial, or unknown.
- Committed effect: independently observed tool state, separate from narrated success.

Report the request denominator and outcomes alongside latency percentiles. Do not
silently drop errors, cancellations or timed-out requests to improve the latency
chart. For unfinished requests record time-to-terminal-error or censoring separately;
do not pretend their completion times are observed. Track total attempt cost and
cost per successful task, including retries and fallbacks, with explicit units.

## Interpret changes before acting

| Change or symptom | Evidence needed | Runtime decision |
|---|---|---|
| Batching raises throughput but delays interactive work | Queue wait, batch wait, task completion and failures at the intended arrival mix | Restrict batching to compatible work or revise admission within approved bounds; do not replace user latency with aggregate throughput |
| Streaming looks faster while tasks finish later | First output, usable-result event, completion, partial-stream failures | Keep partial output visibly provisional; never infer completed tool effects from streamed text |
| Cache improves aggregate latency | Cold/warm split, eligibility, source age, identity/authorization scope, invalidation behavior | Bypass entries outside the approved freshness or access boundary; recheck quality for cached and uncached paths |
| Tool times out after submitting a mutation | Operation identifier, tool-side status and independently observed state | Mark outcome unknown and reconcile before retry; do not replay a potentially committed effect blindly |
| Fallback avoids model errors but loses capabilities | Fallback-specific quality, tool availability, authority, load and cost evidence | Use only the validated fallback scope; otherwise reduce capability or transfer to an accountable operator |
| Cost per successful task rises while per-call cost falls | Success denominator, attempt count, retry/fallback distribution | Enforce total task budgets, investigate the failing slice, and pause expansion |

A valid empty retrieval result is not the same as a transport error or a cancelled
query. Preserve those distinctions in the status handed to the user and in retained
telemetry. Do not turn unavailable evidence into a negative search conclusion.

## Check that fast safeguards still cover the intended work

Compute the denominator from the versioned policy at action admission:
attempts that required a particular check, counted once per attempt using
an attempt ID, whether or not the checker ran. For those attempts, distinguish
valid check verdict (allow or deny), routed to review, held, execution without
a required verdict, and missing telemetry. Track verdict coverage separately
from safe handling; routing to review protects the action but is not a model
verdict. Reconcile admission records with tool outcomes so a checker outage
cannot erase its own evidence. Treat unverified coverage as unknown and an
observed unauthorized execution as a control incident.

Pair the coverage and disposition breakdown with check and task p95, reviewer
queue age, and accepted outcomes by action class. On a timeout or unavailable
checker, hold the affected action or route it to the authorized review lane;
keep separately permitted work available. Validate coverage and safe failure
before restoring capability. To test, inject an outage and compare with normal
traffic; a faster dashboard that omits the affected attempts is not a win.

Motivation: [Runkle's account of disabling a slow tool-risk check](https://www.youtube.com/watch?v=qquIt--ANqI&t=391s).
The coverage metric is a proposed operating control, not a reported result.

## Bound degradation and recovery

For each important failure, name the detector/window, owner, immediate action,
permitted fallback, authority reduction, restoration evidence and review deadline.
Thresholds come from the approved contract; examples are not universal limits.
If a proposed fallback can perform additional actions or read additional data, it
needs a new authority decision rather than inheriting the original clearance.

Keep unknown side effects in a reconciliation queue with ownership and deduplication
keys. Cancellation of generation does not prove that an already dispatched tool
operation was cancelled. Confirm the authoritative tool outcome or escalate the
unresolved state without repeating it. Route incident investigation to SRE and
verified incidents to the existing trace-to-eval workflow.

## Exit gate

Expansion remains paused until the intended envelope has task-quality evidence,
end-to-end outcome and cost measures, validated fallback behavior, and a responsible
operator for unresolved state. Record `supported`, `outside-tested-envelope`, or
`insufficient-evidence` for each proposed condition. Existing authority can continue
only within its already approved bounds; this reference grants no new authority.

## Research basis

Original operational synthesis, checked against these primary references on 2026-09-14:

- [Google SRE: implementing SLOs](https://sre.google/workbook/implementing-slos/): user-oriented indicators, denominators and explicit measurement definitions.
- [OpenTelemetry GenAI metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md): separate inference timing and token measures. Pin the convention version when implementing instrumentation; this workflow does not prescribe metric names.
