# Data Architect

Make data architecture choices grounded in workload, ownership, operating cost, and evidence.

## Why Install This Skill

Choosing a store or platform should start with the decision in front of you. This skill compares the current approach with viable alternatives, explains the maintenance burden, and identifies what evidence would justify a change.

For a small transactional service, it focuses on correctness, recovery, and the team's ability to operate it. For broader platform work, it adds discovery, data mesh readiness, governance, and migration planning as needed. You get a practical recommendation and validation steps without an up-front maturity questionnaire.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Decision workflow, tradeoff rules, evidence requirements, and resource routing |
| `references/` | Discovery framework, maturity model, architecture patterns, data mesh readiness, event-driven products, platform evaluation, governance, compliance, anti-patterns, and case studies |
| `scripts/` | Interactive governance maturity assessment |
| `templates/` | Architecture decision record and data architecture design-session worksheets |
| `evals/` | Output-quality cases for architecture reviews, mesh adoption, data products, governance, and boundary routing |

## Triggers

Load this when your data pipelines are growing out of control, teams disagree on data definitions, you're choosing a data platform, assessing data mesh readiness, designing an event-driven data product, or planning a current-to-target data architecture. Do not use it for pipeline implementation, platform operations, interface contract semantics, SQL tuning, or data science model development.

## Requirements

No runtime needed for the guidance; Python 3 for the optional governance assessment. Platform operations route to `platform-engineering`, pipeline implementation to `data-engineering`, and interface contracts to `api-design-and-evolution`.


## Quick Start

Ask: “Compare our current transactional store with the proposed alternative, including ownership, recovery evidence, and conditions that would change the recommendation.”

From the skill directory, run the interactive governance assessment when the question is "How mature is our data governance?":

```bash
python3 scripts/governance-assessment.py
```

For architecture reviews, platform decisions, data mesh assessments, or design sessions, load `SKILL.md` and follow its task-specific reference routing.
