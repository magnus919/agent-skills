---
name: implementation-planning
description: >-
  Plan the implementation of an approved requirement or specification: produce an
  executable, dependency-aware delivery plan covering work breakdown, dependency
  mapping, critical path, ownership, parallelism and sequencing, rollout strategy,
  rollback and recovery paths, and verification against the original requirement.
  Supports cross-team, cross-repository, migration, and staged-rollout scenarios.
  Do not use for pre-approval discovery or needs-finding, authoring a specification
  from scratch, coding or implementation, the neckbeard issue-to-PR delivery flow
  itself, or any work whose prerequisite decision has not been approved — planning
  unapproved work is an explicit stop condition.
license: MIT
compatibility: >-
  Platform-agnostic methodology. Templates use markdown. No runtime dependency.
metadata:
  source_repo: https://github.com/magnus919/agent-skills
  skill_version: "1.0.0"
  tags: implementation-planning, delivery-planning, work-breakdown, dependency-mapping,
    rollout-planning, migration-planning, cross-team-planning, execution-planning
---

# Implementation Planning

Turn an **approved** requirement or specification into an executable delivery plan.
This skill is a planning discipline — it produces a plan, not code, not a spec, and
not a lifecycle orchestration.

## When to load this skill

Load when the input is an **approved requirement, specification, or decision** and
the task is to produce a concrete delivery plan that accounts for dependencies,
sequencing, risk, and verification.

| Trigger | Example |
|---|---|
| An approved SPEC.md or product brief needs a delivery plan | "Plan the implementation for the payments checkout spec" |
| A cross-team or multi-repo feature needs work coordination | "Plan the rollout for the identity-migration change across three services" |
| A data migration needs a staged execution plan | "Plan the schema migration with rollback stages" |
| A risky or high-stakes change needs a rollout strategy | "Plan the staged rollout for the auth-provider replacement" |
| Multiple workstreams need dependency mapping and critical-path analysis | "Map dependencies and critical path for the platform upgrade" |

### When not to use

- **Pre-approval discovery or needs-finding** — the input is not yet an approved
  requirement. Route to [product-discovery](../product-discovery/SKILL.md).
- **Authoring a specification from scratch** — no approved spec exists yet.
  Route to [spec-driven-development](../spec-driven-development/SKILL.md).
- **Coding, implementation, or architecture design** — the plan is done, now
  execute. Route to [backend-engineering](../backend-engineering/SKILL.md),
  [frontend-engineering](../frontend-engineering/SKILL.md), or
  [software-architecture-analysis](../software-architecture-analysis/SKILL.md).
- **The neckbeard issue-to-PR delivery flow** — this skill plans work, it does
  not execute the neckbeard lifecycle gates, delivery-packet sequencing, or
  phase orchestration. Delivery execution is a separate concern.
- **The prerequisite decision is not approved** — if the requirement or
  specification has not been approved, **stop**. Planning unapproved work is an
  explicit stop condition. Record the missing approval and escalate; do not
  produce a plan.
- **The whole run needs a control-plane protocol** — intent contracts, work
  classification, autonomy gating, review-as-triage, and failure routing around the
  plan and its execution. Route to [bmad](../bmad/SKILL.md). This skill produces a
  delivery plan; bmad owns the protocol that runs intent-to-delivery work end to end.

For ongoing milestone reviews, forecast changes, sponsor decisions, and project
closure after planning, route to
[technical-project-management](../technical-project-management/SKILL.md).
Keep detailed work breakdown and dependency-plan maintenance here.

## Entry gate: prerequisite approval

Before any planning work begins, verify that the input requirement or
specification has been **approved** by an authorized decision-maker. An approved
input is one that has passed a review gate (SDD spec review, product brief
approval, architecture decision record accepted, or equivalent).

If the input is **not approved**:

1. **Stop.** Do not produce a draft plan, partial work breakdown, or
   "assume-approved" artifact.
2. State the missing approval explicitly: what decision is pending and who
   (role or name) must approve it.
3. Route to the appropriate upstream skill:
   - No spec exists → [spec-driven-development](../spec-driven-development/SKILL.md)
   - Requirements are unvalidated → [product-discovery](../product-discovery/SKILL.md)
   - Architecture decision is pending → [adr-authoring](../adr-authoring/SKILL.md)

This gate exists because a plan built on an unapproved foundation wastes
every downstream team's time and creates false certainty.

## Core workflow

1. **Ingest the approved input.** Read the approved requirement, specification,
   or decision record. Capture the source, approval date, approver, and any
   explicit constraints or non-goals.

2. **Decompose into work.** Break the approved scope into vertical slices or
   workstreams that deliver independent value. Prefer vertical slices (end-to-end
   capability) over horizontal layers (database then API then UI). Each slice
   must have a clear completion criterion.

3. **Map dependencies.** Identify every dependency: upstream inputs, downstream
   consumers, shared services, data stores, platform capabilities, team
   availability, and external vendors or partner teams. Distinguish hard
   dependencies (blockers) from soft dependencies (preferences). Record them in
   the dependency record.

4. **Identify the critical path.** Trace the longest chain of dependent work
   that determines the earliest possible completion. Flag any dependency that,
   if delayed, shifts the critical path.

