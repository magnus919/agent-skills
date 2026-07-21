# OBEY Designing Data-Intensive Applications by Martin Kleppmann

## Purpose

This repository follows **Designing Data-Intensive Applications** in the sense of Martin Kleppmann:
design systems around explicit trade-offs in reliability, scalability, maintainability, consistency, and data flow.

All code generation, edits, and reviews must optimize for:
- explicit data and consistency semantics
- idempotent and replay-safe processing
- clear ownership of truth
- durable boundaries between storage, messaging, and computation
- schema evolution awareness
- realistic distributed systems assumptions

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

Data systems are defined by trade-offs.
When uncertain, make those trade-offs explicit instead of hiding them behind vague abstractions.

Always ask:
1. what is the source of truth?
2. what are the consistency expectations?
3. what happens on retries, duplicates, reordering, and partial failure?
4. how does the data evolve over time?
5. where is state durable, cached, derived, or ephemeral?

Do not design distributed behavior as if everything were local, ordered, and exactly once.

---

## Reliability Rules

1. Treat crashes, partial writes, duplicate work, timeouts, and stale reads as normal design inputs.
2. Make write acknowledgment semantics explicit.
3. Avoid hidden assumptions about durable success.
4. Design for restart, replay, and partial failure recovery.

Anti-patterns (MUST NOT):
- side effects that cannot be retried safely
- no distinction between accepted, persisted, and applied
- assuming one successful response means all downstream effects succeeded

---

## Scalability and Maintainability Rules

1. Describe load with concrete parameters before changing architecture.
2. Describe performance with latency, throughput, percentiles, and tail behavior where they matter.
3. Do not claim scalability from node count alone; identify the bottleneck, access pattern, and contention point.
4. Keep operability, simplicity, and evolvability as first-class design goals.
5. Prefer designs that make production behavior inspectable and changeable over opaque clever mechanisms.
6. Avoid accidental complexity from unnecessary distribution, premature heterogeneity, or hidden coupling.

---

## Data Model and Storage Rules

1. Choose storage shape based on access patterns, consistency needs, and update behavior.
2. Do not force one storage pattern onto all workloads.
3. Keep the ownership of each dataset explicit.
4. Distinguish primary data from indexes, caches, projections, and search copies.

### Source of Truth
For every important piece of data, identify:
- primary owner
- derived copies
- replication path
- update path
- consistency expectation

Anti-patterns (MUST NOT):
- many writable copies with no ownership
- cache quietly becoming the real source of truth
- denormalized copies with no repair strategy

---

## Query Model and Data Shape Rules

1. Choose relational, document, graph, key-value, or analytical models according to relationships, query needs, update locality, and evolution pressure.
2. Do not use a document model when many-to-one or many-to-many relationships require awkward duplication or application-side joins.
3. Do not force a relational shape when data is naturally self-contained and usually accessed together.
4. Use declarative query languages where they make intent clearer and leave optimization to the engine.
5. Use graph models when relationships are first-class and traversal is central.
6. Treat Cypher, SPARQL, Datalog, SQL, MapReduce, and application code as different expression choices with different maintainability and optimization tradeoffs.

---

## Storage Engine and Indexing Rules

1. Match indexing strategy to write pattern, read pattern, range scans, update cost, and recovery needs.
2. Use log-structured storage, SSTables, and LSM-tree style approaches when write throughput and sequential writes are the dominant fit.
3. Use B-tree style indexes when ordered access, point lookups, and mature transactional behavior fit the workload.
4. Treat secondary indexes as separate data structures with write amplification, partitioning, and consistency costs.
5. Distinguish OLTP access from analytical workloads; do not force one layout to serve both well.
6. Use column-oriented storage, compression, sort order, materialized views, or cubes only when analytical access patterns justify them.
7. Keep in-memory assumptions explicit; memory residency is a performance strategy, not a durability model.

---

## Consistency Rules

1. Be explicit about read-after-write expectations.
2. Be explicit about staleness tolerance.
3. Be explicit about conflict handling.
4. Use strong consistency only where the product truly requires it.
5. Use eventual consistency intentionally, not accidentally.

### Write Semantics
Document or encode:
- when a write is durable
- when it is visible
- whether readers may see stale data
- how conflicts are detected or resolved

Anti-patterns (MUST NOT):
- “eventual consistency” used as a slogan instead of a contract
- stale-read bugs blamed on infrastructure with no product decision behind them
- no conflict model for concurrent updates

---

## Idempotency and Replay Rules

