# SDLC Stages

Each stage below defines **entry conditions** (what must be true to start),
**required evidence** (what you must gather or produce), **exit conditions**
(what must be true to leave), and **escalation rules** (when to stop and hand to
a human). The spine in `SKILL.md` is the order; this file is the detail.

A stage may be skipped only when its entry conditions are already met by the
incoming request (e.g. a fully-specified contract skips most of Framing). Record
every skip and why in the evidence ledger.

---

## Stage 1 — Frame the change contract

**Entry:** A request that could justify a change.

**Do:**
- State the user-visible problem in one or two sentences.
- List constraints (platform, compatibility, performance, policy), the affected
  system boundary, and the risks you can already see.
- State explicit **non-goals** — what this change will *not* do.
- Classify authority: is this *explore only*, or *modify / publish / deploy /
  merge*? When unclear, assume explore and ask.
- Decide whether any change is justified at all. "No change needed" is a valid,
  evidence-backed outcome.

**Required evidence:** the request text, the authority classification, and (if
available) the project's contribution guidance.

**Exit:** A change contract exists (use [../templates/change-contract.md](../templates/change-contract.md))
OR a documented decision that no change is warranted.

**Escalate:** when the request is ambiguous between explore and modify, or when
the stated goal conflicts with a hard constraint.

---

## Stage 2 — Discover before designing

**Entry:** A framed contract (or a documented no-change decision to confirm).

**Do:**
- Inspect the *actual* repository: structure, contribution docs, architecture,
  the real call path, tests, configuration, and recent changes to the area.
- Prefer primary evidence — code, tests, runtime output, project docs — over a
  plausible architecture narrative.
- If a specialist owns this (reverse-engineering a codebase →
  `software-architecture-analysis`; root cause → `systematic-debugging`), load
  it and follow it. Note in the ledger if the specialist was unavailable.
- Write down every unverified assumption and every access gap.

**Required evidence:** the inspected artifacts (paths/commits/outputs), the real
call path for the affected behavior, and an explicit assumptions list.

**Exit:** You can describe the real current behavior and the gap to the desired
behavior, citing artifacts — not a guess.

**Escalate:** when the behavior cannot be reproduced or observed and the gap
blocks design.

---

## Stage 3 — Select the smallest safe intervention

**Entry:** A verified understanding of current vs. desired behavior.

**Do:**
- Reuse existing code and platform capabilities first. Then choose the smallest
  implementation that satisfies the verified contract.
- Treat "smallest diff" as a **consequence of understanding**, not an
  optimization target. Do not compress to win a metric.
- **Minimalism is conditional.** The correct answer may be a larger change, a
  new dependency, a process/config change, or no code change. Pick by evidence,
  not by reflex.
- Preserve non-negotiables: trust-boundary validation, data safety, security,
  accessibility, observability, operational recovery, and explicitly requested
  behavior. Never trade these for brevity.
- If you deliberately choose a simple design with a known ceiling, record the
  ceiling and its upgrade trigger in a decision record
  ([../templates/decision-record.md](../templates/decision-record.md)).

**Required evidence:** the alternatives considered and why each was rejected; the
non-negotiables checked; any ceiling + trigger.

**Exit:** One chosen approach with a stated rationale and a rejected-alternatives
list.

**Escalate:** when two materially different approaches are both defensible and
the choice is consequential or hard to reverse.

---

## Stage 4 — Execute by stage

Route the chosen work to the stage that owns it and follow that stage's method
(load the specialist skill where one exists):

- **Discovery / requirements** → problem framing, stakeholders, acceptance
  criteria, edge cases. Specialist: `product-discovery`.
- **Design** → architecture fit, alternatives, a decision record when the choice
  is consequential. Specialist: `spec-driven-development` for formal specs;
  `product-design-and-ux` for user-facing behavior, interaction, or information
  architecture; `api-design-and-evolution` for an interface contract.
- **Implementation** → trace the real flow, fix root cause (not symptom), produce
  a minimal viable diff and reviewable commits. Specialist: `systematic-debugging`
  for bugs. For security-sensitive changes (untrusted input, auth, secrets,
  trust-boundary crossings), load `secure-software-engineering`; for accessible
  UI, load `web-accessibility`.
