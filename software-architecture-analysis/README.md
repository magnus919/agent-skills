# Software Architecture Analysis — Reverse Engineering to Design Document

Reverse-engineer an existing codebase, assess its architecture health, and produce a clean-room design document, PRD, or migration plan grounded in repository evidence.

## Why Install This Skill

When your agent loads this skill, it becomes a **codebase archaeologist** who can:

- **Map repository structure** — identify core components, languages, and frameworks
- **Extract architecture** — understand how the system is actually built, not how it's documented
- **Inventory features** — catalog every capability the system provides
- **Identify implicit contracts** — storage operations, data flows, integration points
- **Assess architecture health** — quality characteristics, six coupling lenses, modularity, data authority, workflow failure, and reconciliation
- **Test decomposition readiness** — compare a bounded split with retaining a modular monolith instead of assuming services are better
- **Design clean-room alternatives** — re-imagine the system under new constraints (local-first, privacy-first, self-hosted)
- **Produce specifications** — PRDs, design documents, migration plans with zero source code copying

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | 7-phase build workflow, trigger conditions |
| `references/` | Interface extraction, quality-characteristic evidence, coupling/decomposition, and data/workflow analysis |
| `templates/` | Architecture health assessment worksheet |
| `evals/` | Output-quality cases for evidence, boundaries, decomposition, and distributed workflows |

## Triggers

Load this when you need to understand how an existing codebase works, produce a design document from implementation evidence, assess architecture health, map data ownership and distributed workflows, or evaluate readiness for a boundary change. Do not use it for greenfield architecture, direct code review, implementation, security auditing, API contract authoring, data-platform strategy, or migration execution.

## Requirements

Git and a programming language runtime matching the target codebase. Mermaid-capable Markdown is useful for architecture diagrams. No purchased books or private source material are required.


## Quick Start

Start with the workflow in `SKILL.md`, then load the relevant reference. For a health review, copy `templates/architecture-health-assessment.md`, fill the evidence ledger first, and keep recommendations in a separate section.
