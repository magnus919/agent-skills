---
name: resilience-and-recovery
description: >-
  Design, exercise, and evidence graceful degradation, disaster recovery, and
  restoration behavior across systems and dependencies. Covers failure-mode
  analysis, RTO/RPO decision records, restore testing, game days, failover
  drills, data integrity verification, and recovery communication. Do not use
  for live incident command or incident response; route to
  site-reliability-engineering for those. Do not use for infrastructure
  implementation details; route to platform-engineering.
license: MIT
compatibility: No runtime dependency. Host-neutral methodology.
---

# Resilience and Recovery

Design, exercise, and evidence resilience and recovery behavior across systems and their dependencies. This skill joins failure modes, dependency behavior, degradation choices, restore testing, disaster recovery, game days, failover, data integrity, and recovery communication into a single method — producing an exercise-backed resilience plan, not only a design document.

## When to use

| Trigger | What it covers |
|---|---|
| "Design a resilience plan for this system" | Failure-mode mapping, dependency analysis, degradation choices, RTO/RPO decision record, recovery plan template |
| "Run a game day or restore test" | Exercise design, scenario definition, evidence recording, follow-up work ledger |
|"Assess our disaster recovery readiness" | DR plan review against exercise evidence, gap analysis, data integrity verification |
| "What happens if this dependency fails?" | Dependency-loss scenarios, degradation paths, circuit-breaker and fallback strategy |
| "Define our RTO and RPO" | Context-specific decision record with tradeoff analysis, not universal prescription |
| "Verify data integrity after a restore" | Post-restore validation procedures, checksum and consistency checks, reconciliation protocol |
| "Plan a failover drill" | Failover exercise design, pre-conditions, success criteria, rollback/failback plan, evidence recording |

## When not to use

- **Live incident command or incident response**: route to [site-reliability-engineering](../site-reliability-engineering/SKILL.md) for the incident command system, on-call operations, and real-time incident management. This skill owns the pre-incident resilience design and exercise-evidence method; SRE owns the live response.
- **Infrastructure implementation details**: route to [platform-engineering](../platform-engineering/SKILL.md) for infrastructure-as-code, CI/CD pipeline implementation, container orchestration, and service networking. This skill owns the resilience requirements and exercise evidence; platform engineering owns the implementation.
- **Release rollout and rollback mechanics**: route to [release-engineering](../release-engineering/SKILL.md) for progressive delivery, canary deployments, feature flags, and rollback runbooks. This skill owns resilience verification of those mechanics through exercises.
- **Backup implementation and pipeline operations**: route to [data-engineering](../data-engineering/SKILL.md) for backup strategy implementation, WAL archiving, and snapshot management. This skill owns the restore-testing evidence and data-integrity verification protocol.
- **Security incident containment and forensics**: route to [secure-software-engineering](../secure-software-engineering/SKILL.md) for security incident response and threat containment. This skill owns the resilience dimension of security incidents — ensuring recovery capability survives a security event.
- **Post-incident learning and verification**: route to incident-learning for converting incident findings into verified follow-up work with closure evidence. This skill feeds exercise and DR test findings into the incident-learning pipeline.

## Loading guide

| File | Load when |
|---|---|
| [references/failure-modes-and-dependencies.md](references/failure-modes-and-dependencies.md) | Mapping failure modes, analyzing dependency loss, or designing degradation paths |
| [references/recovery-plan-template.md](references/recovery-plan-template.md) | Building or reviewing a resilience/recovery plan with structured fields |
| [references/exercise-design-and-evidence.md](references/exercise-design-and-evidence.md) | Designing a game day, restore test, failover drill, or recording exercise evidence |
| [references/rto-rpo-decision-record.md](references/rto-rpo-decision-record.md) | Defining RTO/RPO with context-specific tradeoffs and a decision-record template |
| [references/data-integrity-verification.md](references/data-integrity-verification.md) | Verifying data correctness and consistency after restore or failover |
| [references/recovery-communication.md](references/recovery-communication.md) | Planning who to notify and when during recovery events |
| [references/follow-up-work-ledger.md](references/follow-up-work-ledger.md) | Converting exercise findings into owned implementation, test, and operational work |
| [references/discovery-brief.md](references/discovery-brief.md) | Understanding ownership boundaries with adjacent skills |

