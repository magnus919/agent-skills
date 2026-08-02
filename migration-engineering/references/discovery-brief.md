# Discovery Brief — Migration Engineering

## Purpose

This brief surveys existing migration-adjacent material in the agent-skills
catalog, identifies overlaps and gaps, and defines the ownership boundary for
the migration-engineering skill. It answers: **what does this skill own, and
what does it deliberately hand off to others?**

## Existing migration-adjacent material in the catalog

### api-design-and-evolution — API versioning and deprecation

`api-design-and-evolution` covers API compatibility assessment, versioning
policy, deprecation mechanics, and the consumer-impact analysis of interface
changes. Its deprecation-migration-plan template and
evolution-and-deprecation reference define how a single API evolves.

**What migration-engineering adds:** API evolution owns the **single-interface**
change. Migration-engineering owns the **cross-system** migration where the API
change is one component of a larger transition — for example, a service
extraction where the API changes, the data moves, and the infrastructure shifts
simultaneously. Migration-engineering also adds the recovery-path classification
(rollback/roll-forward/restore/irreversible) that API evolution does not address,
and the structured reconciliation and correctness-evidence fields.

**Boundary:** API design owns the contract. Migration engineering owns the plan
that coordinates the contract change with data, infrastructure, and service
changes. When a migration involves only an API version bump with no data movement
or infrastructure change, the api-design-and-evolution deprecation workflow is
sufficient — migration-engineering is not needed.

### data-engineering — schema migration and ETL

`data-engineering` covers database schema evolution (its database-migrations reference),
ETL/ELT pipeline design, data quality monitoring, and backup/recovery. Its
zero-downtime migration patterns, versioned schemas, and test-first migrations
are the authoritative source for database-level changes.

**What migration-engineering adds:** Data engineering owns the **single-store**
schema change. Migration-engineering owns the **cross-store** migration — moving
data between different stores, splitting a monolith database into services, or
migrating ownership of data from one team to another. Migration-engineering also
adds the migration-type classification (distinguishing schema, data, API, and
infrastructure migrations), the expand/contract sequence as a general pattern,
and the structured reconciliation fields that span beyond database-level
comparisons.

**Boundary:** Data engineering owns the DDL, the backfill script, and the
pipeline. Migration engineering owns the migration plan that sequences the DDL
with the API change, the consumer migration, and the cutover. For a
single-database schema change (e.g., add a nullable column), data-engineering's
database-migrations reference covers it directly.

### platform-engineering — infrastructure changes

`platform-engineering` covers infrastructure-as-code, container orchestration,
service networking, and cloud platform operations. Its references on CI/CD
pipelines and infrastructure-as-code define how platform changes are
provisioned and deployed.

**What migration-engineering adds:** Platform engineering owns the **how** of
infrastructure provisioning. Migration-engineering owns the **when and in what
order** — the staging, the compatibility window, the traffic-shifting
procedure, and the rollback decision points. Platform engineering provides the
Terraform module or Helm chart; migration engineering provides the plan that
says "apply this module to the staging environment first, verify SLOs for 48
hours, then promote to production with a 10% canary."

**Boundary:** Platform engineering owns the infrastructure definition and
provisioning tooling. Migration engineering owns the migration plan that
sequences the infrastructure change with other migration components. For a
pure infrastructure change with no data or API component (e.g., upgrading a
Kubernetes cluster version), platform-engineering and release-engineering
together are sufficient.

### release-engineering — rollout and change promotion

`release-engineering` covers progressive delivery (canaries, rings, percentage
rollouts), feature flags, release readiness gates, rollback planning, and
change governance. Its rollout mechanics are the execution engine for
promoting changes through environments.

**What migration-engineering adds:** Release engineering owns the **release
pipeline** — how artifacts move through stages. Migration engineering owns the
**migration staging** — what each stage means for data consistency, consumer
compatibility, and recovery. A release engineer can design a canary deployment;
a migration engineer can design the dual-write period, the reconciliation gate,
and the cutover trigger that the canary deployment gates on.

**Boundary:** Release engineering owns the promotion mechanics. Migration
engineering owns the migration-specific gates and evidence requirements that
feed into those mechanics. For a standard code deployment with no data or
schema migration, release-engineering alone is sufficient.

### site-reliability-engineering — change management

`site-reliability-engineering` covers SLO/SLI frameworks, error budgets,
incident command, and operational change management. Its change-management
practices define how operational risk is assessed and how changes are
monitored in production.

**What migration-engineering adds:** SRE owns the **operational safety** of
change — error budgets, SLO-based gating, and incident response. Migration
engineering owns the **migration-specific risk** — compatibility breaks,
reconciliation failures, and cutover timing. SRE provides the error budget
that gates the migration; migration engineering provides the migration plan
that stays within that budget.

**Boundary:** SRE owns the operational risk framework. Migration engineering
owns the migration risk specific to the cross-system transition. For a change
that is not a migration (no data movement, no interface change, no
infrastructure shift), SRE change management covers it.

