---
name: spec-driven-development
description: Spec-Driven Development (SDD) methodology for AI software factories —
  where structured specifications are the input, AI agents generate the code, and
  quality gates enforce correctness at each pipeline phase. Use when designing a spec
  → review → decompose → implement → verify pipeline that any AI coding tool (Claude
  Code, Cursor, Hermes Agent, Devin, OpenHands) can follow.
license: MIT
compatibility: Tool-agnostic — methodology applies to any AI coding agent. Templates
  use markdown and Gherkin. Scripts require bash.
metadata:
  source: https://github.com/magnus919/agent-skills/spec-driven-development
  spec-version: 1.2.0
  hermes: tags=["sdd", "specifications", "ai-code-generation", "software-factory",
    "bdd", "gherkin", "quality-gates", "phase-gates"], related_skills=["sdd-authoring",
    "sdd-review", "sdd-verification", "sdd-work-decomposition"]
---

# Spec-Driven Development for AI Software Factories

A methodology for building software where **specifications are the executable input** to an AI code generation pipeline. The factory model: specs are blueprints, AI agents are the assembly line, verification is quality control, and gates catch defects before they compound.

## Pipeline Overview

```
INCEPTION → [SPECIFY] → REVIEW → [DECOMPOSE] → REVIEW → [IMPLEMENT] → REVIEW → [VERIFY] → DELIVER
                 ↑         ↑          ↑            ↑           ↑           ↑          ↑         ↓
            Phase 1    Gate 1    Phase 2       Gate 2    Phase 3      Gate 3    Phase 4   Gate 4
```

Each phase passes through a gate before the next begins. A defect caught at Gate 1 costs minutes to fix; the same defect found at Gate 4 costs hours.

> **SDD Core Principles**
> 1. **Precision over clarity.** A precise-but-dense spec is better than a readable-but-ambiguous one. The AI cannot ask for clarification — it implements one interpretation at random.
> 2. **Completeness over brevity.** Every missing acceptance criterion is a missing feature. Specifying an edge case upfront costs minutes; discovering it in production costs hours or days.
> 3. **Testability over descriptiveness.** An AC that cannot produce CLEAR PASS or CLEAR FAIL is not an AC — it's a hope.
> 4. **Gates catch defects early.** A Gate 1 (spec review) fix costs minutes. A Gate 4 (acceptance review) fix costs hours — the entire implementation may need to be discarded.
> 5. **Spec is the single source of truth.** Every downstream artifact traces back to the spec. Deviations are defects unless explicitly documented.
> 6. **Spec IS the test (when possible).** Gherkin-style ACs serve double duty as test cases. No separate test writing required.

## Loading Guide

| Reference | Load when | File |
|-----------|-----------|------|
| SDD Overview & Philosophy | You need to understand the *why* — the software factory metaphor, how SDD differs from traditional requirements, the core principle that specs are executable inputs not communication artifacts | `references/sdd-overview.md` |
| The AI Factory Pipeline | You need the full 5-phase pipeline with phase inputs, outputs, and transition rules — or you're designing a new pipeline from scratch | `references/ai-factory-pipeline.md` |
| Spec Quality Gates | You've written a SPEC.md and need to validate it before Gate 1 — the 7 gates that separate a good spec from a vague one | `references/spec-quality-gates.md` |
| Phase Gate Methodology | You're running a review gate (any of the 4) and need the decision criteria, verdict format, and escalation path | `references/phase-gate-methodology.md` |
| Methodology Selection Matrix | You're deciding which spec methodology (BDD, Formal, DbC, OpenAPI, ADRs) fits your context — when each applies and their AI-readiness ratings | `references/methodology-matrix.md` |
| NFR Encoding for AI Specs | You need to express non-functional requirements (performance, security, observability) in machine-readable format | `references/nfr-encoding.md` |
| Format Translation | You need to map between spec formats — Gherkin ↔ OpenAPI ↔ SPEC.md ↔ JSON Schema — or translate a human PRD into an AI-ready spec | `references/format-translation.md` |
| Critiques & Tradeoffs | You need to decide *when not* to use SDD — the honest limitations: spec bottleneck, GIGO, drift, over/under-specification, the formal methods tax | `references/critiques-and-tradeoffs.md` |
| Worked Example — Complete SPEC.md | You want to see a fully-realized specification to calibrate your output depth — shows proper AC format, edge case enumeration, NFR thresholds, data contracts, and assumptions for a password reset feature | `references/example-spec.md` |

## Methodology Quick-Pick

Not sure which spec methodology fits your situation? Use this quick reference table (load `references/methodology-matrix.md` for full depth):

