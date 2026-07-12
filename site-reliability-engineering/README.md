# Site Reliability Engineering

Build practical reliability practices around the work teams actually perform: measurable service objectives, useful alerts, incident response, and learning-oriented follow-up.

## Why Install This Skill

Build practical reliability practices around the work teams actually perform: measurable service objectives, useful alerts, incident response, and learning-oriented follow-up. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `guiding-principles.md`, `incident-command-system.md`, `monitoring-alerting.md`, `oncall-best-practices.md`, `postmortem-culture.md`, `product-focused-reliability.md`, `release-engineering.md`, `senior-sre-blueprint.md`, `slo-sli-framework.md`, `sre-book-chapters.md`, `sre-communication-guide.md`, `sre-ecosystem-guide.md`, `toil-elimination.md`, `troubleshooting.md`, `twenty-years-lessons.md` |
| `templates/` | Templates: `error-budget-policy.md`, `incident-command-checklist.md`, `incident-communication.md`, `oncall-rotation.md`, `postmortem-template.md`, `runbook-template.md`, `service-review-checklist.md`, `slo-declaration-template.md` |
| `scripts/` | Scripts: `slo-burn-rate.py` |

## Quick Start

Start with the SLO/SLI, incident-command, or service-review template that matches the work at hand.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Design, operate, and improve reliable production systems with SLOs, incident command, observability, error budgets, and operational practices.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

Python 3.9+ is required only for the bundled calculation and summary scripts.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
