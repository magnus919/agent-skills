# gap-analysis

Evidence-based comparison of a current state with a justified target state, producing actionable and reviewable decisions.

## Why Install This Skill

A gap analysis is easy to make look rigorous: add a current column, a target column, and a red/amber/green score. This skill teaches the harder part: defining a target that is actually warranted, collecting evidence that matches the question, separating observations from causes, and making trade-offs and uncertainty visible.

After installing it, an agent can produce gap registers, capability and maturity assessments, process and operating-model reviews, compliance/readiness assessments, and research-evidence gap analyses. The included templates are designed to be adapted, not treated as a universal scoring system.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Method, routing, quality gates, and completion boundary |
| `references/` | Research-grounded methodology, variants, prioritization, examples, and source index |
| `templates/` | Gap register plus capability, process, compliance/readiness, and research variants |
| `scripts/validate-register.py` | Dependency-free checker for a JSON gap register |
| `evals/evals.json` | Output-quality cases for evidence, ambiguity, prioritization, and variants |

## Quick Start

No installation or API key is required. Read `SKILL.md`, choose a context template, and keep current evidence, target authority, confidence, owner, and closure test visible for every material gap.

For a machine-checkable register:

```sh
python3 gap-analysis/scripts/validate-register.py path/to/register.json
```

## Triggers

Load this skill when you need to compare current and desired states for a capability, process, control, readiness decision, maturity question, operating model, or research evidence base.

## Requirements

- No external dependencies for the methodology or templates.
- Python 3 for the optional validator script.
- A defined decision, outcome, requirement, benchmark, or stakeholder target. Without one, the first deliverable is scoping, not a completed gap analysis.
