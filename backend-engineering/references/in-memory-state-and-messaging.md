# Native state operations and stream consumers

Use when implementing service state, counters, leaderboards, atomic updates, or messaging on Valkey/Redis. Architecture and engine selection belong to `data-architect`; this guide turns an approved boundary into application behavior.

For an open-source-first choice, prefer Valkey's BSD licensing and community governance; do not assume Redis 8's AGPL option resolves the user's licensing or trust concern. This is the catalog's orientation for that audience, not a claim about business preferences. If the target is already Redis, respect its explicit identity and review compatibility before proposing a change. Pin engine, server/module versions and client library; RESP compatibility does not prove feature parity.

## Select the smallest native operation

| Required behavior | Candidate | Implementation boundary |
|---|---|---|
| Increment one integer | Native increment | Avoid client GET/add/SET races; define overflow/type-error handling |
| Update named object fields | Hash | Validate allowed fields and serialization; one field update is not a multi-object invariant |
| Membership or set intersection | Set | Bound cardinality and result size; server-side does not mean constant cost |
| Ranked leaderboard | Sorted set | Define tie order, bounded page size, score updates and retention |
| Ordered work/history | Stream | Define durability, retention, group ownership and duplicate-effect handling |
| Ephemeral live notification | Pub/Sub | Disconnection can lose messages; unsuitable as the only durable job channel |

Check the command-specific complexity: hash writes scale with fields supplied; a typical sorted-set range includes lookup plus returned members. Avoid broad “instant” claims and unbounded results. A list's end-operation cost does not supply acknowledgement, reclaim or durable job semantics by itself.

## Atomicity ladder

1. Prefer a native command when it expresses the whole invariant.
2. For read-dependent conditional updates, consider `WATCH` plus `MULTI`/`EXEC`; handle conflicts with bounded retries and a stable connection. Inspect per-command results, not only whether EXEC returned.
3. Use a short parameterized Lua script when server-local branching/composition is needed. Validate arguments and key types before the first mutation. Declare accessed keys; in Cluster, verify the shared slot boundary for all affected keys.
4. If the invariant spans independent slots, stores or external services, redesign the boundary or use the existing durable workflow/outbox method. A lock or script is not automatically a cross-system transaction.

Scripts isolate execution from interleaving, but block other work while running. Runtime failure after an earlier mutation does not automatically roll it back. MULTI/EXEC also does not supply relational rollback for execution-time command errors. Prevalidation reduces predictable failures; it does not prove all-or-nothing recovery. Define detectable partial states, invariant checks and repair/compensation. Keep scripts bounded in keys, iterations, payload size and execution time.

If a reply is lost after execution, the operation's outcome is ambiguous. Blindly retrying increments or external effects can duplicate them. Use a stable request identity and an application-owned deduplication/result protocol where needed; specify how long that identity survives and what recovery does. Pipelining reduces round trips; it is neither atomicity nor idempotency.

## Pub/Sub versus Streams

Pub/Sub is at-most-once live delivery: offline clients miss events. Use it for explicitly lossy notifications, or provide an independent authoritative resynchronization path.

For durable work with Streams:

1. Establish producer identity, event ID, ordering scope, retention, persistence and loss agreement. A stream data structure alone is not a durability guarantee.
2. Read through a consumer group, track pending deliveries and apply the handler through the existing inbox/idempotency boundary.
3. Persist required effects before acknowledging. An acknowledgement records processing state, not proof that an external payment/email happened exactly once.
4. Recover stalled pending work through a bounded, version-supported claim/reclaim policy; a new consumer reading only new messages does not recover another consumer's pending entries automatically.
5. Treat timeout/reclaim as possible duplicate execution. Use stable effect IDs, bounded retries and poison-message quarantine. A slow original worker can still be alive; ownership transfer alone is not fencing of external effects.
6. Reconcile retained history, pending IDs and sink effects after crashes. Define what happens if trimming removes payloads still needed by pending consumers. Monitor lag, pending age, retry count and duplicate effects separately.

Keep service event implementation in the existing event-driven reference; route public delivery contracts to `api-design-and-evolution`, pipeline ownership to `data-engineering`, runtime recovery to SRE and migration lifecycle to `migration-engineering`.

## Implementation record and completion

Record engine/version/client, key/type and invariant, slot scope, atomic mechanism, conflict/timeout behavior, partial-state repair, retention, acknowledgement point and focused boundary tests. Include cases for concurrent updates, error after first mutation, lost reply, consumer crash after effect/before ACK, stale worker after reclaim and trimmed pending payload. Complete when code and observed boundary evidence support the stated guarantees, or clearly hand off unverified runtime checks. Do not claim these documentation examples were executed.

## Sources

Checked 2026-11-03: [Valkey introduction](https://valkey.io/topics/introduction/), [INCR](https://valkey.io/commands/incr/), [HSET](https://valkey.io/commands/hset/), [ZRANGE](https://valkey.io/commands/zrange/), [transactions](https://valkey.io/topics/transactions/), [Lua](https://valkey.io/topics/eval-intro/), [Cluster](https://valkey.io/topics/cluster-tutorial/), [Pub/Sub](https://valkey.io/topics/pubsub/), [Streams](https://valkey.io/topics/streams-intro/) and [migration compatibility](https://valkey.io/topics/migration/). These support documented mechanisms; application effect guarantees need separate tests. For the licensing distinction, see [Valkey history](https://valkey.io/topics/history/) and [Redis licenses](https://redis.io/legal/licenses/).
