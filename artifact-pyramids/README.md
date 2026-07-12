# Artifact Pyramids

Structure durable research work so people and agents can start with conclusions, then inspect the analysis and underlying evidence only when needed.

## Why Install This Skill

Structure durable research work so people and agents can start with conclusions, then inspect the analysis and underlying evidence only when needed. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `artifact-pyramid-framework.md`, `canonical-article.md`, `companion-session-summary.md`, `composite-pyramid-synthesis.md`, `delegation-context-template.md`, `flat-to-pyramid-migration.md`, `intellectual-lineage.md`, `methodology-to-pyramid-mapping.md`, `nested-pyramid-pattern.md`, `output-classification-framework.md`, `pipeline-stages.md`, `provenance-artifacts.md`, `quality-gates.md`, `skillopt-baseline-pyramid.md`, `skillopt-pipeline-integration.md`, `synthetic-example.md` |
| `assets/` | Assets: `artifact-inventory.md`, `pyramid-template.md` |
| `scripts/` | Scripts: `extract-atoms.py`, `pyramid-status.sh`, `pyramid-status.sh.bak` |

## Quick Start

Copy `assets/pyramid-template.md` into a new research directory, then follow the layer and navigation rules in `SKILL.md`.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Organize durable agent research outputs as summaries, analysis, and evidence dossiers. Use when producing multi-layer research artifacts or coordinating research handoffs.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

Python 3.9+ and a POSIX shell are required only for the bundled scripts.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