- **Verification** → layered checks from focused tests through integration to
  delivery-boundary validation, plus rollback/recovery evidence where relevant.
  Specialist: `verification-methodology`; `qa-methodology` for test strategy and
  regression coverage.
- **Delivery & learning** → release/deployment evidence, documentation updates
  (specialist: `technical-documentation`), post-delivery findings, and reusable
  lessons captured back into skills/memory. For reliability objectives, incident
  response, or operational recovery, load `site-reliability-engineering`.

**Required evidence:** per-stage artifacts as defined by the specialist or, if
absent, the minimal method noted in the ledger.

**Exit:** The stage's own exit conditions, plus an updated ledger.

**Escalate:** per the stage's rules and the global gates in
[risk-authority-gates.md](risk-authority-gates.md).

---

## Stage 5 — Verify at the target boundary

**Entry:** An implementation that claims to satisfy the contract.

**Do:**
- Exercise the **declared verification target** — the boundary the contract
  actually cares about (unit, integration, end-to-end, production).
- Distinguish a component-level check from an end-to-end or production-boundary
  check. State which one ran.
- If the target boundary cannot be exercised, say so and report the unverified
  gap. Do not substitute a weaker check and call it done.

**Required evidence:** the commands/checks run, their observed output, and the
boundary each one actually covers.

**Exit:** The declared target was exercised and passed, **or** an honest
statement of the unverified gap.

**Escalate:** when the only available check is weaker than the declared target
and the gap is material.

---

## Stage 6 — Deliver and learn

**Entry:** A verified (or honestly gap-declared) change with authority to deliver.

**Do:**
- Produce release/deployment evidence appropriate to the change.
- Update documentation affected by the change.
- Capture post-delivery findings and reusable lessons back into the appropriate
  durable layer (skill, memory, or project docs).

**Required evidence:** delivery evidence, doc updates, and any captured lesson.

**Exit:** Delivered with evidence, or blocked with a stated reason.

**Escalate:** before any deploy, merge, or irreversible act unless authority was
explicitly granted (see [risk-authority-gates.md](risk-authority-gates.md)).

---

## Change-request gates

When neckbeard runs the change-request journey
([journey.md](journey.md)), five explicit gates block phase
progression. Gate **numbering groups gates by area** and does **not** imply
chronological order. The execution sequence is:

> gate 1 → gate 3 → gate 2 → gate 4 → gate 5

Every gate produces a verdict recorded in the delivery packet
([delivery-packet.md](delivery-packet.md), group (h)) with the gate identifier,
verdict, evidence references, and the exact head SHA at which the verdict was
reached.

### Verdict semantics

Each gate verdict is one of three values with operational consequences:

| Verdict | Meaning |
|---|---|
| **pass** | The phase may exit and the next phase may start. |
| **conditional** | The phase may exit only with recorded conditions. Each condition is tracked and must be **closed before the next gate** is evaluated. Open conditions at the next gate are a protocol error. |
| **blocked** | The phase **may not exit**. The run stops and escalates per [risk-authority-gates.md](risk-authority-gates.md). The delivery packet transitions to the **blocked** lifecycle state (see [delivery-packet.md](delivery-packet.md), blocked-state semantics). |

### Gate 1 — Architecture/design delta approval

**Gates:** entry into phase 4 (specification and work decomposition).

The architecture delta, design decisions, risk assessment, compatibility
analysis, migration strategy, and rollback plan produced in phase 3 must be
**approved** before specification and task-planning work begins. The gate
requires an approval verdict — not merely the existence of design artifacts.

**Inputs:** architecture delta / ADR / C4 output from phase 3 (see
`software-architecture-analysis`, `adr-authoring`, `c4-diagramming` in the
[routing table](routing-table.md)).

**No-delta path:** when the change has no architecture impact, the gate is
satisfied by a **documented "no architecture delta" determination** recorded in
the packet (group (f)). The gate is never silently skipped.

**Verdict owner:** phase 3 (architecture/design delta and risk assessment).

### Gate 3 — Specification and task-plan completeness

**Gates:** exit from phase 4 (specification and work decomposition).

Chronologically the second gate. Planning may not complete until:

- `SPEC.md` exists with acceptance criteria **mapped to the change contract**;
- `TASK-PLAN.md` covers **every** spec item and acceptance criterion;
- no task is unbounded (missing effort/scope estimate) or ownerless (no
  assigned phase or specialist).

