# ai-governance

Design and run an organization's AI governance system: principles, operating models and decision
rights, risk frameworks, lifecycle gates, and the fairness, transparency, privacy, security,
regulatory, and board-oversight controls that make AI accountable.

## Why Install This Skill

AI systems get deployed faster than the organizations that build them can decide who is
accountable for them, what risk they are allowed to carry, and what evidence should gate each
stage of their life. Without a working governance system, launches are rubber-stamped, risks are
surfaced too late, and "someone approved it" is rarely traceable to a named, evidence-backed
decision. This skill gives your agent a complete, field-tested framework for standing up and
operating AI governance — not a compliance checklist you copy, but a method you run.

After installing, your agent can stand up a governance program from scratch, tier AI use cases by
risk and prescribe the controls each one requires, review an LLM or agent system for governance
and safety gaps, map a regulation to a concrete compliance and control plan, score organizational
governance maturity and get a prioritized gap list, and prepare board-level reporting. It ships
dense references for each governance domain, including a GxP/data-integrity overlay, six fillable templates, and two executable scripts,
so the method turns into working artifacts instead of advice.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | The router: triggers, what the skill owns vs. doesn't, and when to load each file |
| `references/` (12 files) | Dense, scannable guides: principles, operating model, risk frameworks, lifecycle, fairness, transparency, privacy, LLM/agent security, regulation, procurement/board oversight, source index, and a GxP/data-integrity overlay |
| `templates/` (6 files) | Fillable artifacts: governance charter, use-case intake, model risk assessment, model card, third-party due diligence, board report |
| `scripts/governance-maturity.py` | CLI that scores an organization's governance maturity from JSON answers and lists gaps |
| `scripts/use-case-risk-tier.py` | CLI that classifies an AI use case into a risk tier and its required controls |
| `evals/evals.json` | Output-quality cases used to grade the skill |
| `README.md` | This human-facing overview |

## Quick Start

The skill is pure methodology plus two stdlib-only Python CLIs — there is nothing to install or
configure.

Score governance maturity from an answers file:

```sh
python3 ai-governance/scripts/governance-maturity.py path/to/answers.json --json
```

Classify a use case's risk tier:

```sh
python3 ai-governance/scripts/use-case-risk-tier.py path/to/use_case.json --json
```

Both scripts print a single JSON object; add `--dry-run` to preview without writing anything.
Example input shapes are documented in each script's `--help`.

## Triggers

Load this skill when you or your agent need to:

- Stand up or mature an AI governance program, or design the operating model and decision rights.
- Tier an AI use case by risk and decide which controls it needs before it ships.
- Review an LLM or agent system (e.g., an internal RAG copilot) for governance and safety gaps.
- Map a current regulation to a compliance and control plan.
- Score organizational governance maturity and prioritize gaps.
- Prepare board-level AI governance reporting or run third-party/model due diligence.
- Govern AI used in a GxP context, including ALCOA+, data integrity, electronic records, validation/assurance, audit trails, or QMS interfaces.

## Requirements

- Nothing to install for the methodology or the templates.
- The two scripts need Python 3 (standard library only; no third-party packages).
- No API keys, accounts, or external services.
- Note: this skill provides governance guidance, not legal, financial, or security advice.
