# Phase Gate Methodology

The four gates that enforce quality at each SDD phase transition. Every gate asks the same question: **"Is the artifact for this phase complete, correct, and unambiguous enough for the next phase to proceed safely?"**

## The Four Gates

```
SPECIFY → [GATE 1] → DECOMPOSE → [GATE 2] → IMPLEMENT → [GATE 3] → VERIFY → [GATE 4] → DELIVER
  Spec Review       Plan Review      Impl Review          Acceptance Review
```

## Gate 1: Spec Review

**Reviews:** SPEC.md
**Question:** Is the spec complete, unambiguous, and testable enough for work decomposition?

**Checklist:**
- [ ] Every acceptance criterion is testable (binary PASS/FAIL)
- [ ] Edge cases are explicitly enumerated, not implied
- [ ] Non-functional requirements have measurable thresholds
- [ ] Scope boundary is clear (explicit in-scope AND out-of-scope)
- [ ] Data contracts and interface definitions are sufficiently precise
- [ ] No section leaves room for the agent to make an unguided assumption
- [ ] Assumptions and open questions are documented

## Gate 2: Plan Review

**Reviews:** TASK-PLAN.md
**Question:** Does every spec requirement map to a task? Are dependencies real?

**Checklist:**
- [ ] Every specification requirement maps to at least one task
- [ ] Dependencies are real and spec-derived (not invented)
- [ ] Each task is independently implementable and verifiable
- [ ] Task sizes are appropriate for a single implementation session (30-120 min)
- [ ] The implementation handoff (CLAUDE.md, .cursorrules, AGENTS.md) accurately represents the spec and plan
- [ ] No task exceeds the scope of any single spec section

## Gate 3: Implementation Review

**Reviews:** Implementation output (code, config, docs) against TASK-PLAN.md
**Question:** Does the implementation satisfy all acceptance criteria for completed tasks?

This gate checks spec compliance. A separate engineering review lane assesses maintainability and relevant architectural consequences before integration; use [factory review lanes](factory-review-lanes.md). Keep its verdict distinct from behavioral acceptance without adding or renumbering SDD gates.

**Checklist:**
- [ ] All task acceptance criteria are satisfied
- [ ] Any deviations from the spec are documented (not silently introduced)
- [ ] Implementation produces correct results for all specified inputs
- [ ] Error states are handled per the spec
- [ ] Interface contracts are honored (return types, error formats, status codes)

## Gate 4: Acceptance Review

**Reviews:** VERIFICATION.md
**Question:** Does the integrated candidate have current, sufficient behavioral and engineering evidence for delivery?

**Checklist:**
- [ ] All spec ACs are accounted for in the verification matrix
- [ ] BLOCKING failures are resolved (none remain open)
- [ ] CRITICAL failures have documented remediation plans or exceptions
- [ ] Required behavior and engineering lanes permit delivery on the same integrated candidate; aggregate scores cannot override unresolved required criteria
- [ ] Any exceptions are documented with owner and due date

## Gate Decision Format

Every gate produces one of three verdicts:

| Verdict | Meaning | What happens next |
|---------|---------|-------------------|
| APPROVED | Artifact passes all criteria. Next phase may proceed. | Deliver artifact to next phase |
| CONDITIONS | Artifact passes subject to specific remediations that don't require full re-review | Deliver artifact + conditions list; next phase may proceed while conditions are resolved |
| REJECTED | Artifact fails one or more criteria. Current phase must produce a revised artifact. | Return artifact to current phase; no downstream work starts |

## Candidate, assumptions, and handoffs

Use `templates/REVIEW.md` to bind every gate verdict to the exact candidate and
acceptance contract, with executed check/environment/result/evidence records.
Read `references/review-records.md` for candidate invalidation, the assumptions
ledger, finding handoffs, and worked transition challenges. Reconcile the record
with the actual artifacts before advancing a phase or delivering.

CONDITIONS never waives authority or a consequential unresolved assumption. Name
which work may proceed, who owns each condition, and the latest safe boundary;
stop dependent merge/release or other effects before that boundary until the
required decision and evidence exist. An aggregate score cannot override this.

## Finding Severity

| Severity | Definition | Disposition |
|----------|-----------|-------------|
| BLOCKING | Issue makes the next phase impossible or produces guaranteed-defective output | Gate cannot pass |
| CRITICAL | Issue significantly impacts quality but next phase can proceed with documented exception | Gate passes with conditions |
| MINOR | Issue should be fixed but doesn't block the phase | Gate can pass with remediation plan |
| INFO | Observation or suggestion, no correctness impact | Informational |

## Escalation

When the reviewer and artifact author disagree on a finding:

1. Document the disagreement — what the artifact says, what the reviewer found, why the author disagrees
2. Escalate to the human orchestrator if the finding is BLOCKING or CRITICAL
3. MINOR and INFO disagreements are resolved by the reviewer's determination — the gate is not delayed for editorial preferences

## The Gate Philosophy

In SDD, early phase gates reduce avoidable rework. They complement behavioral verification and engineering review; they do not replace either. A defect caught at Gate 1 (spec review) costs minutes to fix. The same defect caught at Gate 4 (acceptance review) costs hours — the implementation may need to be discarded and rewritten against a corrected spec.

This is the fundamental insight: **shift quality left.** The cheapest defect is the one caught before a single line of code is written.
