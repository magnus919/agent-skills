# Site Reliability Engineering

Build practical reliability practices around the work teams actually perform: measurable service objectives, useful alerts, incident response, and learning-oriented follow-up.

## Why Install This Skill

Build practical reliability practices around the work teams actually perform: measurable service objectives, useful alerts, incident response, and learning-oriented follow-up. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer, with an explicit closure gate that prevents a cleared alert from being mistaken for proven recovery.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, operational closure gate, and guidance for loading deeper resources. |
| `references/` | Reference material for SLOs, incidents, on-call, toil, troubleshooting, product engagement, adoption, reliability design, human systems, and the SRE learning ecosystem. |
| `templates/` | Templates for SLOs, error budgets, incident response, runbooks, service reviews, reliability design reviews, and overload recovery. |
| `scripts/` | Scripts: `slo-burn-rate.py` |

## Quick Start

Start with the SLO/SLI, incident-command, service-review, reliability-design-review, or operational-overload-recovery template that matches the work at hand.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Design, operate, and improve reliable production systems with SLOs, incident command, observability, error budgets, and operational practices.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.
- Work that adopts SRE practices without assuming a dedicated SRE department.
- Reliability design, capacity, overload, configuration, canary, dependency, durability, or operational-learning reviews.

## Requirements

Python 3.9+ is required only for the bundled calculation and summary scripts.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
