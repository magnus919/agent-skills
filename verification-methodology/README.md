# Verification Methodology

Replace completion claims with a disciplined evidence trail that shows what was checked, what passed, and what remains uncertain.

## Why Install This Skill

Replace completion claims with a disciplined evidence trail that shows what was checked, what passed, and what remains uncertain. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `criteria-assessment.md`, `evidence-standards.md`, `verdict-template.md` |

## Quick Start

Define the criteria, collect direct evidence, and produce a verdict using `references/verdict-template.md`.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Verify work against explicit criteria using evidence, reproducible checks, and clear pass, conditional, or blocked verdicts. Use before declaring an artifact, implementation, or claim complete.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

No runtime dependency.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
