# Research Methodology

Turn an open question into a bounded, evidence-led investigation rather than a plausible-sounding synthesis.

## Why Install This Skill

Turn an open question into a bounded, evidence-led investigation rather than a plausible-sounding synthesis. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer. The method requires research to leave behind durable, source-linked artifacts that others can discover and reuse.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `industry-analysis.md`, `journalistic-research.md`, `research-lifecycle.md`, `source-evaluation.md`, `structured-analytic-techniques.md`, `synthesis-patterns.md`, `technical-verification.md` |
| `assets/` | Assets: `research-brief.md`, `research-log.md`, including a durable-artifact inventory and source-to-artifact preservation ledger. |

## Quick Start

Choose the research track in `SKILL.md`, then start from `assets/research-brief.md` and maintain a research log. Preserve the retained evidence and extracted claims in the long-lived research surface your agent and users normally use before delivering the synthesis.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Plan, conduct, evaluate, and synthesize rigorous research. Use for journalistic, industry, or technical investigations that need credible evidence and a traceable method.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

No runtime dependency. Use appropriate retrieval tools and retain source URLs and access dates in the research log.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
