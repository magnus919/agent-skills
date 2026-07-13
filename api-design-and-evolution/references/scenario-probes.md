# Scenario Probes

Run these as design reviews and contract tests before declaring an interface ready.
Replace placeholders with the actual contract; grade explicit reasoning and evidence,
not endpoint counts or fixed operational values.

## Strict-Client Additive Evolution

Add a response field or enum value. Identify every consumer that has a strict decoder,
generated model, exhaustive switch, signed representation, cache key, or quota-related
assumption. Demonstrate the actual consumer behavior, then classify the change for
each consumer and select a rollout, compatibility flag, or migration if needed.

**Pass evidence:** consumer inventory, fixture/diff, strict-client result, assumptions,
and rollback path.

## Semantic Breaking Migration

Change an existing representation or operation meaning, such as moving a flat value
into a nested model or redefining a status. State why shape compatibility cannot prove
semantic compatibility. Provide coexistence, consumer migration, telemetry,
communication, deprecation metadata where applicable, sunset criteria, and rollback.

**Pass evidence:** before/after semantic contract, affected-consumer assessment,
migration verification, and an owner-approved rollback decision.

## Idempotent Retry With Partial Failure

Model a client timeout during a mutation that can create several effects or batch
items. Define the idempotency-key scope/equivalence, concurrent duplicate outcome,
accepted versus completed state, per-item results, retryable failures, reconciliation
read, and compensation/cancellation behavior.

**Pass evidence:** request/retry trace, duplicate trace, partial-result contract,
negative cases, and an explicit client stop condition.
