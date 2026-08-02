---
name: migration-engineering
description: >-
  Plan and execute safe cross-system migrations — schema, data, API, infrastructure,
  and service — with compatibility windows, dual-running, backfills, reconciliation,
  cutover, deprecation, and cleanup. Covers expand/contract, reversible and irreversible
  recovery paths, migration observability, correctness evidence, ownership, and
  customer impact. Do not use for single-technology quick fixes, tool-specific
  how-to guides, or migrations whose scope does not cross a system boundary; do not
  prescribe one migration technology or claim rollback is always possible.
license: MIT
compatibility: Platform-agnostic methodology. No runtime dependencies, API keys, or external services required.
metadata:
  tags: migration-engineering, data-migration, schema-migration, api-migration,
    infrastructure-migration, service-migration, expand-contract, compatibility-window,
    dual-running, backfill, reconciliation, cutover, deprecation, rollback,
    roll-forward, irreversible-migration
---

# Migration Engineering

Plan and execute safe migrations across system boundaries. A migration is any
change that moves data, schemas, interfaces, infrastructure, or services from a
current state to a target state while preserving correctness, availability, and
recoverability during the transition.

This skill owns the **cross-system migration method** — compatibility design,
staging, reconciliation, cutover, recovery, and deprecation. It does not own the
implementation details of any single technology or subsystem; those belong to
specialist skills.

## When to use

Load this skill when the task involves:

| Trigger | Example |
|---|---|
| A schema change that must not break existing readers or writers | "Add a non-nullable column to a high-traffic table with zero downtime" |
| A data migration between stores or representations | "Migrate user profiles from Postgres to a dedicated service with its own database" |
| An API version migration with a deprecation window | "Move consumers from v1 REST to v2 GraphQL over six months" |
| An infrastructure or service migration | "Shift a workload from self-hosted VMs to a managed platform across regions" |
| A cross-system change requiring dual-running and reconciliation | "Replace the legacy billing engine with a new one while keeping both in sync" |
| Planning cutover, rollback, or irreversible steps for a migration | "Define the recovery strategy for the warehouse schema migration" |

## When not to use

- **Single-technology quick fixes** — if the change is confined to one system
  with no compatibility window, no dual-running, and no cross-system coordination,
  use the relevant specialist skill directly (e.g., [data-engineering](../data-engineering/SKILL.md)
  for a simple DDL change, [api-design-and-evolution](../api-design-and-evolution/SKILL.md)
  for a single-endpoint deprecation).
- **Tool-specific how-to guides** — this skill provides the method, not
  vendor-specific instructions. It does not prescribe one migration technology, one
  database engine, one API gateway, or one infrastructure platform.
- **Migrations without a system boundary** — in-place refactors, code rewrites
  that don't cross a data or interface boundary, or single-service configuration
  changes are not migration-engineering scope.
- **Guaranteeing rollback** — this skill does not claim rollback is always possible.
  Some migrations include steps that are irreversible; the method requires
  identifying those steps explicitly and planning acceptance, communication, and
  contingency rather than implying a false safety net.

## Migration type classification

Migrations differ materially in their compatibility, correctness, and recovery
characteristics. Classify the migration before selecting patterns.

### Schema migration

A change to a database schema, message format, or serialization contract.
**Compatibility:** forward compatibility (old readers tolerate new writers) and
backward compatibility (new readers tolerate old writers) are the central design
constraints. **Correctness:** verified by dual-reading or shadow-traffic
comparison — the new schema must produce equivalent results for the same input.
**Rollback:** possible if the schema change is purely additive (expand phase);
destructive changes (drop column, rename, change type) require a multi-step
expand/contract sequence with a compatibility window where both old and new
schemas coexist before the old is removed.

### Data migration

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

### API migration

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

### Infrastructure and service migration

Moving workloads, services, or infrastructure between environments, platforms,
or ownership domains. **Compatibility:** network, identity, and data-plane
continuity must be maintained. DNS, certificates, service discovery, and
security boundaries are the primary compatibility surface. **Correctness:**
verified by traffic shifting, canary deployment, and service-level objective
(SLO) monitoring during the transition. **Rollback:** depends on the migration
topology. Lift-and-shift with the old environment preserved is reversible;
in-place replacement without a preserved old environment may be irreversible
or require a full redeploy (roll-forward/restore).

## Core workflow

### 1. Classify and scope the migration

Determine which migration type(s) apply. A real-world migration often combines
types — for example, a service extraction includes both a data migration and an
API migration. Document:
- The current state, target state, and system boundary being crossed.
- The migration type(s) and their compatibility requirements.
- Which systems, teams, and consumers are affected.

### 2. Design the expand/contract sequence

The **expand/contract pattern** is the foundational safe-migration primitive:

1. **Expand** — add the new interface, schema, or system while the old one
   continues to serve. Both old and new coexist. This phase is
   backward-compatible: existing consumers are unaffected.
