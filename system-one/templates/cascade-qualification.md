# Cascade qualification record

Fill before evaluating a confidence-based acceptance/escalation policy. This is
a design and evidence record, not an executable gate or proof of calibration.

## Contract and ownership

- Workload, observable target, supplied evidence, unsupported domains:
- Primary/fallback immutable identities; adapter/runtime/precision revisions:
- Question/rubric, primitive, options, serialization, request grouping, decoder:
- Uncertainty signal definition; calibration artifact and fitting provenance:
- Candidate order policy, identity mapping, aggregation and tie/unknown handling:
- Exact authorization owner and deterministic execution boundary:
- Invalid/unavailable/uncertain first stage, fallback, and budget-exhaustion lanes:

## Frozen design

- Baselines: current rules, primary, fallback, matched-budget control, full route:
- Practical absolute accepted-error limits by consequence/slice:
- Maximum paired quality loss/noninferiority margin, minimum useful coverage:
- End-to-end latency/deadline, total cost, review-capacity limits:
- Selection and untouched-test IDs/hashes; independent grouping unit:
- Overlap/leakage check; label source and human/model-teacher/unknown provenance:
- Reviewer blinding, disagreement, ambiguity/abstention treatment:
- Threshold/calibration/aggregation fitted on selection only; freeze timestamp:
- Planned paired uncertainty calculation, sample counts and slice adequacy:

## Challenge review

| Condition | Expected policy behavior | Available evidence / result |
|---|---|---|
| Required evidence absent but confidence high | Obtain evidence/review; no confidence override | |
| Elaborate wrong answer | Count retained confident errors | |
| Reversed candidates / changed option set | Align identity; inspect instability; requalify | |
| Invalid primary / invalid fallback | Defer first; preserve unresolved final result | |
| Shared judge error / fallback regression | Count against independent labels | |
| New domain/model/rubric | Requalify before transfer | |

## Held-out outcomes

- Attempted/valid/resolved counts and label ambiguity:
- All-case accuracy, accepted error, coverage, escalation and review rates:
- Confusion, calibration bins/counts/Brier/NLL, error discrimination/risk–coverage:
- Deferral-band rescue/regression/shared errors; confident-error cases:
- Slice outcomes; paired cluster intervals against fallback/current baseline:
- Pass/fail against each preregistered practical gate, including absolute risk:
- Replay/offline simulation or measured live execution (name explicitly):
- Complete stage calls/retries/cost and unknown-price coverage:
- Measured delivery-boundary p50/p95/p99, queueing and deadline outcomes:
- Shadow sampling, rollback, disable conditions, reassessment triggers:

## Decision

- Scoped adopt / shadow / revise / reject, owner, evidence links and limitations:
- If revised after test inspection: new revision and new untouched test required:

Do not describe fallback agreement, model-teacher screening, structural manifest
validity, or a relative accuracy-retention ratio as validated release approval.
