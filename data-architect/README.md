# Data Architect — Virtual Expert for Teams Who Don't Have One

A virtual data architect that helps you spot data platform problems you didn't know you had. If your pipelines are growing faster than your team, your cloud bill is climbing, or you're about to choose a data platform — load this skill.

## Why Install This Skill

When your agent loads this skill, it becomes a **senior data architect** who can:

- **Run a QuickScan** — 5-minute diagnostics that surface common data platform gaps
- **Discover data assets** — inventory every system producing data your team consumes
- **Assess data maturity** — evaluate where you are on the data maturity curve
- **Design data architectures** — data mesh readiness, event-driven data products, data lakehouse, streaming, and real-time analytics
- **Establish governance** — data ownership models, business glossary, data contracts
- **Create migration plans** — structured paths from current state to target architecture

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Symptom recognition guide, QuickScan diagnostic, consulting workflow, and resource routing |
| `references/` | Discovery framework, maturity model, architecture patterns, data mesh readiness, event-driven products, platform evaluation, governance, compliance, anti-patterns, and case studies |
| `scripts/` | Interactive governance maturity assessment |
| `templates/` | Architecture decision record and data architecture design-session worksheets |
| `evals/` | Output-quality cases for architecture reviews, mesh adoption, data products, governance, and boundary routing |

## Triggers

Load this when your data pipelines are growing out of control, teams disagree on data definitions, you're choosing a data platform, assessing data mesh readiness, designing an event-driven data product, or planning a current-to-target data architecture. Do not use it for pipeline implementation, platform operations, interface contract semantics, SQL tuning, or data science model development.

## Requirements

No special system requirements. Designed for agentic AI assistants. Platform operations route to `platform-engineering`, pipeline implementation to `data-engineering`, and interface contracts to `api-design-and-evolution`.


## Quick Start

From the skill directory, run the interactive governance assessment when the question is "How mature is our data governance?":

```bash
python3 scripts/governance-assessment.py
```

For architecture reviews, platform decisions, data mesh assessments, or design sessions, load `SKILL.md` and follow its task-specific reference routing.
