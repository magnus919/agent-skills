# Spec-Driven Development for AI Software Factories

A methodology where structured specifications are the executable input to an AI code generation pipeline. Quality gates enforce correctness at each phase.

## Why Install This Skill

When your agent loads this skill, it becomes a **software factory designer** who can:

- **Design an SDD pipeline** — 5-phase pipeline from SPECIFY to DELIVER with 4 phase gates
- **Write great specs** — 7 spec quality gates that separate precise specs from vague ones
- **Choose spec methodologies** — BDD, OpenAPI, AsyncAPI, DbC, TLA+, ADRs, C4 — matched to your context
- **Encode NFRs** — performance, security, observability requirements in machine-readable format
- **Translate between formats** — PRD → SPEC.md → Gherkin → OpenAPI
- **Handle gate recovery** — revision workflows when specs fail review
- **Review consequential designs** — give a separate reader a bounded source pack, check their reconstruction before critique, and keep findings tied to a specific candidate
- **Review integrated releases** — check real behavior and maintainability separately without duplicating your existing planning documents

## What You Get

Regression cases include the relevant worked example with recorded source hashes.

Business-policy recipe, release template, and a read-only fictional loan evaluator with boundary tests.

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Pipeline overview, loading guide, methodology quick-pick |
| `references/` | Pipeline, quality gates, independent design review, review records, assumptions, methodology selection, NFRs, and worked examples |
| `templates/` | Specifications, task plans, candidate-bound reviews, verification, business-policy records, and separate behavior/engineering verdicts |
| `scripts/` | Spec/task validators, a review-input hash manifest, and a synthetic business-policy evaluator |
| `evals/` | Output-quality cases and challenge examples for review records, pipeline modes, and business-policy workflows |

## Triggers

Load this when designing a spec-driven pipeline, writing an AI-ready specification, or setting up quality gates for AI code generation.

## Requirements

Tool-agnostic — works with Claude Code, Cursor, Hermes Agent, Devin, OpenHands, droid, or any AI coding agent. Optional review-input hashing requires Python 3.10+; no model API or network access is required.


## Quick Start

Start with the pipeline mode that fits the change and use the linked template:
SPEC.md for intent, TASK-PLAN.md for approved work, or REVIEW.md for a phase
decision. To record the exact local files selected for an independent review:

```sh
python3 scripts/review_input_manifest.py --target docs/design.md --context README.md
```

The command prints JSON with the relative paths, byte sizes, per-file SHA-256
values, and a bundle hash; it does not print or copy file contents.

Review records bind approval to a candidate and acceptance contract. The SPEC
assumptions ledger gives provisional choices owners and safe decision deadlines;
finding handoffs retain ownership and verified closure. See
`references/review-records.md` for worked regression challenges.