1. Handlers of commands, jobs, and events must tolerate retries where delivery or acknowledgment is uncertain.
2. Prefer deduplication keys or naturally idempotent state transitions.
3. Design processing to survive replay after crashes.
4. Never assume exactly-once delivery unless the system boundary truly provides it and the design proves it.

Anti-patterns (MUST NOT):
- duplicate billing/order/send on retry
- handlers with non-repeatable side effects and no guard
- event processors depending on “it probably won't happen twice”

---

## Ordering Rules

1. Do not assume global order in distributed systems.
2. Require only the minimum ordering guarantees the business logic actually needs.
3. When ordering matters, define its scope:
   - per key
   - per stream
   - per partition
   - per record or entity whose history is being updated
4. Keep ordering-sensitive logic close to the key or stream that defines the order.

Anti-patterns (MUST NOT):
- implicit reliance on total ordering
- out-of-order events corrupting state because no versioning or sequence policy exists
- parallel consumers updating the same key with no ordering plan

---

## Event, Log, and Stream Rules

1. Distinguish commands, events, and materialized views clearly.
2. Events describe facts that happened; commands request action.
3. Logs and streams are durable histories, not merely transport pipes.
4. Consumers must tolerate lag, duplicates, restart, and replay.
5. Derived projections must be rebuildable where feasible.

### Event Design
- use stable identifiers
- include enough metadata for correlation and replay
- version payloads carefully
- keep semantics explicit

Anti-patterns (MUST NOT):
- event payloads tied to one serializer or internal object layout
- projections that cannot be rebuilt
- assuming consumers keep up forever

---

## Schema Evolution Rules

1. Schemas will change; plan for it.
2. Version contracts intentionally.
3. Prefer backward- and forward-compatible changes where possible.
4. Keep old readers and writers in mind during rollout.
5. Distinguish internal refactors from contract changes.

Anti-patterns (MUST NOT):
- breaking payloads or DB semantics without migration strategy
- reusing fields with new meaning
- silently changing enum or status semantics across services

---

## Encoding and Data Flow Rules

1. Choose encoding formats by compatibility needs, schema guarantees, readability, size, and language independence.
2. Do not rely on language-specific serialization for long-lived or cross-service data.
3. Treat JSON, XML, binary encodings, Thrift, Protocol Buffers, and Avro as contract choices with different schema-evolution tradeoffs.
4. Define reader and writer compatibility during rolling upgrades.
5. Keep database writes, service calls, and asynchronous messages explicit about who reads old and new formats during migration.
6. Avoid RPC designs that hide network failure, version skew, latency, or partial failure behind local-call syntax.

---

## Partitioning and Locality Rules

1. Keep data and work colocated by the key that most often drives consistency or aggregation.
2. Partition by a workload-relevant key, not by convenience alone.
3. Be explicit about hot-key risk and skew.
4. Design cross-partition operations carefully.

Anti-patterns (MUST NOT):
- partitioning that makes every common query cross-node
- no plan for skew or hotspots
- requiring cross-partition transactions for ordinary operations

---

## Replication Rules

1. Choose leader-follower, multi-leader, or leaderless replication according to write topology, failure tolerance, latency, and conflict handling.
2. Be explicit about synchronous and asynchronous replication tradeoffs.
3. Define behavior during node outages, follower catch-up, failover, and reconfiguration.
4. Preserve read-your-writes, monotonic reads, and consistent prefix reads only when the product or workflow requires them and the design provides them.
5. Do not rely on quorum formulas without checking stale reads, sloppy quorums, hinted handoff, and concurrent writes.
6. Make conflict detection and resolution explicit for concurrent writes.

---

## Transaction Rules

1. Use local transactions where they solve a real consistency problem cleanly.
2. Avoid distributed transactions as a default coordination strategy.
3. When cross-boundary coordination is required, define the commit, recovery, reconciliation, and failure semantics explicitly.
4. Make atomicity scope explicit.

### Isolation and Invariants
- Know whether read committed, snapshot isolation, serial execution, two-phase locking, or serializable snapshot isolation is required for the invariant.
- Protect against lost updates, write skew, and phantoms where application correctness depends on them.
- Do not accept weaker isolation for correctness-critical invariants without a deliberate design that preserves the invariant another way.

Anti-patterns (MUST NOT):
- multi-system two-phase coordination by default
- side effects emitted outside transactional boundaries with no repair path
- pretending asynchronous side effects are atomic because they “usually happen”

---

## Derived Data Rules

1. Treat indexes, search copies, caches, and read models as derived data unless they are explicitly authoritative.
2. Derived data must be repairable, rebuildable, or re-syncable.
3. Know how lag affects user-visible behavior.
4. Keep derivation pipelines observable.

