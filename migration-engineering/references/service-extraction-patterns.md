# Service Extraction Patterns

Load this reference when a migration moves a capability out of a modular or
distributed monolith into an independently deployed service. It helps choose a
transition shape after the candidate boundary has been identified; it does not
decide whether the organization should decompose the system.

## Boundary evidence before sequencing

Treat a proposed extraction seam as a hypothesis. Record evidence for the
capability, not enthusiasm for a deployment style:

- **Capability coherence:** the behavior has a recognizable business purpose,
  stable language, and a bounded set of invariants.
- **Data ownership:** the candidate can name the records it owns, the writers,
  the authoritative source, retention rules, and the queries that must cross
  the proposed boundary.
- **Change seam:** the capability changes, scales, is secured, or is released
  on a different cadence from its neighbors. A high edit count alone is not
  sufficient; show who changes what and which releases are coupled.
- **Coupling shape:** map synchronous calls, shared tables, foreign keys,
  transactions, events, batch jobs, caches, feature flags, and operational
  dependencies. Include temporal coupling such as required ordering and
  deployment coupling such as coordinated releases.
- **Consumer surface:** identify callers, data consumers, operators, external
  partners, and customer-visible workflows. A seam with one clear owner is
  easier to transition than one with many unowned consumers.
- **Failure boundary:** state which failures may be isolated and which business
  invariants currently depend on one local transaction.

If the evidence cannot identify a data owner, a stable contract, or a bounded
failure behavior, stop at discovery. Do not manufacture a service boundary to
make the plan look complete. Route the decomposition decision and target
boundary to the repository's software-architecture owner when that skill is
available; this skill begins once a current-to-target transition is authorized.

## Pattern selection

Choose one primary transition pattern and name any supporting pattern. The
default is the least disruptive shape that creates useful evidence.

| Pattern | Use when | Main evidence | Main risk | Reversal posture |
|---|---|---|---|---|
| **Strangler routing** | A request path can move endpoint-by-endpoint or capability-by-capability | Traffic and outcome comparisons by route and consumer | Hidden callers bypass the route or semantics differ | Usually strong while the old path remains live |
| **Branch by abstraction** | Callers can be placed behind a stable internal interface before the implementation moves | Contract tests and parity checks at the abstraction | The abstraction becomes a new leaky coupling layer | Strong while the old implementation remains selectable |
| **Anti-corruption boundary** | The new service needs a different model or vocabulary from the monolith | Explicit translation rules, ownership, and rejected legacy concepts | Translation hides unresolved ownership or loses meaning | Good if translation is isolated and old model remains available |
| **Change-data capture (CDC)** | The source database remains authoritative while a target is populated or kept current | CDC lag, ordering, replay, dead-letter handling, and reconciliation | Missed changes, schema drift, duplicate delivery, and unclear deletes | Good before source write ownership changes; weaker after contract |
| **Parallel run** | Both implementations can process the same inputs safely for comparison | Deterministic comparison, side-effect isolation, and mismatch triage | Duplicate side effects, non-determinism, and double cost | Strong only when the old result remains authoritative |

Do not present these as interchangeable synonyms. Routing changes where a
request is handled; abstraction changes which implementation callers invoke;
translation protects a model boundary; CDC moves changes; parallel run creates
comparison evidence. A plan may combine them, but should state the role of each.

## Sequencing a service extraction

Use the existing migration lifecycle and fill it with extraction-specific
decisions:

1. **Prove the seam.** Inventory callers, writes, reads, transactions, jobs,
   and customer journeys. Identify the source of truth and the invariant that
   must not be split accidentally.
2. **Make the old path selectable.** Add routing, an abstraction, or an
   adapter without changing the old behavior. Define the feature-flag or
   configuration owner and the interruption point.
3. **Establish the target contract.** Add the service interface and translate
   legacy concepts at the boundary. Route contract semantics and versioning to
   `api-design-and-evolution`; do not hide breaking changes in an adapter.
4. **Populate and synchronize data.** Choose full, incremental, or streaming
   backfill. If CDC or events are used, specify ordering, duplicates, deletes,
   replay, lag limits, schema compatibility, and dead-letter recovery. Route
   pipeline implementation to `data-engineering`.
