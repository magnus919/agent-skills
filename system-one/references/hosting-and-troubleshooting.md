# Hosting, security, and troubleshooting

Use this reference when deploying a private Laya service, placing Jev behind a
gateway, or diagnosing a failed decision path.

For a runnable local Laya path and container build, begin with
`references/laya-self-hosting.md`. The operational checks below apply after
the target, owner, and rollback unit are known.

## Preflight record

Before a live change, record target, owner, model/provider and revision, image
digest, device/driver, model artifact checksum, question-contract hash,
calibration version, timeout/retry budget, expected p50/p95/p99, data handling,
health/readiness behavior, and rollback image/config. A read-only inspection can
proceed without mutation; restart, redeploy, scale, or credential changes need
an explicit target and rollback path.

## Health and delivery checks

Run checks in this order:

1. Process/container is running.
2. Readiness confirms model and tokenizer loaded on the intended device.
3. Model identity/revision matches the record.
4. A bounded synthetic request returns the expected contract.
5. A representative shadow case returns a validated answer and policy lane.
6. Metrics show queue time, inference time, errors, fallback, and actual device.

Do not call a process-health endpoint “inference is working.” Do not call a
green test stub or a zero exit “production delivery.” Verify the boundary the
user actually requested.

For the bundled adapter, `GET /healthz` is unauthenticated process liveness;
authenticated `GET /readyz` reports the loaded device only, not separate
tokenizer or calibration-artifact readiness. Extend the readiness gate to cover
every dependency the application requires before production traffic. A synthetic
`POST /v1/systemone` exercises inference. Use
`python3 scripts/systemone_probe.py --request examples/request.json --live --url
http://127.0.0.1:8788/v1/systemone --api-key-env
SYSTEM_ONE_SERVICE_TOKEN` from the skill root after setting the service
token. The probe's success establishes contract connectivity only; it does
not test calibration, throughput, or target-domain error rates.

### Bounded incident sequence

1. Freeze the exact failing request *shape* and correlation ID, redacting
   state. Capture target image/artifact/model/policy hashes and the observed
   failure lane; do not retry an unknown-completion action blindly.
2. Check health, readiness, actual device, and a synthetic request. If only
   production data fails, compare question IDs, option count, effective
   tokenization/truncation, language route, and response schema.
3. Separate time into queue, model inference, network, and downstream
   execution. A warm p99 regression with unchanged inference but increased
   queue time is capacity/backpressure, not necessarily model quality.
4. Reproduce once with the prior frozen artifact/config on scratch or shadow
   traffic. If the bad revision is confirmed and the rollback unit is known,
   restore it through the owning deployment mechanism; verify readiness,
   actual device, synthetic inference, and error/latency recovery afterward.
5. If no boundary is identified after three non-converging passes, stop,
   preserve evidence, and escalate to the owner. Do not keep changing model,
   runtime, and policy together.

## Failure matrix

| Symptom | First checks | Safe response |
|---|---|---|
| Jev 401/403 | Credential name, secret injection, account/model access | Stop retries; fix auth/configuration |
| Jev 400/422 | Exact JSON, question type, criteria, endpoint/model ID | Fix contract; do not retry unchanged payload |
| Jev 429/5xx/529 | Retry headers, rate, provider status, total budget | Bounded retry or review/fallback; preserve request ID |
| Jev timeout | Region, payload size, deadline, duplicate policy | Mark outcome unknown; retry only if duplicate cost is acceptable |
| Laya import/load hangs | Python/dependency versions, `USE_TF=0`, tokenizer config | Reproduce in a clean pinned environment |
| Laya is unexpectedly slow | Actual device, CPU fallback, model reloads, queue | Make residency/device observable before tuning |
| Laya language quality collapses | Script/language route and checkpoint | Route before inference; test language slice |
| High-cardinality Choice degrades | Effective head budget and label tokenization | Shortlist/hierarchy or increase budget and re-evaluate |
| Confidence is high but wrong | Out-of-domain/language slice, calibration, rubric | Gate by domain evidence; recalibrate or abstain |
| Valid response rejected | Adapter schema/version and rounding tolerance | Version the adapter and test both provider contracts |
| Model missing after restart | Artifact cache, revision pin, permissions, startup preload | Fail readiness; never download mutable weights on request path |

## Retry and idempotency

Retries are part of the semantics for a POST decision call. A network timeout
does not prove the provider did not finish the request. If the decision is
billable or triggers a downstream action, use a decision ID, a deduplication
record, and a policy for unknown completion. Prefer a human/replay queue over an
unbounded retry loop. Separate per-attempt timeout from total deadline.

## Routine administration

**Rotate a caller token:** identify the exact service and clients; prepare a
new secret in the approved store; roll a new worker/ingress accepting the new
token while old clients drain (or use an externally managed two-token overlap);
switch clients; verify authenticated readiness and a synthetic request;
revoke the old secret and check 401/error rates. The bundled adapter accepts
one token only, so rotation without an overlap mechanism needs a coordinated
cutover. Never paste either token into logs, support tickets, or commands
recorded in a shared shell history.

**Upgrade weights or runtime:** build a separate immutable image/artifact;
record its digest, package lock, model and tokenizer hashes, calibration and
question-contract revisions. Run the offline contract tests, actual-device
load, synthetic inference, held-out quality, cold/warm latency, and memory
checks. Shadow the new worker, then canary with an explicit error and
wrong-action rollback gate. Keep the previous *entire* unit until the new
one passes. A package-only upgrade can alter tokenization, so re-evaluate it
like a model change.

**Scale capacity:** measure arrival rate, p95/p99 service time, queue wait,
memory per resident worker, and burst length. Add workers only if each can
hold its checkpoint without swapping or unexpected CPU fallback. The bundled
adapter allows one inference in flight per process but does not limit idle
HTTP connection threads; ingress must cap connections and rate. Do not claim
autoscaling is healthy until cold-start preload and readiness are measured.

**Back up and recover:** store the immutable model artifact, image, contract,
policy, calibrator, and deployment manifest together. Back up outcomes and
labels under the applicable privacy policy; raw states are not needed for a
basic restoration test. Rebuild a scratch worker from the recorded revisions,
verify hashes and actual device, and run the synthetic and held-out gates.

## VPC hardening

- Keep the service private and authenticate every caller; do not expose a local
  model port to `0.0.0.0` without an intentional ingress boundary.
- Use least-privilege artifact access and read-only runtime model mounts where
  possible. Pin image, Python dependencies, tokenizer, weights, and calibration.
- Bound input bytes, UTF-8 validity, question count, option count, and total
  tokens. Reject unknown question types rather than silently coercing them.
- Redact state from logs and traces. Use hashed/correlated IDs, sampled payload
  capture only with an approved privacy policy, and short retention.
- Treat model output as untrusted data. Validate it before policy code and keep
  policy configuration outside user-controlled state.
- Add a kill switch that routes to human review or a deterministic baseline. A
  model process must not be able to grant itself new tools or authority.

## Evidence for a tuning claim

Freeze model revision, device, precision, batch/concurrency, context/options,
question contract, dataset, policy, and repetitions. Report warm/cold status,
latency percentiles, throughput, memory, cost, accuracy, calibration, and
coverage. One live example demonstrates connectivity, not quality or
reliability.