### implementation-planning — migration planning

`implementation-planning` produces executable delivery plans for approved
specifications: work breakdown, dependency mapping, critical path, ownership,
sequencing, and rollout strategy. Its templates cover migration staging and
rollback design as part of a broader delivery plan.

**What migration-engineering adds:** Implementation planning owns the
**delivery plan structure** — who does what, in what order, with what
dependencies. Migration engineering owns the **migration-specific content**
that fills that structure — the compatibility matrix, the reconciliation
design, the recovery-path classification, the cutover procedure. An
implementation plan says "Week 3: backfill user profiles"; a migration plan
says *how* to backfill, *how* to reconcile, *what* to do if reconciliation
fails, and *whether* the backfill step is reversible.

**Boundary:** Implementation planning owns the work-breakdown and coordination
structure. Migration engineering owns the migration domain knowledge that
populates the structure. They are complementary, not competing. A migration
plan produced by this skill is a structured input to an implementation plan
produced by implementation-planning.

### product-lifecycle-learning — retirement and sunset

`product-lifecycle-learning` covers feature and product retirement: deprecation,
migration paths for customers, customer treatment during sunset, and retained
reusable learning. Its retirement-lifecycle reference and
sunset-plan template define the retirement decision and communication
lifecycle.

**What migration-engineering adds:** Product-lifecycle-learning owns the
**decision to retire** and the **customer-treatment plan**. Migration
engineering owns the **technical migration** that executes the retirement —
the data export, the API shutdown, the infrastructure decommissioning.
Product-lifecycle-learning says "this feature retires in Q3 and customers
must migrate to the replacement by Q4"; migration engineering says *how* to
migrate the data, *how* to run the old and new in parallel during the
transition, and *how* to verify the migration before shutting down the old
system.

**Boundary:** Product-lifecycle-learning owns the retirement decision and
customer communication. Migration engineering owns the technical execution
of the retirement migration. They are sequential: the retirement decision
triggers the migration plan.

## Ownership boundary

### What migration-engineering OWNS

1. **Migration-type classification** — distinguishing schema, data, API, and
   infrastructure/service migrations and their different compatibility,
   correctness, and recovery characteristics.
2. **Expand/contract sequencing** — the general pattern of adding the new
   alongside the old, maintaining a compatibility window, dual-running,
   and contracting by removing the old.
3. **Compatibility window design** — defining the duration, conditions, and
   consumer migration tracking for the period when old and new coexist.
4. **Backfill strategy** — selecting full, incremental, or streaming backfill
   and sequencing it with dual-writes.
5. **Reconciliation design** — defining how source and target are verified
   to match across completeness, accuracy, timeliness, and consistency.
6. **Cutover procedure** — the exact sequence, pre-conditions, observability
   signals, and interruption points for switching to the new system.
7. **Recovery-path classification** — distinguishing rollback, roll-forward,
   restore, and irreversible steps, and requiring explicit acknowledgment for
   irreversible steps.
8. **Deprecation and cleanup** — the timeline and procedure for removing the
   old system after migration is verified.
9. **Structured planning fields** — reconciliation, correctness evidence,
   observability, customer impact, and ownership as checklist/template items.
10. **Cross-specialist coordination** — routing implementation details to the
    domain specialist that owns each subsystem.

### What migration-engineering HANDS OFF

1. **API contract design and versioning policy** → [api-design-and-evolution](../api-design-and-evolution/SKILL.md).
   Migration engineering cites the API compatibility policy; it does not define it.
2. **Database DDL, ETL pipeline implementation, backfill script authoring** →
   [data-engineering](../data-engineering/SKILL.md). Migration engineering
   defines the backfill strategy; data engineering implements it.
3. **Infrastructure provisioning, Terraform modules, Helm charts** →
   [platform-engineering](../platform-engineering/SKILL.md). Migration
   engineering defines the staging sequence; platform engineering provisions it.
4. **Release pipeline mechanics, canary configuration, feature flag implementation** →
   [release-engineering](../release-engineering/SKILL.md). Migration engineering
   defines the migration gates; release engineering implements the promotion pipeline.
5. **SLO definition, error budget policy, incident response procedure** →
   [site-reliability-engineering](../site-reliability-engineering/SKILL.md).
   Migration engineering consumes the error budget as a gate; SRE defines it.
6. **Work breakdown, dependency mapping, critical path, ownership assignment** →
   [implementation-planning](../implementation-planning/SKILL.md). Migration
   engineering provides the migration-specific content; implementation planning
   structures it into a delivery plan.
7. **Threat modeling, security review of migration surface** →
   [secure-software-engineering](../secure-software-engineering/SKILL.md).
8. **Retirement decision and customer communication** →
   [product-lifecycle-learning](../product-lifecycle-learning/SKILL.md). Migration
   engineering executes the technical side of a retirement-triggered migration.
9. **Test strategy and verification gate design** →
   [qa-methodology](../qa-methodology/SKILL.md) and
   [verification-methodology](../verification-methodology/SKILL.md).