**Inputs:** `SPEC.md` and `TASK-PLAN.md` produced under
`spec-driven-development` (see [routing table](routing-table.md)).

**Verdict owner:** phase 4. The verdict is recorded **before** the planning
phase exits.

### Gate 2 — QA-owned test and verification plan

**Gates:** entry into phase 6 (domain-specific implementation).

Chronologically the third gate. A test strategy and verification plan must
exist and be approved **before implementation begins**.

**Operational rule:** no implementation work — code edits, commits, or
branch work beyond the packet — may occur until the QA-plan verdict is
recorded in the packet. "Implementation begins" means the first
implementation-phase commit or edit, not planning discussion.

**Inputs:** `VERIFICATION-PLAN.md` naming verification targets, test levels
(unit / integration / end-to-end), regression coverage strategy, and the
evidence artifacts that constitute a passing verification.

**Verdict owner:** phase 5 (pre-implementation test and verification
planning). The plan is produced under `qa-methodology`
(see [routing table](routing-table.md)), establishing independence between
planning and execution. Post-hoc self-approval by the implementer is not
permitted.

**No-new-tests path:** when the change requires no new tests (e.g., a
docs-only change), that determination is documented with a reason in the
packet rather than silently omitting the gate.

**Distinction:** this gate checks the **plan's** existence and adequacy, not
the test results — those are produced later under gate 5.

### Gate 4 — Independent review

**Gates:** exit from phase 7 (independent review and boundary verification).

Chronologically the fourth gate. An independent review covering qualities
**not captured by the specification** — this is **not** a spec-compliance
re-check. Spec compliance is verified at gate 3; gate 4 verifies
maintainability, security posture, accessibility conformance, documentation
clarity, and architectural coherence.

**Per-dimension reviewer mapping:**

| Review dimension | Specialist(s) |
|---|---|
| Code quality | `programming-principles` |
| Architecture consistency | `software-architecture-analysis` + `c4-diagramming` |
| Security | `secure-software-engineering` / `security-audit-methodology` |
| Accessibility | `web-accessibility` |
| Documentation | `technical-documentation` |