2. **Compatibility window** — a defined period (duration or condition) during
   which both old and new are available. Consumers, replicas, and dependent
   systems are migrated to the new interface during this window. The window
   must have an explicit end condition — a date, a metric threshold (e.g.,
   "zero traffic on old endpoint for 7 days"), or an event (e.g., "all
   registered consumers confirmed migration").
3. **Dual-running or parallel operation** — for data and service migrations,
   both systems operate concurrently. Writes may be dual-written; reads may be
   dual-read with comparison. The dual-running period provides the evidence
   needed for the cutover decision.
4. **Contract** — remove the old interface, schema, or system after the
   compatibility window closes and verification confirms the new system is
   correct and complete. The contract phase may include data cleanup, code
   removal, and decommissioning.

Not every migration uses all four phases. A simple additive schema change may
use only expand (phase 1) — the old schema keeps working, the new column is
added, and no contract phase is needed. A complex service extraction uses all
four.

### 3. Plan the backfill and reconciliation

For data migrations, design the backfill strategy:

- **Full backfill** — copy all existing data from source to target in a
  single or batched operation before enabling dual-writes.
- **Incremental backfill** — copy data in pages or segments; useful for
  large datasets where a full backfill would exceed the available window.
- **Streaming backfill** — capture changes from the source via change-data-
  capture (CDC) or event log and apply them to the target continuously.

**Reconciliation** — how source and target are verified to match:

| Reconciliation dimension | Description |
|---|---|
| **Completeness** | Every record in the source exists in the target (row count, key-space coverage). |
| **Accuracy** | For a sample or full population, field-level values match within tolerance. |
| **Timeliness** | The target lag behind the source is within the defined threshold. |
| **Consistency** | Related records (e.g., orders and line items) are consistent in the target. |

Reconciliation runs continuously during the compatibility window and must pass
before cutover. A reconciliation failure is a **stop condition** — the cutover
must not proceed.

### 4. Design the cutover

The cutover is the point where the new system becomes the source of truth.
Design for:

- **Cutover procedure** — the exact sequence of operations, automated where
  possible, with pre-conditions and post-conditions.
- **Cutover window** — the expected duration, the acceptable downtime (if any),
  and the communication plan.
- **Interruption points** — where the cutover can be paused or reversed.
  A cutover that has no interruption points is a risk to flag explicitly.
- **Observability during cutover** — what metrics, logs, and alerts confirm
  the cutover is proceeding correctly, and what signals trigger abort.

### 5. Define recovery paths

Every migration step has a recovery classification. Use exactly these four
categories — never conflate them:

| Recovery path | Definition | When it applies |
|---|---|---|
| **Rollback** | Reverse to the prior state by undoing the change. | Additive schema changes, feature-flag-controlled code paths, dual-write data migrations where the old store is still current. |
| **Roll-forward** | Fix forward in the new state — the old state is no longer reachable, but a fix can be deployed to the new system. | Bugs discovered after cutover where the old system has been decommissioned; configuration errors in the new system that can be corrected without reverting. |
| **Restore** | Restore the prior state from a backup or snapshot. | The old system was taken offline and cannot be simply re-enabled; a backup exists and a restore procedure is tested. |
| **Irreversible** | Reversal is impossible — the change cannot be undone at any level. The migration plan must include acceptance criteria, explicit stakeholder communication, and a contingency plan (e.g., "if the migration fails, we will rebuild from the source of truth" or "we accept data loss within this bounded scope"). | Destructive operations with no backup, physical hardware decommissioning, cryptographic key rotation where old keys are destroyed, third-party data exports with no recall mechanism. |

**Irreversible steps require explicit acknowledgment before execution.** The
migration plan must distinguish "we have chosen not to build a reversal path"
from "reversal is physically impossible." Both require acceptance, communication,
and contingency — never silent assumption.

### 6. Plan deprecation and cleanup

After cutover is complete and verified:

- **Deprecation window** — how long the old system remains available in
  read-only or degraded mode before removal.
- **Consumer migration tracking** — which consumers still depend on the old
  interface, and when they are expected to migrate.
- **Cleanup** — removal of old schemas, code paths, feature flags,
  configuration, credentials, and infrastructure.
- **Communication** — notifications to consumers, stakeholders, and operators
  at each stage: compatibility window opens, cutover scheduled, cutover
  complete, deprecation window closing, old system removed.

### 7. Verify and close

Before declaring the migration complete:

- **Correctness evidence** — reconciliation reports, consumer verification,
  error-rate comparisons, SLO compliance data.
- **Observability confirmation** — migration-specific dashboards and alerts
  show the expected post-migration steady state.
- **Recovery verification** — rollback, roll-forward, or restore procedures
  were tested (where applicable); irreversible steps were acknowledged.
- **Owner sign-off** — the accountable owner for each phase confirms completion.

## Structured planning fields

Every migration plan must address these fields. They may appear as checklist
items, template fields, table columns, or labeled section headers — not only
as prose.

### Reconciliation

| Field | Question to answer |
|---|---|
| Strategy | Full, incremental, or streaming reconciliation? |
| Frequency | Continuous, hourly, daily, or pre-cutover only? |
| Coverage | All records or a statistical sample? |
| Tolerance | What divergence is acceptable? |
| Failure action | Stop, alert, or automatically re-reconcile? |

### Correctness evidence

| Field | Question to answer |
|---|---|
| Comparison method | Dual-read, shadow-traffic, consumer-side test, or synthetic validation? |
| Pass criteria | What measurements confirm correctness (e.g., "100% record match," "error rate < 0.01%," "p95 latency within 10% of baseline")? |
| Evidence artifact | Where is the evidence recorded (dashboard link, test report, reconciliation log)? |

### Observability

| Field | Question to answer |
|---|---|
| Progress metrics | Bytes migrated, records processed, consumers cut over? |
| Anomaly signals | Error-rate spikes, latency degradation, reconciliation drift? |
| Dashboards and alerts | Where are migration-specific metrics visible, and who is on-call? |

### Customer impact

| Field | Question to answer |
|---|---|
| Visible change | What does the customer experience during each phase? |
| Downtime | Is any downtime expected, and how is it communicated? |
| Performance | Could latency, throughput, or error rates change during the migration? |
| Support | How are customer issues triaged and escalated during the migration window? |

### Ownership

| Field | Question to answer |
|---|---|
| Migration lead | Who owns the overall migration plan and its execution? |
| Phase owners | Who is accountable for expand, dual-running, cutover, deprecation, and cleanup? |
| Communication owner | Who owns stakeholder and consumer notifications? |
| Escalation path | Who is the decision-maker if the migration must be paused, rolled back, or abandoned? |

## Loading guide

Load references and templates on demand — do not load everything at once.

| File | Load when |
|---|---|
| [references/discovery-brief.md](references/discovery-brief.md) | You need to understand how migration concepts map across sibling skills and where this skill's boundaries are |
| [references/compatibility-patterns.md](references/compatibility-patterns.md) | Designing forward/backward compatibility for a specific migration type |
| [references/recovery-classification.md](references/recovery-classification.md) | Classifying recovery paths (rollback, roll-forward, restore, irreversible) for a concrete migration step |
| [templates/migration-plan.md](templates/migration-plan.md) | Producing a complete migration plan with all structured fields |
| [templates/compatibility-matrix.md](templates/compatibility-matrix.md) | Building a compatibility matrix for a multi-consumer migration |
| [templates/reconciliation-plan.md](templates/reconciliation-plan.md) | Designing a reconciliation strategy for a data migration |
| [templates/cutover-and-recovery-record.md](templates/cutover-and-recovery-record.md) | Recording cutover procedures, recovery paths, and irreversible-step acknowledgments |

## Specialist routing

Migration engineering composes domain specialists — it never duplicates their
methodology. Route implementation details to the skill that owns the subsystem.

| Migration concern | Route to |
|---|---|
| API contract design, versioning policy, deprecation mechanics | [api-design-and-evolution](../api-design-and-evolution/SKILL.md) |
| Database schema evolution, ETL/ELT pipeline design, backfill operations | [data-engineering](../data-engineering/SKILL.md) |
| Infrastructure provisioning, service networking, secret management during migration | [platform-engineering](../platform-engineering/SKILL.md) |
| Release sequencing, progressive delivery, canary rollout, artifact promotion | [release-engineering](../release-engineering/SKILL.md) |
| SLO definition, error budgets, operational readiness, incident response during migration | [site-reliability-engineering](../site-reliability-engineering/SKILL.md) |
| Work breakdown, dependency mapping, critical path, ownership assignment | [implementation-planning](../implementation-planning/SKILL.md) |
| Threat modeling, security review of migration surface, auth boundary changes | [secure-software-engineering](../secure-software-engineering/SKILL.md) |
| Test strategy, regression coverage, verification gates during migration | [qa-methodology](../qa-methodology/SKILL.md) |
| Verification verdicts, evidence standards, boundary testing | [verification-methodology](../verification-methodology/SKILL.md) |

### Routing to same-wave and future skills

Migration evidence — reconciliation reports, cutover records, recovery-path
classifications, and deprecation tracking — feeds **production-readiness**
assessments. The production-readiness skill consumes migration plans as evidence
that a service is ready for production operation.

The **production-excellence** bundle composes migration-engineering alongside
production-readiness, resilience-and-recovery, capacity-and-cost-engineering,
incident-learning, and privacy-engineering. Migration-engineering contributes
the safe-change dimension to the production-excellence lifecycle.

### Routing to product-lifecycle skills

When a migration is triggered by a feature retirement or product sunset,
coordinate with **product-lifecycle-learning** for the retirement decision
record, deprecation timeline, and customer-treatment plan.
