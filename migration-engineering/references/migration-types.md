# Migration Types

Load this file when classifying a migration before selecting patterns: each
type has materially different compatibility, correctness, and recovery
characteristics, and real-world migrations often combine types (a service
extraction is usually a combined infrastructure/service, API, and data
migration).

## Schema migration

A change to a database schema, message format, or serialization contract.
**Compatibility:** forward compatibility (old readers tolerate new writers) and
backward compatibility (new readers tolerate old writers) are the central design
constraints. **Correctness:** verified by dual-reading or shadow-traffic
comparison — the new schema must produce equivalent results for the same input.
**Rollback:** possible if the schema change is purely additive (expand phase);
destructive changes (drop column, rename, change type) require a multi-step
expand/contract sequence with a compatibility window where both old and new
schemas coexist before the old is removed.

## Data migration

Movement or transformation of data between stores, representations, or
ownership boundaries. **Compatibility:** the old and new data representations
must coexist during the transition; consumers may read from either or both.
The backfill strategy (full, incremental, or streaming) determines how long
the dual-read window lasts. **Correctness:** requires reconciliation — a
record-level or aggregate comparison between source and target to verify
completeness and accuracy before cutover. **Rollback:** depends on whether the
old store remains writable and current during the transition. If the old store
is kept in sync (dual-write), rollback is reversing the cutover. If the old
store was dropped or made read-only, rollback requires restore from backup.

## API migration

A change to the contract between a provider and its consumers — versioning,
protocol, schema, or endpoint topology. **Compatibility:** defined by the
provider's compatibility policy (e.g., "additive changes are backward-compatible;
removals require a deprecation window"). The compatibility window is measured
in consumer migration time — how long consumers need to move from the old
interface to the new one. **Correctness:** verified by consumer-side testing,
shadow-traffic replay, and error-rate comparison between old and new interfaces.
**Rollback:** the old interface must remain available and supported throughout
the deprecation window; rolling back means reverting the deprecation notice
and keeping the old interface live. Once the old interface is removed, rollback
requires deploying it again — a restore or redeploy path, not a simple reversal.

## Infrastructure and service migration

Moving workloads, services, or infrastructure between environments, platforms,
or ownership domains. **Compatibility:** network, identity, and data-plane
continuity must be maintained. DNS, certificates, service discovery, and
security boundaries are the primary compatibility surface. **Correctness:**
verified by traffic shifting, canary deployment, and service-level objective
(SLO) monitoring during the transition. **Rollback:** depends on the migration
topology. Lift-and-shift with the old environment preserved is reversible;
in-place replacement without a preserved old environment may be irreversible
or require a full redeploy (roll-forward/restore).

## Service extraction

A service extraction is usually a combined infrastructure/service, API, and data
migration. Before the expand phase, record the proposed capability's boundary
evidence, coupling, data ownership, callers, and failure behavior. Select the
least disruptive transition pattern that creates evidence: strangler routing,
branch by abstraction, an anti-corruption boundary, CDC, parallel run, or a
combination with distinct roles. Keep the old path selectable until comparison,
reconciliation, customer-impact, and operational gates pass.

The extraction assessment must also record explicit reasons to retain a modular
monolith. If the boundary still needs shared writes, frequent cross-boundary
transactions, unobservable consumers, or has no tested recovery path, stop and
recommend modular improvement or request more evidence rather than creating a
distributed shape by default. Route target-boundary justification to the
[`software-architecture`](../software-architecture/SKILL.md) decision owner;
migration-engineering owns the safe current-to-target transition once authorized.

For transition-pattern selection detail, load
[`service-extraction-patterns.md`](service-extraction-patterns.md).
