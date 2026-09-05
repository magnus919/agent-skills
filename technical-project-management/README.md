# Technical Project Management

Keep technical projects moving with credible commitments, clear decisions, and useful evidence.

## Why Install This Skill

A team can have good engineers and a busy board while still missing dependencies,
hiding schedule risk, or leaving decisions unresolved. This skill helps your agent
coordinate the work from project kickoff through acceptance and operational handoff.
It selects an approach that fits your constraints instead of imposing one framework.

Teams without a project manager get a lightweight way to organize ownership and
next steps. Experienced TPMs get concise analysis, recovery options, and decision
briefs without introductory lessons. Research references and real cases explain
where practices help and where their assumptions break down.

## What You Get

| Contents | What they provide |
|---|---|
| `SKILL.md` | Focused entry point and connections to specialist skills |
| `references/` | Method selection, predictive/adaptive/hybrid delivery, control, forecasting, recovery, closure, source ledger, and four real cases |
| `templates/` | Seven adaptable project records and a worked schedule input |
| `scripts/` | Read-only dependency schedule analysis with resource-conflict warnings and tests |
| `evals/` | Realistic quality scenarios covering team and expert use |

## Quick Start

Ask: "We have three teams, a fixed launch date, and a vendor slipping. Help me
assess the impact and prepare a decision for our sponsor."

For a schedule calculation, from this directory:

```sh
python3 scripts/schedule.py --input templates/schedule-example.json --json
```

The example returns a finish at working day 6, one day beyond its deadline, and a
shared-resource conflict. It does not claim those earliest dates are achievable.

## Triggers

- Starting or inheriting a technical project, including teams without a PM.
- Choosing a delivery approach or coordinating teams and suppliers.
- Reviewing milestones, forecasts, scope changes, or troubled-project recovery.
- Preparing a sponsor decision or closing and handing off a project.

## Requirements

No service, API key, or runtime is needed for the guidance and templates. The
optional calculator and its tests require Python 3.10+ with the standard library.
Jira or Linear operations use the separate tool skills and their own credentials.
