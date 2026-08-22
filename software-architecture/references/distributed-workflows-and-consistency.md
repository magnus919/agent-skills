# Distributed Workflows And Consistency

For every cross-process workflow, describe the command or event path, authority, durable state, acknowledgement point, and recovery path. Use a sequence or state table when prose would hide timing.

## Consistency contract

State what must be atomic, what may be eventually consistent, the allowed staleness or lag, the visibility point, and the conflict rule. Do not say "strong consistency" without naming the invariant and scope. Route message or API contract semantics to `api-design-and-evolution` and implementation patterns to `backend-engineering`.

## Failure inventory

Cover timeouts, retries, duplicate delivery, lost or delayed messages, reordering, partial commits, dependency outage, process restart, poison input, overloaded consumers, and operator intervention. For each, state detection, user-visible result, retry or compensation rule, idempotency key or deduplication scope, and reconciliation owner.

## Orchestration and choreography

Choose orchestration when a coordinator makes progress and compensation legible; choose choreography when independent facts and local reactions reduce central coordination. Either choice must expose observability, completion detection, stuck-work handling, and ownership. Do not treat asynchronous messaging as automatically decoupled or reliable.

## Recovery evidence

Name the state that can be rebuilt, the source of truth, the replay or reconciliation mechanism, and the test or exercise that proves recovery. Route RTO/RPO, game days, and restore verification to `resilience-and-recovery`; route service SLOs and incident operation to `site-reliability-engineering`.
