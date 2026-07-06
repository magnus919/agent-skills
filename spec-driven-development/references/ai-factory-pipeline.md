# The AI Software Factory Pipeline

The canonical 5-phase pipeline for spec-driven code generation. Each phase produces an artifact that passes through a gate before the next phase begins.

## Pipeline Diagram

```
INCEPTION → [SPECIFY] → GATE 1 → [DECOMPOSE] → GATE 2 → [IMPLEMENT] → GATE 3 → [VERIFY] → GATE 4 → DELIVER
                │                      │               │              │
          Produces:              Produces:        Produces:       Produces:
          SPEC.md                TASK-PLAN.md     Code/PRs        VERIFICATION.md
```

## Phase 1: Spec Authoring (SPECIFY)

**Input:** Raw requirements — conversation, ticket, PRD, user research, competitive analysis

**Output:** SPEC.md

**Who writes it:** A human domain expert, an AI spec-authoring agent guided by a human, or both in collaboration

**What SPEC.md contains:**
1. Problem statement — what problem this solves and why it matters
2. Success criteria — measurable outcomes that define success
3. Scope boundary — explicit in-scope and out-of-scope
4. User stories — prioritized, each with acceptance criteria
5. Acceptance criteria — per-story, Given/When/Then or bulleted pass/fail
6. Edge cases — explicit boundary conditions, error states, invalid inputs
7. Non-functional requirements — performance, security, observability, compliance
8. Data contracts / interfaces — schemas, APIs, events
9. Assumptions & open questions — documented for resolution planning

**Gate 1: Spec Review** — Is the spec complete, unambiguous, and testable enough for decomposition? Pass quality gates first.

## Phase 2: Work Decomposition (DECOMPOSE)

**Input:** Reviewed, approved SPEC.md

**Output:** TASK-PLAN.md

**Principle:** The spec IS the plan. This phase does not invent work — it extracts an execution sequence from the spec's defined behaviors.

**Rules:**
- Every spec requirement maps to at least one task
- Each task is independently implementable and verifiable
- No task exceeds one session of AI agent work (30-120 minutes)
- Dependencies are real and spec-derived (not invented)
- Each task body includes a `Spec: -- section X` reference back to SPEC.md

**Gate 2: Plan Review** — Does every spec requirement have a covering task? Are dependencies honest? Is each task independently implementable?

## Phase 3: Implementation (IMPLEMENT)

**Input:** TASK-PLAN.md per-task directives

**Output:** Code, configs, documentation changes (typically as a PR)

**Who implements:** AI coding agents, each working on one task at a time

**Rules:**
- Each task is implemented as an independent unit
- Contract interfaces defined in the spec are the coordination mechanism between parallel tasks
- Deviations from the spec are explicitly documented, not silently introduced
- The spec is the ground truth — implementation must satisfy all ACs

**Gate 3: Implementation Review** — Does the implementation satisfy all acceptance criteria for completed tasks? This is NOT a general code review — it checks spec compliance only.

## Phase 4: Verification (VERIFY)

**Input:** Implementation artifacts, SPEC.md acceptance criteria

**Output:** VERIFICATION.md with pass/fail matrix

**Method:** Every acceptance criterion from the spec is tested against the implementation. Verification covers:
- Functional correctness — does output match expected for each input?
- Behavioral completeness — are all scenarios handled (including edge cases)?
- Contract compliance — do interfaces match spec definitions?
- Non-functional requirements — do performance/security thresholds pass?
- Negative testing — are invalid inputs correctly rejected?

**Severity classification:**
| Severity | Definition | Gate Impact |
|----------|-----------|-------------|
| BLOCKING | AC failed, no workaround — core requirement unmet | Gate does not pass |
| CRITICAL | AC failed but feasible workaround exists | Gate does not pass without documented exception |
| MINOR | AC passes suboptimally | Gate can pass with remediation plan |
| INFO | Observation, no pass/fail impact | Informational |

**Gate 4: Acceptance Review** — All BLOCKING failures resolved? CRITICAL failures documented? Compliance score adequate?

## Phase 5: Delivery (DELIVER)

**Input:** Approved VERIFICATION.md, implementation artifacts

**Output:** Merged PR, deployed feature

**Gate:** Only passed if verification report shows no BLOCKING failures and all CRITICAL failures have documented exceptions.

## Parallel Task Execution

When the spec has independent features with no dependency chain, multiple AI agents can implement tasks in parallel. The coordination mechanism:

1. **Contracts first:** Shared interfaces (API schemas, data contracts) are defined in the spec and are the first tasks implemented
2. **Independent tasks:** Tasks with no interdependencies run in parallel
3. **Dependent tasks:** Sequential execution with contract verification at each handoff

## The Pipeline Template

The pipeline is a template, not a straitjacket. Common variations:

- **Greenfield project:** Full 5-phase pipeline from INCEPTION to DELIVER
- **Feature addition:** Phases 1-4 (spec through verify) against an existing codebase
- **Bug fix:** Compressed pipeline — spec-only for the fix scope, implement, verify
- **Refactor:** No new spec — spec is inferred from existing behavior, verified after refactor