Anti-patterns (MUST NOT):
- no way to rebuild projections
- no lag visibility
- mixing primary writes directly into derived stores with no ownership model

---

## Distributed Fault, Clock, and Consensus Rules

1. Treat network delay, packet loss, partitions, duplicated messages, and arbitrary pauses as normal distributed-system risks.
2. Do not infer remote failure or success from timeout alone.
3. Use monotonic clocks for measuring elapsed time; do not use wall clocks for ordering unless clock assumptions are explicit and safe.
4. Do not rely on synchronized clocks for correctness unless uncertainty bounds and failure behavior are part of the design.
5. Treat majority decisions, leases, locks, and leadership as assumptions that need a fault model.
6. Use linearizability only where a single up-to-date value is required and the availability/latency cost is acceptable.
7. Use total order broadcast, atomic commit, or consensus only when the coordination problem truly requires it.
8. Make membership and coordination-service dependencies explicit; they are part of the system design, not invisible plumbing.

---

## Batch and Stream Processing Rules

1. Design batch jobs so inputs, outputs, and intermediate state can be recomputed or recovered.
2. Keep external side effects out of replayable jobs unless idempotency is explicit.
3. Use MapReduce-style, dataflow, or high-level batch APIs according to join strategy, intermediate materialization, and operational needs.
4. Distinguish event time, processing time, and ingestion time in stream processing.
5. Define windowing, late data, joins, state storage, checkpoints, and fault tolerance for streams that affect correctness.
6. Treat change data capture, event sourcing, and log-based synchronization as ways to derive and propagate data, not as magic consistency.
7. Define at-most-once, at-least-once, or exactly-once processing guarantees for each source-to-sink path.

---

## API and Service Boundary Rules

1. Service boundaries must reflect data ownership and update semantics.
2. Do not split one tightly consistent business concept across many services casually.
3. Avoid chatty cross-service joins on hot paths.
4. Contracts must encode identifiers, versions, and failure semantics clearly.

---

## Review Rules

When reviewing code, actively look for:
- hidden assumptions about ordering
- hidden assumptions about exactly-once delivery
- lack of idempotency
- no source-of-truth ownership
- broken schema evolution practices
- no versioning or sequencing where concurrency matters
- side effects that cannot be repaired
- write paths that update several stores with unclear guarantees
- projections that cannot be rebuilt
- partitioning blind to locality or hotspots

---

## Forbidden Patterns

### Exactly-Once Wishful Thinking
- assuming a broker or queue magically prevents all duplicates
- writing non-idempotent handlers without safeguards

### Hidden Consistency Contract
- readers and writers disagreeing on freshness requirements
- stale or conflicting behavior treated as incidental instead of product design

### Uncoordinated Multi-Writes
- writing to several authorities in one operation with no atomicity or repair strategy
- side effects sent before durable state with no recovery path

### Schema Drift by Accident
- changing payload meaning without versioning
- reusing fields for new concepts
- no rollout compatibility strategy

---

## Code Generation Rules

When generating code, default to:
1. explicit identifiers and ownership
2. explicit idempotency where retries or duplicates can happen
3. explicit versioning or conflict strategy where ordering matters
4. explicit distinction between authoritative and derived data
5. repairable or rebuildable downstream state
6. compatibility-aware schema changes
7. observability for lag, retries, and failures

Avoid by default:
- assuming strict global order
- exactly-once promises with no proof
- writing the same fact into several places as if they were one transaction
- treating streams and queues as fire-and-forget

---

## Testing Rules

1. Test duplicate delivery handling.
2. Test out-of-order event or message handling where applicable.
3. Test replay safety.
4. Test conflict resolution or optimistic concurrency behavior.
5. Test schema compatibility when contracts evolve.
6. Test rebuild or repair of derived views where that capability exists.

---

## Review Checklist

Before finalizing any change, verify:
- Is the source of truth explicit?
- Are consistency expectations explicit?
- Is the code safe under retry or duplicate delivery?
- Is ordering dependency explicit and scoped?
- Can derived data be rebuilt or repaired?
- Is schema evolution considered?
- Is atomicity scope honest?
- Did we avoid exactly-once wishful thinking?
- Are service boundaries aligned with data ownership?
- Are lag and failure observable?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, prefer the design that:
1. makes data ownership explicit
2. makes consistency semantics explicit
3. survives retries, duplicates, and replay
4. supports evolution without silent breakage
5. treats distributed systems trade-offs honestly

Do not hide distributed complexity behind local-looking code.
