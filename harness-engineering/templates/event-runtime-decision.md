# Event runtime decision

## Task and choice

- Representative task, revision, external-effect surface:
- Observed waiting/compute/queue problem and baseline:
- Resident loop or event-driven continuation; why:
- Model/configuration, source revision and environment:
- Acceptance, time/cost bounds, rollback and owner:

## Continuation and event contract

- Durable history and metadata; external resources reconstructed separately:
- Conversation single-writer mechanism; shared-resource fencing:
- Event ID, causal parent, source operation, tenant/thread/task revision, expiry:
- Producer authentication, callback admission and current authority on wake:
- Dispatch acknowledgement versus eventual outcome/postcondition:
- Inline, child or deferred routing; context inheritance and fan-out budget:
- Deferred-event storage, retention and process-death behavior:
- Synchronous exceptions and slice time/completion/cost limits:
- Compaction index, child spawn boundary, source lookup and fidelity check:

## Effects and recovery

| Boundary | Transaction/ack order | Recovery evidence | Owner |
|---|---|---|---|
| History append / dedup ID | | | |
| Intent commit / dispatch | | | |
| Tool acceptance / effect | | | |
| Effect / result checkpoint | | | |
| Cancel / late callback | | | |

- Stable operation/effect key; outbox or reconciliation strategy:
- Revocation, unknown effects, stale publication and subscription cleanup:

## Bounded validation

| Drill | Expected invariant | Actual receipt | Pass / fail / not assessed |
|---|---|---|---|
| Duplicate/mismatched/forged callback | | | |
| Crash at each boundary above | | | |
| Process loss with deferred event | | | |
| Flood and duplicate child creation | | | |
| Compaction across spawn/revision change | | | |
| Grant revoked during sleep | | | |

- Real task outcomes versus scripted workload:
- Resident, active, queued and waiting populations; latency and total cost:
- Comparable baseline/candidate schedule and uncertainty:
- Remaining evidence, disposition and responsible decision owner:
