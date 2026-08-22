# Data Ownership and Workflow Analysis

Use this reference when architecture behavior depends on who may change data, how multi-step work completes, or how the system repairs partial outcomes.

## Data authority map

For every important entity or fact, identify:

- authoritative store and write path;
- schema or semantic owner;
- allowed writers and readers;
- derived copies, caches, indexes, exports, and event projections;
- invariant owner and validation point;
- retention, deletion, replay, and backfill behavior;
- evidence for the map and unresolved conflicts.

Distinguish “source of truth” from “most frequently queried copy.” A projection may be operationally critical without owning the fact. Shared tables with multiple business writers are a strong coupling signal and require explicit invariant ownership.

## Distributed transaction trace

Trace each multi-resource operation as a timeline, not just a component diagram. Record the trigger, writes, reads, emitted messages, acknowledgement points, timeout/retry behavior, and visible intermediate states. Then answer:

1. What must be atomic, and where is that atomicity actually enforced?
2. What can be repeated safely, and what idempotency key or deduplication evidence supports that claim?
3. What may commit in one resource while another fails?
4. Who detects and repairs the split state?
5. What does the user or downstream consumer observe while repair is pending?

Do not describe a workflow as transactional merely because one database call is transactional. Name the boundary of each transaction and the remaining business consistency mechanism.

## Orchestration and choreography

Classify the workflow from observed control flow:

- **Orchestration:** a named coordinator chooses steps, tracks progress, applies timeouts, and exposes completion or compensation state.
- **Choreography:** participants react to facts or commands without one central coordinator; trace implicit ordering, duplicate handling, and how operators discover a stuck process.
- **Hybrid:** central policy or admission with event-driven local reactions.

The labels are descriptive. Evaluate observability, ownership, coupling, and recovery rather than treating either shape as inherently superior.

## Failure and reconciliation

For each boundary crossing, enumerate lost, delayed, duplicated, reordered, rejected, malformed, and permanently unavailable outcomes. For each outcome record detection signal, retry policy, idempotency behavior, dead-letter or quarantine path, operator owner, user-visible state, and recovery evidence.

Reconciliation is a first-class workflow, not a batch apology. Define its comparison keys, source precedence, safe repair action, conflict policy, audit trail, rate limits, and completion proof. If no reconciliation path exists, mark the workflow as an unresolved integrity risk. Route detailed event/API contract design to `api-design-and-evolution` and implementation mechanics to `data-engineering` or `backend-engineering`.
