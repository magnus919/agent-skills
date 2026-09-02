---
name: production-excellence
description: >-
  Build cross-domain production evidence from readiness, migration, recovery,
  capacity/cost, and incident learning into launch or operational decisions. Do not use
  this skill for a single specialist's risk packet and launch gate; use
  `production-readiness` for that readiness review.
license: MIT
compatibility: Platform-agnostic methodology. No runtime dependencies, API keys, or external services required.
metadata:
  tags: production-excellence, launch-decision, gate-model, evidence-packet,
    operational-handoff, readiness-review, cross-domain, production-acceptance,
    go-no-go, exception-escalation, post-launch-learning
---

# Production Excellence

A thin composition bundle that assembles cross-domain production evidence into a
defensible launch or operational decision. It owns the **acceptance and handoff
layer** — the gate model that reads evidence from specialist skills and produces
go / no-go / defer / exception / escalation outcomes with accountable owners.
It does not own any specialist's runbook.

## When to load this

Load when:

- A service or change is approaching a launch decision and evidence from multiple
  production domains must be assembled.
- You need a structured gate model (go/no-go/defer/exception/escalation) with
  conditions, evidence, and accountable owners.
- Cross-domain evidence (readiness, migration, recovery, capacity/cost, incident
  history) must be combined into one operational handoff record.
- A launch or change needs a post-launch learning path routed to incident-learning
  and product-lifecycle-learning.
- You are coordinating a production change across SRE, release, platform, security,
  data, and QA specialists and need a single acceptance contract.

## When not to use

Do **not** load this bundle for:

- **Incident command or SLO operations** — those are owned by
  [site-reliability-engineering](../site-reliability-engineering/SKILL.md).
- **Release-pipeline mechanics, versioning, or deployment strategies** — those are
  owned by [release-engineering](../release-engineering/SKILL.md).
- **Platform architecture or internal-developer-platform design** — those are
  owned by [platform-engineering](../platform-engineering/SKILL.md).
- **Threat modeling, security review procedure, or vulnerability assessment** —
  those are owned by
  [secure-software-engineering](../secure-software-engineering/SKILL.md).
- **Data-pipeline design, ETL, or storage architecture** — those are owned by
  [data-engineering](../data-engineering/SKILL.md).
- **Test-strategy design, regression-suite management, or test-automation
  framework design** — those are owned by
  [qa-methodology](../qa-methodology/SKILL.md).
- **A generic checklist detached from service ownership, risk, evidence, and
  verification** — every gate in this bundle requires a named service owner,
  assessed risk, verified evidence, and a declaration of the verification
  boundary. A bare checklist is never a valid outcome.

This bundle composes specialists. It never replaces them and never re-derives
their methods. If the task is wholly within one specialist's domain, load that
specialist directly.

## Readiness routing table

The bundle routes each production concern to the specialist that owns it. The
bundle itself owns only the acceptance and handoff layer — the cross-domain
assembly and the gate decision.

### Primary production-domain routes

| Domain | Specialist skill | What the specialist owns | What the bundle adds |
|---|---|---|---|
| **Production readiness** | [production-readiness](../production-readiness/SKILL.md) | Risk-scaled evidence packet (11 categories), go/no-go/defer/exception launch decisions, accountable owners | Cross-domain assembly with migration, recovery, capacity/cost, and incident evidence; gate integration |
| **Migration** | [migration-engineering](../migration-engineering/SKILL.md) | Expand/contract, compatibility windows, dual-running, backfills, reconciliation, cutover, recovery paths | Migration evidence as input to the gate model; handoff of migration verification to the operational record |
| **Resilience and recovery** | [resilience-and-recovery](../resilience-and-recovery/SKILL.md) | Failure modes, degradation choices, RTO/RPO, restore testing, DR, game days, failover, data integrity | Recovery evidence as a gate condition; exercise results feed the handoff record |
| **Capacity and cost** | [capacity-and-cost-engineering](../capacity-and-cost-engineering/SKILL.md) | Demand/capacity/scaling/utilization models, unit-cost connection to SLO decisions, cost-constrained scenarios | Capacity/cost evidence as a gate condition; SLO/cost tradeoff decisions feed the gate model |
| **Incident learning** | [incident-learning](../incident-learning/SKILL.md) | Observed facts, causal hypotheses, contributing conditions, follow-up work mapping, verified closure | Pre-existing incident evidence as a gate condition; post-launch incidents routed back to incident-learning |

### Supporting specialist routes