## Core principles

**Resilience is proven by exercise, not design.** A recovery plan that has never been tested is a hope, not a capability. Every resilience claim must be backed by exercise evidence: a game day, a restore test, a failover drill, or a chaos experiment. Design documentation alone is not sufficient. Recovery plans require evidence from exercises — not just design claims. Exercise evidence, not only design documentation, is the standard of proof.

**High availability is not recoverability.** HA (redundancy, failover, clustering) keeps a system running through component failure. Recovery (backup, restore, disaster recovery) rebuilds a system after it has failed. HA is not a substitute for recovery: redundant systems can still experience data corruption, logical errors, or cascading failures that propagate across replicas. A system with 99.99% availability but no tested restore capability is not resilient — it is available but unrecoverable. Both HA and recovery are required; neither replaces the other.

**RTO and RPO are context-dependent, not universal.** Recovery time and recovery point objectives depend on the system's role, data classification, user impact, regulatory requirements, and cost. There is no universal "RTO should be < 1 hour." A payment system, an internal wiki, and a batch analytics pipeline have fundamentally different RTO/RPO profiles. Define RTO/RPO per system through a decision record with explicit tradeoffs, not by copying a template value. See the RTO/RPO decision record reference for the structured template.

**Dependencies define your blast radius.** Every upstream and downstream dependency is a failure mode. A resilience plan that does not account for dependency behavior under failure is incomplete. Map what happens when each dependency is unavailable, degraded, or slow — and what your system promises to its own consumers in each case.

**Degrade gracefully, not completely.** When a dependency or internal component fails, the system should continue operating in a reduced-but-acceptable mode rather than failing completely. Define acceptable degradation paths: which features are shed, which remain, and what user experience results. Not every failure justifies a full outage.

**Exercise failures are gifts.** When an exercise exposes a gap — a restore that took too long, a failover that lost data, a dependency loss that cascaded unexpectedly — that finding is an asset. Convert every exercise finding into owned follow-up work with a named owner, a target date, and a verification method. An exercise that reveals no gaps was not thorough enough or the system is untested.

**Recovery communication is part of recovery.** During a recovery event, stakeholders need to know: what happened, what is affected, what is being done, when to expect resolution, and who to contact. Pre-plan communication templates, notification channels, and escalation paths. Communication failures during recovery compound technical failures.

## Resilience patterns

### Pattern A: Graceful degradation

The system continues operating in a reduced-but-acceptable mode when a component or dependency fails. This is not a full outage — it is a deliberate choice to shed non-critical capability while preserving core function.

**Decision criteria for degradation:**
- Is the failing component essential to the system's core function? If yes, degradation may not be acceptable — the system may need to fail closed or fail safe.
- Can the remaining capability serve users acceptably for the expected recovery window? If users cannot accomplish their primary task, degradation is not working.
- What is the blast radius of continuing in degraded mode? Does degraded operation risk data corruption, security exposure, or cascading failure?

**Examples:**
- An e-commerce checkout loses the recommendation engine but still accepts orders. Recommendations are shed; ordering is preserved.
- A dashboard loses a real-time metrics feed but still displays cached data from the last refresh with a "data may be stale" indicator. Real-time is shed; observability is preserved.
- An API gateway loses a downstream microservice and returns a cached response or a graceful fallback payload instead of a 500 error. Freshness is shed; availability is preserved.

**Feature shedding by tier:**
- **Tier 1 (preserve):** Core function — the system's reason to exist. Must remain available.
- **Tier 2 (shed if necessary):** Enhancing features — improve experience but are not essential. Shed first.
- **Tier 3 (shed early):** Nice-to-have — non-critical embellishments. Shed immediately under stress.

### Pattern B: Restore-based recovery

The system is recovered from a backup, snapshot, or replica after a failure that cannot be mitigated through redundancy or degradation. This covers disaster recovery, data corruption recovery, and full-system rebuild.

