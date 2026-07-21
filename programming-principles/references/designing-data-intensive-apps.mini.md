# OBEY Designing Data-Intensive Applications by Martin Kleppmann

## When to use

Use for systems where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived-data maintenance.

## Primary bias to correct

Do not design distributed data behavior as if every write, read, queue, cache, replica, clock, and downstream side effect were local, ordered, fresh, and exactly once.

## Decision rules

- Make core trade-offs explicit: source of truth, consistency expectation, retry behavior, duplicate and reordered work, partial failure, data evolution, and whether state is durable, cached, derived, or ephemeral.
- Treat crashes, partial writes, duplicate work, timeouts, stale reads, and unknown downstream success as normal inputs. Distinguish accepted, persisted, applied, and durable success.
- Describe load and performance with concrete request rates, data volume, access patterns, latency, throughput, percentiles, bottlenecks, contention, and tail behavior before changing architecture.
- Choose data models, query models, and ownership boundaries from relationships, access patterns, consistency needs, update locality, evolution pressure, and whether data is primary or derived.
- Match storage engines, indexes, and analytical layouts to write patterns, read patterns, range scans, recovery needs, write amplification, OLTP-vs-analytics separation, and memory-vs-durability assumptions.
- Treat indexes, caches, search copies, read models, materialized views, and denormalized copies as derived data with explicit propagation, lag, observability, repair, and rebuild paths.
- Define write semantics: when a write is durable, when it is visible, whether stale reads are allowed, which conflicts can happen, and how conflicts are detected or resolved.
- Make commands, jobs, events, batch jobs, and stream processors safe under retry and replay with deduplication keys, naturally idempotent transitions, or an explicit transactional recovery contract.
- Preserve only the ordering the business logic actually needs. Scope it per key, stream, partition, record, entity history, or stronger contract, and keep ordering-sensitive logic close to that scope.
- Separate commands, events, durable logs, streams, and materialized views. Events describe facts; consumers must tolerate lag, duplicates, restart, replay, stable identifiers, correlation metadata, and versioned payloads.
- Design schemas, encodings, APIs, messages, events, and database changes as evolving contracts across old readers, old writers, old data, in-flight messages, rolling upgrades, and cross-service formats.
- Choose replication topology from write topology, latency, failure tolerance, lag, failover, reconfiguration, conflict handling, read-your-writes, monotonic-read, consistent-prefix, quorum, and convergence needs.
- Partition by workload-relevant locality and consistency keys, with hot-key, skew, routing, secondary-index, rebalancing, and cross-partition-operation costs explicit.
- Match transactions and isolation to invariants. Make atomicity scope, commit behavior, recovery, reconciliation, lost-update, write-skew, phantom, and side-effect repair semantics explicit.
- Treat network delay, packet loss, partitions, duplicate messages, pauses, stale leaders, timeouts, wall-clock uncertainty, leases, locks, majorities, and leadership as assumptions needing a fault model.
- Use linearizability, total order broadcast, atomic commit, or consensus only where the coordination problem truly requires agreement and the availability or latency cost is acceptable.
- Make batch and stream processing recomputable and recoverable: define inputs, outputs, intermediate state, checkpoints, external side effects, event time, processing time, ingestion time, windows, late data, joins, and source-to-sink guarantees.
- Align service boundaries with data ownership and update semantics. Do not casually split one tightly consistent business concept across services or put chatty cross-service joins on hot paths.

## Trigger rules

- When changing a write path, state the source of truth, consistency boundary, durability point, visibility point, downstream effects, rollback or repair path, and behavior after timeout or unknown success.
- When adding or changing a cache, index, projection, search copy, read model, warehouse, or denormalized field, define ownership, propagation, staleness, write cost, lag visibility, rebuild, and repair.
- When changing a schema, API, message, event, enum, status, or payload meaning, plan compatibility for old readers, old writers, old stored data, old messages, new writers, rollout, and migration.
- When adding retries, jobs, consumers, queues, CDC, event sourcing, stream processors, or replayable batch work, prove duplicate, replay, ordering, retention, side-effect, and recovery safety.
- When routing reads to replicas or using asynchronous replication, identify read-your-writes, monotonic-read, consistent-prefix, staleness, catch-up, failover, and conflict expectations before allowing the read.
- When partitioning data or work, test the ordinary query path for locality, skew, hot keys, routing metadata, rebalancing cost, secondary-index behavior, and cross-partition coordination.
- When choosing transaction isolation or weakening consistency, map each anomaly to the invariant it can break and add serializable isolation, locks, compare-and-set, versioning, reconciliation, or another compensating design where needed.
- When using timestamps, leases, locks, leadership, majority decisions, coordination services, or consensus-like mechanisms, define the clock assumption, quorum/session semantics, stale-authority behavior, and fencing.
- When reviewing or testing data-intensive code, look specifically for hidden source-of-truth ownership, missing idempotency, accidental exactly-once assumptions, unscoped ordering, schema drift, unrebuildable projections, unclear multi-writes, and unobservable lag or failure.

## Final checklist

- Source of truth and derived representations are explicit.
- Consistency expectations, durability points, visibility points, staleness, and conflict rules are concrete.
- Retries, duplicate delivery, replay, reordering, timeouts, crashes, and unknown success are handled.
- Schemas, encodings, APIs, messages, events, enums, and statuses evolve safely across mixed versions.
- Storage, indexing, replication, partitioning, routing, and analytical layouts match the actual workload.
- Transaction isolation and coordination choices protect the named invariants.
- Events, logs, streams, batch jobs, and projections are replayable or have explicit repair paths.
- Service boundaries follow data ownership and update semantics.
- Lag, retries, failures, rebuilds, and repair paths are observable.
- The design avoids exactly-once wishful thinking and hidden distributed-system contracts.