5. **Assign ownership.** Every workstream and every dependency needs an owner.
   Ownership means accountability for completion, not necessarily doing the
   work personally. Record owners by name or role.

6. **Sequence and parallelize.** Order work to respect dependencies and maximize
   parallelism. Identify which slices can run concurrently, which must be
   sequential, and where parallel tracks must synchronize.

7. **Design the rollout strategy.** Define how the change reaches production:
   big-bang, staged (by customer, region, percentage), canary, feature-flagged,
   or a combination. Define the rollout stages, gates, and duration of each stage.

8. **Design rollback and recovery.** For every rollout stage, define the
   rollback path: what triggers a rollback, how to execute it, how long it takes,
   and what state is left behind. Include data rollback where applicable.

9. **Verify against the original requirement.** Trace every workstream back to
   the approved input. Confirm nothing is missed and nothing extra is included.
   Record any deliberate scope decisions.

10. **Identify unresolved decisions and risks.** List every decision that could
    not be resolved during planning and every residual risk. Assign each an owner
    and a resolution deadline.

## Outputs

An implementation plan includes these sections. Templates are in [templates/](templates/).

| Output | Template | Purpose |
|--------|----------|---------|
| Work breakdown | [templates/implementation-plan-template.md](templates/implementation-plan-template.md) | Vertical slices, workstreams, completion criteria, ownership |
| Dependency and handoff record | [templates/dependency-record.md](templates/dependency-record.md) | Dependency map, critical path, handoff contracts between teams |
| Risk, decision, verification record | [templates/risk-decision-verification.md](templates/risk-decision-verification.md) | Risks, unresolved decisions, assumptions, verification checklist |

## Cross-team and cross-repository planning

This skill does **not** assume a single repository or team. When the approved
requirement spans multiple repositories, teams, or organizations:

- Treat each repository or team boundary as a **dependency interface** — define
  the contract (API, schema, event, or handoff artifact) and its owner.
- Plan **integration checkpoints** where cross-team work is verified together,
  not only at the end.
- Explicitly name the **coordination mechanism**: shared calendar, sync meeting,
  Slack channel, or status dashboard.
- For migrations, include the **cutover strategy** (parallel run, big-bang
  switch, phased migration) and the **backfill/reconciliation plan**.

## Staged rollout and migration planning

When the change carries material risk, the plan must include a staged rollout
strategy. See [references/discovery-brief.md](references/discovery-brief.md) for
how this skill's rollout planning relates to [release-engineering](../release-engineering/SKILL.md)'s
pipeline design and [site-reliability-engineering](../site-reliability-engineering/SKILL.md)'s
SLO-based gradual rollout.

At minimum, a staged rollout plan defines:

- **Stages**: how many stages, what each stage gates on, and how long each runs.
- **Observability**: what metrics, logs, or signals confirm each stage is healthy.
- **Rollback trigger**: what specific condition triggers a rollback at each stage.
- **Recovery path**: how to roll back data, configuration, and traffic.

For data migrations, additionally include:

- **Dual-write or backfill strategy** for the transition period.
- **Schema compatibility** (forward and backward) during migration.
- **Cutover and reconciliation** before removing old paths.

## Handoff to specialist skills

This skill produces a **plan**. Specialist skills execute the plan. The handoff
from planning to execution is a deliberate boundary — do not let planning bleed
into implementation.

| When the plan covers... | Hand off to |
|---|---|
| Specification authoring or formal phase gates | [spec-driven-development](../spec-driven-development/SKILL.md) |
| Discovery of unvalidated requirements | [product-discovery](../product-discovery/SKILL.md) |
| QA strategy, test planning, or verification design | [qa-methodology](../qa-methodology/SKILL.md) |
| Intent contracts, autonomy gating, or failure routing around the plan | [bmad](../bmad/SKILL.md) |
| Release pipeline, promotion gates, or canary mechanics | [release-engineering](../release-engineering/SKILL.md) |
| Internal developer platform or CI/CD infrastructure | [platform-engineering](../platform-engineering/SKILL.md) |
| Security requirements, threat modeling, or secure design | [secure-software-engineering](../secure-software-engineering/SKILL.md) |
| Reliability targets, SLOs, incident response, or operational readiness | [site-reliability-engineering](../site-reliability-engineering/SKILL.md) |
| Architecture decisions that need formal ADRs | [adr-authoring](../adr-authoring/SKILL.md) |
| API contract design or evolution | [api-design-and-evolution](../api-design-and-evolution/SKILL.md) |
| Data pipeline, schema, or storage design | [data-engineering](../data-engineering/SKILL.md) |

When a specialist skill listed above already owns a section of the plan (e.g.,
rollout mechanics are owned by release-engineering), this skill cites the
specialist's output rather than re-deriving it. The plan names the specialist
artifact and its owner; it does not duplicate the specialist's method.

## File map

| Path | Load when |
|---|---|
| [references/discovery-brief.md](references/discovery-brief.md) | Understanding what this skill owns vs. hands off to adjacent skills |
| [templates/implementation-plan-template.md](templates/implementation-plan-template.md) | Producing a full implementation plan |
| [templates/dependency-record.md](templates/dependency-record.md) | Mapping dependencies, critical path, and handoff contracts |
| [templates/risk-decision-verification.md](templates/risk-decision-verification.md) | Recording risks, unresolved decisions, and verification traceability |
