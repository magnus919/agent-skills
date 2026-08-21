# Event-Driven Service Implementation

Load this reference when a service publishes domain facts, consumes messages, or
coordinates durable state with asynchronous work. It covers implementation seams;
use `api-design-and-evolution` for the event contract and delivery agreement.

## Boundaries And Flow

Keep three responsibilities visible, even when the project uses different names:

| Boundary | Owns | Must not know |
|---|---|---|
| Domain | Invariants, state transitions, and meaningful past-tense business facts | ORM types, broker clients, HTTP, serialization, retry policy |
| Application | Use-case coordination, unit-of-work scope, ports, and event dispatch intent | Vendor-specific connection or broker details |
| Infrastructure | Database mappings, transaction implementation, outbox relay, broker adapter, inbox store | Business decisions and domain invariants |

The normal command path is:

1. Translate the request into an application command at the transport boundary.
2. Open one unit of work, load the aggregate through a domain-facing repository, and
   invoke behavior that protects its invariants.
3. Collect domain events produced by the successful state transition. Events are facts,
   not instructions to make setters run; do not emit one for every field change.
4. Persist aggregate changes and an outbox row in the same local transaction. The row
   contains a stable event identity, type, schema version, aggregate identity/version,
   occurred-at value, payload, and trace/correlation context appropriate for the
   service's data policy.
5. Commit before performing broker I/O. A relay publishes committed rows and records a
   delivery result or retry state. It must tolerate a crash after publish and before
   marking the row complete, so consumers still need deduplication.

The unit of work is a logical application operation, normally one aggregate's
immediate invariants plus its outbox records. A broader transaction needs a concrete
invariant justification. Do not turn it into a distributed transaction by calling an
external service while the local transaction is open.

## Inbox And Idempotent Handlers

Assume at-least-once delivery unless the contract proves a narrower guarantee. An
inbox record or equivalent deduplication mechanism should be keyed by the consumer's
identity and the producer event identity, not merely by a business field that may be
reused. This reference uses a single atomic transaction design: the inbox insert,
handler effects, and completed state commit together. It does not use leases or
separate claim/completion transactions.

1. Validate the envelope and schema version before domain mapping. Treat event input
   as untrusted: verify producer authenticity and authorization before trusting the
   producer identity or event identity. Route the protocol, key, credential, and
   authorization design to `secure-software-engineering`.
2. Parse with a safe, data-only deserializer; never use pickle, eval, unsafe YAML, or
   gadget-prone formats. Treat every deserialized field as untrusted at downstream
   boundaries and use parameterized queries plus safe command, template, and path
   handling. The quarantine path must use bounded, access-controlled storage for
   opaque or encrypted raw bytes and sanitized metadata, not blindly persist and
   reparse executable or injection-bearing content. Route detailed injection and
   deserialization controls to `secure-software-engineering`.
3. Insert the inbox identity with a uniqueness constraint in the same transaction as
   the handler effects.
4. If the identity already completed, acknowledge without repeating side effects or
   claiming to return an outcome that was not persisted. A competing transaction
   observes the unique-conflict result after the owner commits; it does not wait on a
   lease or stale claim.
5. Apply a handler whose state transition is safe to repeat. Use a natural idempotency
   key or a version/precondition check for effects outside the local store.
6. Persist the handler's changes and completed-inbox state atomically, then acknowledge.

Do not call a handler "idempotent" because the final row looks unchanged. Check
emails, payments, downstream commands, counters, notifications, and external writes
for duplicate effects. Where an external effect cannot be made idempotent, persist a
durable intent and reconcile its status rather than guessing after a timeout.

## Retry, Replay, And Failure

Classify failures before choosing the response:

| Failure | Default action | Evidence or stop condition |
|---|---|---|
| Temporary broker/database/network issue | Bounded retry with backoff and jitter | Attempt count, age, and queue lag remain within budget |
| Concurrency or serialization conflict | Roll back the unit of work and retry the whole operation | Finite attempts; preserve the original correlation context |
| Invalid or unauthorized event | Do not retry; quarantine and alert the owner | Payload, producer, and reason are available without leaking secrets |
| Poison message or deterministic handler bug | Move to a dead-letter/quarantine path after policy limits | Repair or replacement is tested before replay |
| Unknown schema version or gap | Pause or route to compatibility handling | Contract owner resolves version/ordering decision |
| Publish succeeded but acknowledgement was lost | Republish safely; consumer deduplication resolves the duplicate | Stable event identity and duplicate metrics |

Replay is a controlled operation, not a blind retry loop. Record the source position
or event IDs, selection criteria, handler version, destination, operator, and expected
side effects. Use the same consumer identity and inbox semantics by default. A fresh
consumer scope deliberately defeats inbox deduplication and must be restricted to
handlers proven side-effect-safe or routed through a repair/compensation path; it is
not safe for payments, refunds, or other irreversible effects. Make the stop condition
explicit. If handlers are not deterministic across versions,
use a versioned translator or a new repair command instead of replaying old payloads
through changed rules.

## Observability And Tests

Instrument the lifecycle with stable dimensions such as service, event type, producer,
consumer, schema version, result class, and deployment version. Useful signals include
outbox age and backlog, publish attempts and failures, inbox duplicate rate, handler
latency, retry counts, dead-letter volume, replay volume, and consumer lag. Propagate
trace/correlation identifiers, but redact payloads, credentials, and sensitive fields.

Test the smallest useful unit at each boundary:

- Unit-test aggregate invariants and the exact domain facts emitted for successful
  transitions; no broker or database is needed.
- Integration-test that state and outbox rows commit together, and that a rollback
  leaves neither durable effect.
- Test relay crashes and duplicate publication, then verify consumer deduplication.
- Test handler retry, permanent failure, quarantine, schema mismatch, replay, and
  acknowledgement ordering against a real or production-compatible broker/store.
- Assert observability fields and alert inputs for lag, age, duplicate, and poison paths.

## Ownership Boundary

`programming-principles` owns bounded contexts, aggregates, domain language, domain
events as DDD concepts, repositories, and anti-corruption guidance. This reference
only explains how those decisions become application and infrastructure behavior.
`api-design-and-evolution` owns event names, envelopes, compatibility, ordering scope,
retention, and consumer-facing delivery semantics. `site-reliability-engineering`
owns SLOs and paging policy; `secure-software-engineering` owns threat modeling,
authorization, and secure logging.