**Decision criteria for restore:**
- Is the failure mode one that HA cannot handle (data corruption, logical error, region loss, ransomware)?
- What is the verified RTO — how long will the restore take, and has this been tested?
- What is the verified RPO — how much data will be lost, and has the backup been validated?
- Has the restore procedure been exercised end-to-end, including data integrity verification?

**Examples:**
- A primary database region is lost. The system fails over to a DR region and restores from the most recent validated cross-region backup. RTO and RPO are measured against the decision record.
- A logical data corruption (bad deployment, bug) propagates to all replicas. HA does not help — every replica is corrupted. The system restores from a point-in-time backup before the corruption event, and data integrity is verified post-restore.
- A ransomware event encrypts primary and replica data stores. The system restores from an air-gapped, immutable backup. Restore testing confirmed this capability within the RTO defined in the decision record.

**Restore testing requirements:**
- Full end-to-end restore must be exercised, not only backup verification.
- Data integrity must be verified after restore: checksums, row counts, application-level consistency checks.
- Restore must be measured against the RTO decision record. A restore that meets RTO on paper but not in practice is a gap.
- Restore procedures must be documented, versioned, and owned. The owner is accountable for exercise results.

## Resilience plan template fields

Every resilience plan must include these structured fields:

| Field | Description | Required evidence |
|---|---|---|
| **System boundary** | What is in scope and out of scope for this plan | Architecture diagram or boundary document |
| **Failure modes** | How the system can fail: component, dependency, region, data, operator error | Failure-mode analysis with likelihood and impact |
| **Dependency map** | Upstream systems this system depends on; downstream systems that depend on this system | Named systems, failure behavior per dependency, consumer contracts |
| **Degradation choices** | What is shed and what is preserved under each failure scenario | Tier assignments with rationale, user-impact assessment |
| **RTO/RPO decision record** | Context-specific recovery objectives per system and scenario | Decision-record template with tradeoffs, not hardcoded numbers |
| **Data integrity** | How data correctness and consistency are verified after recovery | Post-restore validation procedure, checksums, reconciliation protocol |
| **Recovery procedure** | Step-by-step recovery process with pre-conditions and success criteria | Versioned procedure, owner assignment, last-exercise date |
| **Communication plan** | Who to notify, when, and through what channels during each recovery scenario | Notification templates, stakeholder list, escalation contacts |
| **Exercise schedule** | When each recovery scenario was last exercised and when it will be re-exercised | Exercise evidence: date, scenario, result, findings |
| **Follow-up work ledger** | Exercise findings converted to owned implementation/test/operational work | Owner, target date, verification method, status per finding |

## Routing and related skills

This skill composes capabilities from and routes to:

- **[site-reliability-engineering](../site-reliability-engineering/SKILL.md)** — Incident command, on-call operations, SLO/SLI framework, error budgets. Resilience-and-recovery owns the pre-incident design and exercise evidence; SRE owns the live incident response.
- **[platform-engineering](../platform-engineering/SKILL.md)** — Infrastructure implementation, CI/CD, container orchestration, service networking. Resilience-and-recovery owns the resilience requirements; platform engineering owns the implementation that satisfies them.
- **[data-engineering](../data-engineering/SKILL.md)** — Backup strategy implementation, WAL archiving, snapshot management. Resilience-and-recovery owns the restore-testing evidence and data-integrity verification protocol.
- **[secure-software-engineering](../secure-software-engineering/SKILL.md)** — Security requirements, threat modeling, secure design. Resilience-and-recovery owns the resilience dimension of security incidents — ensuring recovery capability survives a security event.
- **[release-engineering](../release-engineering/SKILL.md)** — Progressive delivery, canary deployments, rollback runbooks. Resilience-and-recovery verifies those mechanics through exercises and feeds evidence into release readiness.
- **incident-learning** (wave 5) — Converts incident and exercise findings into verified follow-up work with closure evidence. Resilience-and-recovery feeds exercise and DR test findings into the incident-learning pipeline for cross-incident pattern analysis.

This skill feeds the **production-excellence** bundle (wave 6) as a component capability: resilience evidence — exercise results, RTO/RPO decision records, follow-up work ledgers — flows into the production-excellence evidence packet for go/no-go/defer/exception readiness decisions.
