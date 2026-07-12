# Adr Authoring

Preserve the reasoning behind consequential architecture choices so later contributors can understand, revisit, or supersede them responsibly.

## Why Install This Skill

Preserve the reasoning behind consequential architecture choices so later contributors can understand, revisit, or supersede them responsibly. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `adr-format.md`, `adr-to-pyramid-mapping.md`, `decision-sustainability.md`, `fitness-functions.md`, `project-setup-guide.md` |

## Quick Start

Read `SKILL.md` for the decision workflow, then start from `references/adr-format.md`.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Write, review, and maintain architecture decision records with clear context, alternatives, consequences, and lifecycle governance. Use when a consequential technical decision must remain understandable.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

No runtime dependency.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
