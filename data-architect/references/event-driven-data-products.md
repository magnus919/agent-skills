# Event-Driven Data Products

Use this guide when operational events, change streams, or event-oriented products feed analytical, ML, or cross-domain consumers. It covers architecture decisions; implementation belongs to `data-engineering` and interface contract semantics belong to `api-design-and-evolution`.

## Choose the Product Shape

An event stream, a current snapshot, and a historical analytical table answer different questions. For each consumer, decide whether it needs:

- **Events:** append-oriented facts for reacting to changes or rebuilding a view
- **Snapshots:** the latest state for query consumers that should not replay history
- **History:** time-aware records for audit, trend, and backfill use cases
- **A combination:** a stream for incremental consumers plus a queryable snapshot for recovery and exploration

Record the source of truth, event time, publication time, identity key, ordering scope, retention, and whether the product is immutable. Do not promise an event stream as a universal replacement for queryable data.

## Producer and Consumer Responsibilities

The producer owns the meaning and publication behavior of facts it authors. It must identify what changed, preserve the product's declared time semantics, publish quality and freshness signals, and communicate lifecycle changes. Consumers own their projections, checkpoints, deduplication state, and migration work.

The architecture must state whether delivery is at-most-once, at-least-once, or effectively-once for the use case. Avoid claiming exactly-once behavior without defining the boundary at which it is verified.

## Failure and Recovery Decisions

For each product, answer:

1. What happens when delivery is delayed, duplicated, reordered, or unavailable?
2. Can a consumer rebuild from retained events, a snapshot, or a separate backfill source?
3. How are late events reconciled with already published aggregates?
4. Who detects a freshness or completeness breach, and who communicates it?
5. What is the safe behavior when a consumer cannot upgrade before a producer change?
6. How are poison records quarantined without silently dropping business facts?

Prefer explicit replay and reconciliation paths over an assumption that a consumer can simply restart. Recovery cost, retention, and replay throughput are architecture inputs.

## Compatibility and Lifecycle

Define compatibility by consumer impact, not by a label alone. A change may be additive at the schema level but still break a consumer through changed meaning, units, defaults, cardinality, ordering, or timing. Capture:

- compatible and incompatible changes;
- announcement and overlap period;
- version or translation strategy;
- consumer inventory and usage evidence;
- deprecation owner and removal condition;
- historical correction and backfill policy.

Route the formal event schema, serialization, API, webhook, and compatibility contract to `api-design-and-evolution`. This skill supplies the consumer and architecture decisions that the contract must support.

## Access Modes and Planes

Separate the operational plane, where producers and reactive consumers exchange timely facts, from the analytical plane, where data is validated, reconciled, retained, and queried. Decide whether consumers pull from a product store, subscribe to events, or use both. Make the latency, freshness, availability, cost, and security consequences visible for each mode.

An event-driven design is justified when the business benefit of timely change exceeds the cost of retention, replay, monitoring, compatibility, and operating the path. Batch or micro-batch remains a valid design when those costs are not justified.
