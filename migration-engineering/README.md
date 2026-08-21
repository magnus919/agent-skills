# Migration Engineering — Safe cross-system migrations

## Why Install This Skill

Every production system changes. Schemas evolve, data moves between stores, APIs
get new versions, services shift between platforms. Each of these changes crosses
a system boundary, and each one risks data loss, downtime, or broken consumers if
done without a method.

Migration Engineering gives your agent a coherent method for planning and
executing safe migrations regardless of technology. It covers the full lifecycle —
compatibility design, dual-running, backfills, reconciliation, cutover, recovery,
deprecation, and cleanup — and it distinguishes between reversible and
irreversible steps so you never assume a false safety net.

After installing this skill, your agent can produce a complete migration plan
with compatibility windows, reconciliation strategies, cutover procedures,
recovery paths (rollback, roll-forward, restore, and irreversible), observability
signals, and ownership assignments — then route implementation details to the
right specialist skill.

## What You Get

| Directory entry | What it provides |
|---|---|
| `SKILL.md` | Core migration workflow: classify the migration type, design the expand/contract sequence, plan backfill and reconciliation, define cutover and recovery paths, plan deprecation and cleanup, verify and close. Includes structured planning fields (reconciliation, correctness evidence, observability, customer impact, ownership) and a specialist routing table. |
| `README.md` | This file — human-facing overview of what the skill does and how to use it. |
| `references/discovery-brief.md` | Bounded survey of existing migration-adjacent material across the catalog and a clear definition of what migration-engineering owns vs. hands off. |
| `references/compatibility-patterns.md` | Detailed patterns for forward and backward compatibility by migration type. |
| `references/recovery-classification.md` | Deep reference on the four recovery paths — rollback, roll-forward, restore, irreversible — with decision rules and examples. |
| `references/service-extraction-patterns.md` | Service-extraction seam evidence, coupling and data-ownership checks, transition-pattern selection, coexistence, reversibility, operational risk, and reasons to retain a modular monolith. |
| `templates/migration-plan.md` | Fillable template for a complete migration plan covering all structured fields. |
| `templates/compatibility-matrix.md` | Template for building a compatibility matrix across consumers and migration phases. |
| `templates/reconciliation-plan.md` | Template for designing a reconciliation strategy with completeness, accuracy, timeliness, and consistency dimensions. |
| `templates/cutover-and-recovery-record.md` | Template for recording cutover procedures, recovery paths per step, and irreversible-step acknowledgments. |
| `templates/service-extraction-assessment.md` | Fillable assessment for boundary evidence, coupling, ownership, coexistence, pattern choice, operational risk, reversibility, and modular-monolith retention. |
| `evals/evals.json` | Ten output-quality evaluation cases covering schema, data, API, irreversible cutover, reconciliation failure, service-extraction seams, pattern choice, data authority, recovery, and modular-monolith boundaries. |

## Quick Start

1. Identify the migration type: schema, data, API, infrastructure/service, or a combination.
2. Load the skill: your agent reads `SKILL.md` and follows the core workflow.
3. The agent produces a migration plan using the templates, starting with the
   migration plan template.
4. For an approved service extraction, load the service-extraction reference and
   assessment template before the general migration plan. The assessment keeps
   the modular monolith as an explicit outcome when the evidence does not support
   an independent service.
5. Route implementation details to the specialist skills named in the routing table
   (api-design-and-evolution, data-engineering, platform-engineering,
   release-engineering, site-reliability-engineering, implementation-planning).

## Triggers

Load this skill when:
- A schema change must not break existing readers or writers (zero-downtime DDL).
- A data migration between stores or representations needs dual-running and reconciliation.
- An API version migration needs a compatibility window and deprecation timeline.
- Infrastructure or services need to move between platforms or environments.
- A cross-system change requires cutover planning, rollback design, or irreversible-step acknowledgment.
- A monolith capability is moving toward an independently deployed service and needs seam evidence, coexistence, CDC, parallel-run, or strangler sequencing.
- A migration's recovery strategy needs to distinguish rollback, roll-forward, restore, and irreversible paths.

Do **not** load this skill when:
- The change is a single-system quick fix with no cross-boundary coordination.
- You need tool-specific instructions for a particular database, API gateway, or platform.
- The change is an in-place refactor or code rewrite with no data or interface migration.
- You are writing a release pipeline or deployment automation — route to release-engineering.
- You are debugging a production incident — route to site-reliability-engineering.
- You are deciding whether to decompose a system or designing its target architecture — route to the software-architecture decision owner.

## Requirements

- No runtime dependencies, API keys, or external services.
- The skill expects a migration scope that crosses at least one system boundary.
- Templates use markdown and work with any text editor or agent.