**Per-dimension coverage:** the review verdict records which dimensions were
covered and, for any dimension that is out of scope for the change, a
documented reason (e.g., "accessibility: out of scope — no user-facing
markup modified"). A reviewer can determine from the verdict both who
reviewed each dimension and whether each was covered.

**Verdict owner:** phase 7. The verdict is **distinct** from the
spec-compliance verdict at gate 3; a completed packet shows two separate
verdicts.

### Gate 5 — Boundary verification

**Gates:** final acceptance (phase 8 readiness).

Chronologically the fifth gate. Boundary verification exercises the declared
verification target (unit, integration, end-to-end, or production boundary)
after implementation is complete.

**Re-verification after material change:** any material review-driven change
invalidates the prior verification verdict and requires re-verification. The
verification verdict is bound to the **exact head SHA** at the time it was
performed; a verdict bound to a stale SHA does not satisfy this gate. For
gate satisfaction, the verdict SHA must equal the final head SHA.

**Material change definition (canonical).** This is the single source of
truth for materiality referenced by [journey.md](journey.md),
[lifecycle.md](lifecycle.md), and
[delivery-packet.md](delivery-packet.md):

- **Material** (invalidates prior verdicts, requires re-verification):
  a change that alters logic, adds or removes functionality, modifies the
  verification surface, changes test assertions, or alters data flow across
  a trust boundary.
- **Non-material** (prior verdicts stand; SHA binding updated):
  typo fixes, formatting-only changes, comment-only edits, pure renames
  without behavior change, docs-only changes, and rebases that produce no
  semantic diff.

After a **non-material** change, the recorded head SHA in the packet is
updated to the current SHA and the update itself is logged (old SHA → new
SHA, materiality: non-material). Prior verdicts are not re-run. After a
**material** change, affected gates re-run and new verdicts are bound to the
new head SHA.

**Verdict owner:** phase 7 (initial verification); re-verification after
material review-driven changes re-enters phase 7.

---

## Delivery paths

Four named paths determine which of the nine journey phases are mandatory
and which are conditional. **This section is the single source of truth for
path/phase matrices**; [journey.md](journey.md) references these definitions
rather than maintaining its own copy.

Path selection is recorded in the delivery packet (group (b)). When a
conditional phase is skipped, the skip is recorded in the packet (group (e))
with a concrete reason citing the path rule — silent omission is prohibited
(see [delivery-packet.md](delivery-packet.md), skip transparency).

### Phase reference

The nine journey phases (see [journey.md](journey.md) for full definitions):

1. Intake and provenance
2. Current-state discovery and reproduction
3. Architecture/design delta and risk assessment
4. Specification and work decomposition
5. Pre-implementation test and verification planning
6. Domain-specific implementation
7. Independent review and boundary verification
8. Readiness, CI/review loops, exact-final-head re-verification
9. Authorized post-merge release and closeout

### Path matrices

| Phase | Lightweight | Full | Refactor | High-risk |
|---|---|---|---|---|
| 1 — Intake and provenance | **mandatory** | **mandatory** | **mandatory** | **mandatory** |
| 2 — Discovery and reproduction | conditional | **mandatory** | **mandatory** | **mandatory** |
| 3 — Architecture/design delta | conditional | **mandatory** | **mandatory** | **mandatory** |
| 4 — Specification and decomposition | conditional | **mandatory** | conditional | **mandatory** |
| 5 — Test and verification planning | conditional | **mandatory** | conditional | **mandatory** |
| 6 — Implementation | **mandatory** | **mandatory** | **mandatory** | **mandatory** |
| 7 — Review and boundary verification | **mandatory** | **mandatory** | **mandatory** | **mandatory** |
| 8 — Readiness and re-verification | **mandatory** | **mandatory** | **mandatory** | **mandatory** |
| 9 — Release and closeout | **mandatory** | **mandatory** | **mandatory** | **mandatory** |

### Lightweight path

For narrow, low-risk changes (single-surface bug fix, docs-only, config
tweak). Mandates phases 1, 6, 7, 8, 9.

**Dropped phases with skip criteria:**

| Dropped phase | Skip criterion |
|---|---|
| 2 — Discovery and reproduction | The change surface is a single function or module and the current behavior is already understood from the change request; no reproduction is needed. |
| 3 — Architecture/design delta | No module boundary, service dependency, cross-component contract, or system-level structure is affected (per the `software-architecture-analysis` skip rule in the [routing table](routing-table.md)). |
| 4 — Specification and decomposition | The change is fully described by the change contract with testable acceptance criteria; no separate `SPEC.md` or phased decomposition is needed (per the `spec-driven-development` skip rule). |
| 5 — Test and verification planning | No `VERIFICATION-PLAN.md` is required beyond the implementer's own focused tests; the change introduces no new verification surface (per the `qa-methodology` skip rule). |

Each skip is recorded with its criterion in packet group (e). Gates 1, 3,
and 2 are conditional on this path (skipped with their phases); gates 4 and
5 remain mandatory.

### Full path

For standard feature work. **All nine phases are mandatory.** All five gates
apply. No phase may be skipped.

### Refactor path

For behavior-preserving structural changes (rename, extract, reorganize).
Mandates phases 1, 2, 3, 6, 7, 8, 9 — discovery and architecture review are
always required to confirm behavior preservation.

**Conditional phases:**

| Conditional phase | Skip criterion |
|---|---|
| 4 — Specification and decomposition | The refactor is fully characterized by the architecture delta and characterization-test plan; no separate `SPEC.md` is needed because no behavior changes. |
| 5 — Test and verification planning | Existing characterization tests cover the affected surface and no new verification plan is needed; the test strategy is recorded as "existing suite, no additions." |

Gates 1, 4, and 5 are always mandatory on this path. Gates 3 and 2 are
conditional (skipped only with their phases, with recorded reasons).
Behavior-preservation evidence (characterization tests passing before and
after) is the gate 5 criterion.

### High-risk path

For changes with safety, security, compliance, or production-criticality
concerns (schema migrations, trust-boundary changes, SLO-affecting work).
**All nine phases are mandatory. All five gates apply with no conditional
skips.** No phase or gate may be skipped regardless of apparent scope.
Escalation review is required at gate 1, gate 2, and gate 5 boundaries.