| Domain | Specialist skill | When routed |
|---|---|---|
| **Reliability / SLOs** | [site-reliability-engineering](../site-reliability-engineering/SKILL.md) | SLO/error-budget status required for gate entry; incident response for post-launch issues |
| **Release mechanics** | [release-engineering](../release-engineering/SKILL.md) | Release plan, rollout/rollback strategy required for gate entry |
| **Platform** | [platform-engineering](../platform-engineering/SKILL.md) | Service-catalog entry, paved-road status for new services |
| **Security** | [secure-software-engineering](../secure-software-engineering/SKILL.md) | Security review evidence for trust-boundary changes |
| **Data** | [data-engineering](../data-engineering/SKILL.md) | Data-quality and pipeline evidence for data-path changes |
| **QA** | [qa-methodology](../qa-methodology/SKILL.md) | Verification evidence for all launches |
| **Verification** | [verification-methodology](../verification-methodology/SKILL.md) | Boundary labeling and gap declaration for evidence assessment |

## Cross-domain entry evidence

Before the gate model runs, entry evidence must exist from every applicable
domain. The bundle does not gather this evidence — it requires it. The complete
evidence packet specification is in
[references/evidence-packet.md](references/evidence-packet.md).

Summary:

- Every evidence domain (readiness, migration, recovery, capacity/cost,
  incident-learning) has a named source or an explicit gap with an owner and
  due date.
- The packet is usable for **both new services and changes to existing systems**
  — domains irrelevant to the change are explicitly marked "not applicable"
  with a reason.
- Missing evidence is never silently omitted. Every gap is recorded.

## Gate and exception model

The gate model produces exactly one of five outcomes for every production change.
Full definitions, conditions, and evidence requirements are in
[references/gates.md](references/gates.md).

| Outcome | Meaning | Key condition |
|---|---|---|
| **Go** | Authorized to proceed to production | All required evidence domains are sourced; no blocking gaps |
| **No-go** | Blocked; must not proceed | A required domain has a blocking gap, or an irreversible step has no verified recovery path |
| **Defer** | Postponed with explicit conditions | A non-blocking gap or dependency has a committed resolution date; re-evaluation is scheduled |
| **Exception** | Proceeds under an explicit waiver | A human authority (not the agent, not the service owner alone) approves a time-bounded, risk-bounded exception |
| **Escalation** | Decision escalated to a higher body | Irreconcilable gate conflict, trust-boundary security gap, cross-team authority gap, or regulatory boundary |

Every outcome is anchored to **service ownership**, **risk**, **evidence**, and
**verification**. No gate passes on a bare checklist. Each outcome names the
accountable owner and records the evidence that supports it.

## Operational handoff and post-launch learning

After a gate outcome is reached, the operational handoff record
([references/handoff-record.md](references/handoff-record.md)) is populated.

### Post-launch learning paths

Launch outcomes and post-launch observations feed two learning routes:

1. **Incident learning** — post-launch incidents (SLO degradations, unexpected
   failures, capacity breaches) are routed to
   [incident-learning](../incident-learning/SKILL.md). The handoff record
   provides the launch context; the incident-learning skill's verified-closure
   requirement ensures follow-up items are tracked to completion.

2. **Lifecycle learning** — expected outcomes recorded in the handoff (SLO
   targets, capacity assumptions, cost projections) are routed to
   [product-lifecycle-learning](../product-lifecycle-learning/SKILL.md)
   for expected-vs-observed comparison at the handoff's review cadence. The
   lifecycle-learning skill's continue/improve/harvest/pivot/pause/retire
   decisions are informed by the gap between predicted and observed production
   behavior.

The handoff record is populated for every outcome — not only Go. No-go, Defer,
Exception, and Escalation each produce a handoff record with the blocking
condition, the follow-up path, and the accountable owner.

## Loading and nested-skill behavior

This bundle is the discoverable entry point. It does not contain nested
sub-skills under a `skills/` directory. All routed skills are top-level catalog
skills referenced via relative markdown links. Harnesses that support progressive
disclosure will discover this bundle through its `SKILL.md` frontmatter and load
the referenced specialists on trigger.

See [AGENTS.md](AGENTS.md) for agent-specific loading notes.

## File map

| Path | Loaded when |
|---|---|
| [references/discovery-brief.md](references/discovery-brief.md) | Understanding the bundle's boundary against existing production and release skills |
| [references/evidence-packet.md](references/evidence-packet.md) | Assembling cross-domain evidence for a production decision |
| [references/gates.md](references/gates.md) | Running the gate model — go/no-go/defer/exception/escalation |
| [references/handoff-record.md](references/handoff-record.md) | Producing the operational handoff record and post-launch learning path |
| [manifest.yaml](manifest.yaml) | Machine-readable composition contract (schema v1): purpose, audience, stages, included skills, prerequisites, outputs, handoffs, conflicts, and eval suite; consumed by the lifecycle capability matrix |
