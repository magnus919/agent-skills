# Technical Documentation

Make documentation useful at the moment someone needs to install, operate, extend, or troubleshoot a system.

## Why Install This Skill

Make documentation useful at the moment someone needs to install, operate, extend, or troubleshoot a system. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `agent-facing-docs.md`, `api-documentation-cli-help.md`, `readme-patterns.md` |

## Quick Start

Select the reference matching the documentation surface, then use its checklist before publishing the document.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Create and review technical documentation, including READMEs, agent-facing instructions, API references, and CLI help. Use when documentation must help someone complete real work.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

No runtime dependency.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
