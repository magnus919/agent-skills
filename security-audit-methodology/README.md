# Security Audit Methodology

Give authorized teams a disciplined way to identify and prioritize security risks without mistaking a checklist for a security guarantee.

## Why Install This Skill

Give authorized teams a disciplined way to identify and prioritize security risks without mistaking a checklist for a security guarantee. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `security-architecture-dependency-audit.md`, `threat-modeling.md`, `vulnerability-classification.md` |

## Quick Start

Confirm authorization and scope first, then begin with `references/threat-modeling.md`.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Plan authorized security reviews with threat modeling, architecture and dependency audits, and vulnerability classification. Use for scoped defensive security assessment.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

Authorization for the target system is required. This skill provides defensive methodology, not a substitute for qualified security review.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