| Concern | Reach For | AI-Readiness | Format Produces |
|---------|-----------|-------------|-----------------|
| REST API contracts | OpenAPI | VERY HIGH | YAML/JSON specification |
| Event/message schemas (Kafka, RabbitMQ) | AsyncAPI | HIGH | YAML/JSON channel specs |
| Behavioral requirements (what the system does) | BDD / Gherkin | HIGH | `.feature` files with Given/When/Then |
| Interface correctness (pre/post/invariants) | Design by Contract | VERY HIGH | Assertions in code |
| Distributed system correctness (consensus, protocols) | TLA+ / Alloy | VERY HIGH (narrow scope) | Mathematical model |
| Architecture decisions (why we chose X) | ADRs | MEDIUM | Structured markdown |
| System structure (boxes-and-lines) | C4 Model | MEDIUM-HIGH | PlantUML / structured text |
| Raw stakeholder intent | User Stories | LOW (needs refinement) | "As a... I want..." |

**Composite approach:** Most systems need 3-4 of these working together. REST APIs get OpenAPI, event streams get AsyncAPI, critical behavior gets Gherkin scenarios, and cross-team interface boundaries get DbC assertions.

## Templates

| Template | Pipeline Phase | File |
|----------|---------------|------|
| SPEC.md | **Phase 1** — Spec Authoring (SPECIFY). Write this first: problem, scope, user stories, ACs, edge cases, NFRs, data contracts | `templates/SPEC.md` |
| REVIEW.md | **Gate 1-4** — Phase-Gate Review. Use at every gate transition: spec review, plan review, implementation review, acceptance review | `templates/REVIEW.md` |
| TASK-PLAN.md | **Phase 2** — Work Decomposition (DECOMPOSE). Extract from an approved spec: task groups, dependency graph, per-task ACs, implementation directives | `templates/TASK-PLAN.md` |
| VERIFICATION.md | **Phase 4** — Verification (VERIFY). After implementation: AC pass/fail matrix, compliance score, failure dossiers with remediation | `templates/VERIFICATION.md` |

## Scripts

| Script | When to run | File |
|--------|-------------|------|
| `spec-quality-check.sh` | After writing or editing a SPEC.md — validates all required sections exist (problem statement, scope, ACs, edge cases, NFRs, assumptions) | `scripts/spec-quality-check.sh` |
| `spec-to-tasks.sh` | After writing a TASK-PLAN.md — validates every spec AC has a covering task reference | `scripts/spec-to-tasks.sh` |

## Trigger Conditions

Load this skill when:

- **You're building a software factory** — a system where AI agents produce code from structured specifications through a gated pipeline
- You're designing or refining an AI code generation pipeline where specs drive implementation
- You need to write a specification that an AI agent (not just a human) will consume
- You're evaluating spec methodologies (BDD, Formal, OpenAPI-first) for a project
- You need templates for SPEC.md, TASK-PLAN.md, REVIEW.md, or VERIFICATION.md
- You're reviewing or verifying AI-generated code against its specification

## Quick Reference: Pipeline Steps

| Step | Action | Load This Reference | Produces |
|------|--------|-------------------|----------|
| 1 | Write SPEC.md from template — problem, scope, stories, ACs, edge cases, NFRs | `references/spec-quality-gates.md` (validate before Gate 1) | `SPEC.md` |
| 2 | Run **spec-quality-check.sh** on SPEC.md | — | Validation report |
| 3 | **Gate 1** — Review spec against quality gates, produce REVIEW.md | `references/spec-quality-gates.md`, `references/phase-gate-methodology.md` | `REVIEW.md` (APPROVED/CONDITIONS/REJECTED) |
| 4 | Decompose approved spec into TASK-PLAN.md — each task traces to a spec section | `references/ai-factory-pipeline.md` (Decompose phase) | `TASK-PLAN.md` |
| 5 | **Gate 2** — Review task plan for dependency honesty, spec coverage | `references/phase-gate-methodology.md` | `REVIEW.md` |
| 6 | Implement each task — one task per agent session | — | Code/PR |
| 7 | **Gate 3** — Verify implementation against spec (not code style) | `references/phase-gate-methodology.md` | `REVIEW.md` |
| 8 | Run verification against all ACs — produce VERIFICATION.md | — | `VERIFICATION.md` |
| 9 | **Gate 4** — Review verification report, deliver only if no BLOCKING failures | `references/phase-gate-methodology.md` | Final approval |

For deeper methodology context, load `references/sdd-overview.md` (philosophy) or `references/ai-factory-pipeline.md` (full pipeline detail with parallel execution).

## Pipeline Mode & Entry Points

### Where to Enter the Pipeline

You don't always start at SPECIFY. Enter at the phase matching what you already have:

