# Adr Authoring

Preserve the reasoning behind consequential architecture choices so later contributors can understand, revisit, or supersede them responsibly.

## Why Install This Skill

Architecture decisions are hard to revisit when records hide the rejected alternatives or confuse approval with delivery. This skill captures the reasoning, costs, and scope so future contributors can understand what was actually decided.

It follows your repository's existing template, folder layout, and amendment policy. Proposals, approved experiments, production decisions, and implementation evidence remain distinct, with links to the checks that support each claim.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Repository conventions, decision scope, lifecycle, and evidence rules. |
| `evals/` | Cases covering local conventions, experiment approval, lifecycle, and evidence quality. |
| `references/` | Reference material for ADR formats, lifecycle, sustainability, fitness-function design, and provenance. |
| `templates/fitness-function-record.md` | Fillable record connecting an ADR decision to a check and observed evidence. |

## Quick Start

Ask: “Draft an ADR for this decision using our repository conventions. Separate the approved scope from implementation evidence.” The result follows your existing decision log and identifies any unresolved approval or validation gaps.

## Triggers

- Write, review, and maintain architecture decision records with clear context, alternatives, consequences, confirmation links, and lifecycle governance. Use when a consequential technical decision or its enforceable architectural constraint must remain understandable.
- Define or review a fitness function's scope, cadence, evidence, threshold, ownership, exception handling, gaming resistance, review, or retirement.
- Do not use for system-wide evolutionary architecture design, general observability, or operating a named test or CI tool.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

No runtime dependency.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
