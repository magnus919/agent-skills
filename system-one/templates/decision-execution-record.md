# Decision and execution record

Fill for one consequential decision in a resumable operational workflow.
Keep references/hashes instead of secrets or raw personal data. A persisted
record does not itself make external actions idempotent or verify their effects.

## Observations and judgment

- Workflow/incident ID, event ID, stage, decision ID:
- Observation source, observed_at, state version/hash, expires_at:
- Bounded evidence references, missing/contradictory evidence, redaction policy:
- Exact candidate identities; deterministic eligibility and excluded actions:
- Hypotheses, discriminating read-only tests, falsifying observations if relevant:
- Model/checkpoint, endpoint identity, adapter/runtime and calibration revisions:
- Question/rubric, primitive/options/order, request grouping, policy revisions:
- Request/attempt IDs, start/end times, failures, selected final response ID:
- Validation outcome, typed values, uncertainty signal, unknown/abstention lane:
- Policy outcome: annotate / inspect / hold / review / permitted command:

## Authorization and command intent

- Exact target, scope, parameters/hash, impact ceiling, rollback path:
- Authority evidence and approval ID; bound action/state; approval expiry:
- Fresh observation and precondition recheck after any approval wait:
- Operation ID/idempotency key and executor deduplication contract:
- Preconditions for reusing this decision for an execution retry:
- Reobserve/redecide triggers: state/target/parameters/policy change or expiry:
- Model-call, autonomous-write, and per-action kill switches:

## Attempts and effect reconciliation

| Attempt ID | Operation ID | Start/end | Response/effect status | Evidence | Next lane |
|---|---|---|---|---|---|
| | | | not started / failed before effect / confirmed / unknown | | |

- Unknown completion: status query/reconciliation method before retry:
- Retry bounds/deadline; deduplication or idempotent activity verification:
- Worker restart/checkpoint test; response-loss-after-effect test:
- Pending approval timeout; escalation owner and handoff artifact:

## Independent verification and closure

- Executed change/effect receipt (separate from proposed command):
- Current user-visible symptom and supported cause, with evidence references:
- Cause removal check, restored user journey, governing invariant checks:
- Stability window, observed outcomes, regressions, still-unknown checks:
- Rollback result if exercised; operator closure decision and evidence:
- End-to-end latency/cost/review workload; stage attempt counts:

An expired approval or unknown effect is not a permit to replay a write. Reconcile
and reobserve, then obtain renewed judgment/authority where required. Do not
mark resolved solely from a model's assessment or a currently healthy pod count.