5. **Compare before authority moves.** Use shadow reads or parallel execution
   with side effects disabled, or compare independently observable outcomes.
   Define mismatch categories and a stop rule before collecting results.
6. **Shift traffic or callers in bounded increments.** Every increment needs a
   precondition, customer-impact check, abort trigger, and recovery
   classification. Route rollout mechanics to `release-engineering` and SLO
   gates to `site-reliability-engineering`.
7. **Transfer ownership explicitly.** Declare when the target becomes the
   source of truth, which writers are disabled, and how stale old data is
   handled. Do not call a read switch an ownership transfer unless writes and
   reconciliation support that claim.
8. **Contract only after evidence.** Remove old routes, adapters, shared-table
   access, CDC feeds, flags, and credentials only after the compatibility and
   deprecation conditions pass. Classify each removal separately; expensive is
   not the same as irreversible.

## Coupling and data ownership checks

Before selecting CDC or dual-write, answer these questions:

- Is there one authoritative writer, or would two systems claim ownership?
- Can the invariant be enforced without a distributed transaction?
- Are updates, deletes, retries, and out-of-order changes represented?
- Can a CDC consumer replay from a known position and reconcile the result?
- Are reads allowed to observe bounded staleness, and who accepts it?
- Which queries currently join the candidate data with data outside the seam?
- What happens when the target is unavailable: queue, reject, serve old data,
  or degrade with a stated customer impact?
- Which old writes remain possible after target cutover, and how are they
  detected?

If the answers require frequent cross-boundary transactions, synchronous calls
in both directions, or shared writes with no clear authority, prefer a modular
monolith increment or branch-by-abstraction experiment. A distributed shape
that preserves the old coupling has added failure modes without buying an
independent boundary.

## Coexistence and reversibility record

For each phase, record:

| Concern | Required decision |
|---|---|
| Coexistence | Which old and new routes, readers, writers, schemas, and data stores are live together? |
| Authority | Which system is authoritative for each operation and data field? |
| Comparison | What is compared, with what tolerance, and what stops promotion? |
| Customer impact | What can users observe in latency, ordering, availability, or semantics? |
| Recovery | Is the step rollback, roll-forward, restore, or irreversible, and what is the tested procedure? |
| Exit condition | What metric, consumer state, or owner decision permits the next phase? |
| Cleanup | Which old dependency is removed, and is its removal reversible? |

Rollback is normally available while the old implementation remains
authoritative or selectable. Once writes are exclusive to the new store, the
old store is deleted, or the old contract cannot be redeployed, do not promise
rollback. Use roll-forward, restore, or irreversible classification as defined
in `references/recovery-classification.md`.

## When to keep a modular monolith

Recommend retaining or strengthening the modular monolith when evidence shows
that extraction would not create a meaningful boundary. Explicit reasons may
include:

- the capability shares invariants that need one local transaction;
- data ownership is contested or the proposed service would still share tables;
- callers are numerous, implicit, or not observable enough to migrate safely;
- the target would require synchronous calls in both directions for normal work;
- the expected scale, release cadence, security isolation, or team ownership
  difference is not material;
- the operation cannot tolerate the latency, partial failure, or eventual
  consistency introduced by the boundary;
- the migration has no tested recovery path within the accepted impact;
- the modular monolith can address the stated problem with module boundaries,
  dependency rules, an internal abstraction, or isolated runtime resources.

"Keep the monolith" is not a failure to decide. Record the evidence, the
modular improvement to make, the condition that would reopen extraction, and
the owner/date for reassessment. If the decision is unresolved, stop before
service creation and escalate rather than selecting a pattern by default.

## Specialist boundaries

- Target-boundary justification and architecture decomposition belong to
  [`software-architecture`](../../software-architecture/SKILL.md); this reference
  sequences an approved transition.
- API contract semantics and compatibility policy belong to
  `api-design-and-evolution`.
- CDC, backfill, schemas, and reconciliation implementation belong to
  `data-engineering`.
- Routing implementation, feature flags, and traffic promotion belong to
  `release-engineering` and `platform-engineering`.
- SLOs, error budgets, alerts, and incident response belong to
  `site-reliability-engineering`.
- Security boundary and authorization review belong to
  `secure-software-engineering`.
