# Implementation Planning — Turn approved specs into executable delivery plans

## Why Install This Skill

A great specification answers "what to build." It does not answer "how to build
it across three teams, two repositories, a data migration, and a staged rollout."
That gap — between an approved requirement and the first line of code — is where
teams lose weeks to misalignment, missed dependencies, and last-minute surprises.

Implementation Planning fills that gap. Give your agent an approved spec or
product brief, and it returns a concrete, dependency-aware delivery plan with
work breakdown, critical path analysis, ownership, rollout strategy, rollback
paths, and verification traceability back to the original requirement.

This skill is designed for real-world complexity: cross-team coordination,
multi-repository changes, data migrations with rollback, and staged rollouts
with observability gates. It does not assume a single repo or a single team.

## What You Get

| Directory entry | What it provides |
|---|---|
| `SKILL.md` | Core planning workflow: ingest approved input, decompose into workstreams, map dependencies, find the critical path, assign ownership, sequence and parallelize, design rollout and rollback, verify against the original requirement. Includes entry gate (stop if not approved), handoff table to specialist skills, and cross-team/cross-repo guidance. |
| `README.md` | This file — human-facing overview of what the skill does and how to use it. |
| `references/discovery-brief.md` | Bounded comparison of existing planning material across the catalog (SDD task plans, release-engineering rollout plans, SRE change plans, product-discovery) and a clear definition of what implementation-planning owns vs. hands off. |
| `templates/implementation-plan-template.md` | Fillable template for a complete implementation plan: workstreams, ownership, sequencing, rollout stages, rollback triggers, and verification checklist. |
| `templates/dependency-record.md` | Structured record for dependency mapping, critical path, and handoff contracts between teams or repositories. |
| `templates/risk-decision-verification.md` | Sections for recording risks, assumptions, unresolved decisions, and verification traceability from plan back to requirement. |
| `evals/evals.json` | Five output-quality evaluation cases covering ambiguous requirements, cross-repository dependencies, a data migration, a risky rollout, and a plan rejection due to missing prerequisite approval. |

## Quick Start

1. Ensure you have an **approved** requirement or specification ready. The skill
   will stop and decline if the input is not approved.
2. Load the skill: your agent reads `SKILL.md` and follows the core workflow.
3. The agent produces a plan using the templates in `templates/`, starting with
   the implementation plan template.
4. Review the plan, resolve any open decisions, and hand it off to the
   specialist skills named in the handoff table.

## Triggers

Load this skill when:
- An approved spec or product brief needs a delivery plan.
- A cross-team or multi-repo feature needs work coordination and dependency mapping.
- A data migration needs a staged execution plan with rollback.
- A risky or high-stakes change needs a rollout strategy with observability gates.
- Multiple workstreams need critical-path analysis and ownership assignment.

Do **not** load this skill when:
- The requirement has not been approved — route to product-discovery or spec-driven-development first.
- You need to write a spec from scratch — route to spec-driven-development.
- You are coding, debugging, or implementing — route to the appropriate engineering skill.
- You are executing the neckbeard issue-to-PR delivery flow — this skill plans work, it does not execute delivery.

## Requirements

- No runtime dependencies, API keys, or external services.
- The skill expects an approved requirement or specification as input. An
  unapproved input triggers the stop condition — no plan is produced.
- Templates use markdown and work with any text editor or agent.