| You Have This | Enter At | Start With |
|-------------|----------|------------|
| A vague idea, conversation, or PRD | **Phase 1 — SPECIFY** | `templates/SPEC.md` + `references/format-translation.md` |
| Approved product scope with interaction contracts | **Phase 1 — SPECIFY** | [product-design-and-ux](../product-design-and-ux/SKILL.md) handoff + `templates/SPEC.md` |
| A clear, approved specification | **Phase 2 — DECOMPOSE** | `templates/TASK-PLAN.md` + `references/ai-factory-pipeline.md` |
| A spec + approved task plan | **Phase 3 — IMPLEMENT** | Task cards with per-task directives |
| Existing code needing verification | **Phase 4 — VERIFY** | `templates/VERIFICATION.md` |

### Which Pipeline Mode to Use

Not every change needs all 4 gates. Choose your mode:

| Mode | When to Use | Gates to Run | Spec Depth |
|------|-------------|-------------|------------|
| **Full** | Greenfield feature, multi-agent work, high-risk change, complex interfaces | All 4 gates | Full SPEC.md with ACs, NFRs, data contracts, edge cases |
| **Lightweight** | Simple bug fix, well-understood change, single-file edit | Gate 1 (light) → Implement → Gate 4 (light) | Single user story, 1-3 ACs, abbreviated NFRs |
| **Minimal** | Prototype, spike, exploration, throwaway code | None — skip formal gates | Mini-spec: 1 paragraph + 3 ACs. No NFR table, no contracts |

> **Rule of thumb:** If you know the fix in under 60 seconds and it touches one file, use Lightweight mode. If you're not sure what the right solution is, use Full mode — the gates will catch your mistakes early.

## Gate Recovery & Revision

What happens when a gate rejects your artifact? The pipeline doesn't stop — it iterates.

### The Revision Loop

```
Artifact submitted → Gate review → REJECTED or CONDITIONS
                                         ↓
                              Return to current phase
                                         ↓
                              Patch specific findings
                                         ↓
                              Resubmit for re-review
                                         ↓
                              APPROVED → next phase
```

### How to Patch, Not Rewrite

Each finding identifies a narrow, fixable defect. Patch at the finding's location:

| Finding Severity | Action | Example |
|-----------------|--------|---------|
| **BLOCKING** | Fix immediately — gate cannot pass until resolved | Rewrite untestable AC with binary PASS/FAIL condition |
| **CRITICAL** | Must fix. Gate may pass with documented exception if ≤2 findings | Add missing edge cases to User Stories section |
| **MINOR** | Fix before next phase if feasible. Gate can pass with remediation plan | Add request/response schemas to Data Contracts |
| **INFO** | Note for future improvement. No action required for gate pass | Suggestion for alternative field naming |

### Re-Review Scope

After patching, the reviewer determines scope:
- **Full re-review:** Required when REJECTED verdict. The entire artifact is re-evaluated, not just patched sections.
- **Targeted re-review:** Possible with CONDITIONS verdict. Only the affected findings and surrounding context are reviewed.

**Risk of partial fixes:** Fixing only BLOCKING findings and ignoring CRITICAL ones guarantees re-rejection at the same gate. The CRITICAL findings that cost minutes to fix at Gate 1 will cost hours if caught at Gate 4.

### Common Revision Patterns

| Failure Pattern | Fix Strategy | Prevention |
|----------------|-------------|------------|
| Untestable ACs (vague language like "should handle", "should be efficient") | Rewrite each AC with explicit Given/When/Then and binary outcome | Apply Gate 1 check before submitting |
| Missing edge cases | Add edge case enumeration per story — 3 minimum per story | Use the "five things that could go wrong" test from spec-quality-gates |
| Vague NFRs ("should be fast", "should be secure") | Replace with specific threshold + verification method | Use the "can I write a test for this?" test from nfr-encoding reference |
| Incomplete contracts (endpoint listed but no schemas) | Add full request/response schemas for every endpoint | Check Gate 5 before submitting |
| Scope creep (ambiguous in-scope items) | Tighten scope description and expand Out of Scope | Apply the "would someone include more than intended?" test

## Tool-Agnostic Design

This skill describes the **methodology**, not a specific tool. The pipeline works with:
- **Claude Code** — use CLAUDE.md as spec context, plan-then-implement mode
- **Cursor** — Plan Mode + .cursorrules for spec context, Agent Mode for implementation
- **Hermes Agent** — native SDD pipeline (authoring → review → decomposition → verification)
- **Devin / OpenHands** — task-based implementation from spec-derived task plans
- **GitHub Copilot Workspace** — issue-driven with spec as structured issue body
- **droid (Factory)** — task cards from spec decomposition

The templates are format-agnostic (markdown). Adapt the handoff mechanism (CLAUDE.md, .cursorrules, AGENTS.md) to your tool.
