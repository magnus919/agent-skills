# Change-Request Journey

The canonical platform-neutral journey for carrying a change request — an issue,
ticket, email, or verbal request — from intake through an authorized post-merge
release. This reference is loaded by [../SKILL.md](../SKILL.md) **only** for
change-request / issue-to-release work; ordinary fix/build/refactor tasks that
lack an issue or ticket trajectory continue to use the core loop in
[../SKILL.md](../SKILL.md) and the stage detail in [stages.md](stages.md).

This document defines the phase sequence, gates, routing rules, and paths. It
does **not** define a second orchestrator, main loop, or skill-loading mechanism.
[../SKILL.md](../SKILL.md) remains the single entry point and owns the top-level
decision of what happens next. The journey is a reference that SKILL.md loads and
follows — not a competing spine.

Every phase reads and writes the delivery packet
([delivery-packet.md](delivery-packet.md)); outputs flow between phases through
named packet field groups. Gate verdicts are recorded in packet group (h).
Skipped phases and skills are recorded in packet group (e) with concrete reasons;
silent omission is prohibited.

This journey is tracker-neutral: it speaks of *work items*, *state
transitions*, *review submissions*, and *merge or acceptance into the protected
target*, never of one platform's nouns. Which tracking system holds the work
item is established during phase 1 intake by
[tracker-discovery.md](tracker-discovery.md), and tracker operations route to
the matching catalog tooling skill; platform mechanics live in the platform
mapping rows below and in [lifecycle.md](lifecycle.md).

Entry normally begins at phase 1. When the work being requested **already
started elsewhere** — no delivery packet exists because the earlier run happened
outside this bundle — do not restart intake blindly: enter through
[position-assessment.md](position-assessment.md) first, then continue from the
assessed position under this journey's rules.

---

## The nine phases

### Phase 1 — Intake and provenance

| Field | Value |
|---|---|
| **Owner** | neckbeard framing step (core loop step 1) |
| **Input** | A change request: issue URL/number, ticket ID, email thread, or verbal request. |
| **Output** | Packet groups (a) provenance and (b) authority/mode/path populated: change-request URL/number and source type, repository, base ref, issue/comment snapshot including **repository conventions** (`CONTRIBUTING.md`, `AGENTS.md`, or equivalent) and **linked/referenced work** (related issues, PRs, commits); **tracking system** identified per [tracker-discovery.md](tracker-discovery.md) (detected from the request's own reference, repository-detected, or requester-confirmed — the specific basis recorded); granted authority class; selected workflow mode (GitHub or enterprise); selected path. A change contract ([../templates/change-contract.md](../templates/change-contract.md)) exists. |
| **Gate** | The intake gate: provenance, authority, repository conventions, linked work, and the identified tracking system are captured. No planning phase may begin until these fields are populated. |
| **Escalation** | Authority is ambiguous between explore and modify; or the stated goal conflicts with a hard constraint (security, data safety, policy, license); or maintainer direction conflicts with proceeding (see [risk-authority-gates.md](risk-authority-gates.md) stop rules). |
| **Platform mapping** | **GitHub mode:** issue body + comments + labels captured via `gh`; `CONTRIBUTING.md` and `.github/` conventions discovered per repository. **Enterprise mode:** ticket-tracker snapshot (ticket ID, description, comments); internal contribution governance or change-governance docs captured. |

### Phase 2 — Current-state discovery and reproduction

| Field | Value |
|---|---|
| **Owner** | neckbeard discovery step (core loop step 2); specialist routing via [routing-table.md](routing-table.md) |
| **Input** | Phase 1 output: change contract with provenance, authority, and repository conventions. |
| **Output** | Packet group (d) completed: baseline (pre-change) evidence with boundary labels (`component` / `integration` / `end-to-end` / `production`); problem restated from primary evidence; affected surfaces confirmed. **When the request is a bug:** reproduction evidence is mandatory — repro steps, observed vs. expected behavior, and environment/version — recorded in group (d) before phase 3 may proceed. **When the request is not a bug:** the output states "non-bug request — reproduction not required" and records the current-state evidence that was gathered. **For lightweight test-hardening:** record that the clean behavior is already correct, identify the named mutation or controlled weakening, and do not require a live production reproduction. |
| **Gate** | Current behavior is described from artifacts (code, tests, runtime output, project docs) — not a guess. For bugs, the reproduction is confirmed or the inability to reproduce is documented. For test-hardening, the clean baseline and the intended failure of the named weakening are the relevant evidence. |
| **Escalation** | Behavior cannot be reproduced or observed and the gap blocks design; or discovery reveals the request is a duplicate, already fixed, or a phantom issue (see no-change-needed termination below). |
| **Platform mapping** | **GitHub mode:** linked issues, referenced PRs, and commit history inspected via `gh` and `git log`. **Enterprise mode:** ticket-tracker linkage, internal wikis, and version-control history inspected. |

### Phase 3 — Architecture/design delta and risk assessment

| Field | Value |
|---|---|
| **Owner** | Routed specialists: `software-architecture-analysis`, `adr-authoring`, `c4-diagramming` as applicable (see [routing-table.md](routing-table.md)) |
| **Input** | Phase 2 output: verified current-state evidence and baseline. |
| **Output** | Packet group (f): architecture delta (or a documented "no architecture delta" determination); design decisions and rejected alternatives; risks; compatibility analysis; migration strategy; rollback plan. Architecture delta / ADR / C4 artifacts produced at their canonical paths. |
| **Gate** | **Gate 1** — architecture/design delta approval (see [stages.md](stages.md)). The delta, decisions, risks, and rollback plan must be **approved** before specification work begins. No-delta path: a documented "no architecture delta" determination satisfies the gate; it is never silently skipped. |
| **Escalation** | Two materially different design approaches are both defensible and the choice is consequential or hard to reverse (see [risk-authority-gates.md](risk-authority-gates.md)). |
| **Platform mapping** | **GitHub mode:** design discussion may occur in issue comments or PRs; ADR artifacts committed to the repo. **Enterprise mode:** design review via enterprise review tooling; architecture board or tech-lead sign-off per change governance. |

### Phase 4 — Specification and work decomposition

| Field | Value |
|---|---|
| **Owner** | `spec-driven-development` (see [routing-table.md](routing-table.md)) |
| **Input** | Phase 3 output: approved architecture delta, decisions, and risk assessment (gate 1 passed). |
| **Output** | Packet group (g) partially: `SPEC.md` with acceptance criteria mapped to the change contract; `TASK-PLAN.md` covering every spec item and acceptance criterion. No task is unbounded or ownerless. |
| **Gate** | **Gate 3** — specification and task-plan completeness (see [stages.md](stages.md)). `SPEC.md` and `TASK-PLAN.md` must be complete and approved before the planning phase exits. |
| **Escalation** | Requirements are irreconcilably ambiguous after product-discovery engagement; or scope exceeds granted authority and requires re-negotiation. |
| **Platform mapping** | **GitHub mode:** spec artifacts committed to the working branch; acceptance criteria may reference issue comments. **Enterprise mode:** spec artifacts stored per project conventions; requirements traced to the ticket tracker. |

### Phase 5 — Pre-implementation test and verification planning

| Field | Value |
|---|---|
| **Owner** | `qa-methodology` (see [routing-table.md](routing-table.md)); QA-owned, independent from the implementer |
| **Input** | Phase 4 output: approved `SPEC.md` and `TASK-PLAN.md` (gate 3 passed). |
| **Output** | Packet group (g) completed: `VERIFICATION-PLAN.md` naming verification targets, test levels (unit / integration / end-to-end), regression coverage strategy, and the evidence artifacts that constitute a passing verification. |
| **Gate** | **Gate 2** — QA-owned test and verification plan (see [stages.md](stages.md)). No implementation work (code edits, commits, or branch work beyond the packet) may occur until this verdict is recorded. Post-hoc self-approval by the implementer is not permitted. No-new-tests path: when the change requires no new tests, that determination is documented with a reason. |
| **Escalation** | The verification target cannot be defined because the acceptance criteria are untestable; or the QA plan reveals an unresolved design risk that blocks test design. |
| **Platform mapping** | **GitHub mode:** verification plan committed to the working branch; CI configuration discovered per repository. **Enterprise mode:** verification plan reviewed via enterprise tooling; enterprise CI capabilities assessed. |

### Phase 6 — Domain-specific implementation

| Field | Value |
|---|---|
| **Owner** | Routed implementation specialists per [routing-table.md](routing-table.md) (e.g., `backend-engineering`, `frontend-engineering`, `cli-builder`, `data-engineering`); one lead per stage when several compose |
| **Input** | Phase 5 output: approved verification plan (gate 2 passed); `SPEC.md` and `TASK-PLAN.md` from phase 4. |
| **Output** | Implementation commits on the working branch; packet group (c) updated with the current head SHA; evidence ledger ([evidence-ledger.md](evidence-ledger.md)) appended with files changed, commands run, and observed outputs. |
| **Gate** | Implementation complete per `TASK-PLAN.md`; all tasks marked done; the working branch builds cleanly. |
| **Escalation** | Implementation reveals a design flaw requiring return to phase 3; or a hard stop from [risk-authority-gates.md](risk-authority-gates.md) is encountered (trust-boundary crossing without authority, irreversible migration without explicit directive). |
| **Platform mapping** | **GitHub mode:** commits pushed to a feature branch (fork-and-PR or branch-in-repo per repository conventions). **Enterprise mode:** commits pushed per enterprise branching policy; CI triggered by enterprise pipeline. |

### Phase 7 — Independent review and boundary verification

| Field | Value |
|---|---|
| **Owner** | Review specialists per dimension (see gate 4 in [stages.md](stages.md)): `programming-principles` (code quality), `software-architecture-analysis` (architecture), `secure-software-engineering` / `security-audit-methodology` (security), `web-accessibility` (accessibility), `technical-documentation` (docs). Boundary verification: `verification-methodology`. |
| **Input** | Phase 6 output: complete implementation at a known head SHA. |
| **Output** | `VERIFICATION.md` with layered verdicts (PASS/FAIL/BLOCKED/NOT-APPLICABLE) bound to the exact head SHA; independent review verdict (gate 4) with per-dimension coverage recorded; packet group (h) updated with gate 4 and gate 5 verdicts. For the lightweight path, the review is requested only after the candidate is frozen and one bounded reviewer or the required platform review is sufficient unless a risk trigger requires more. |
| **Gate** | **Gate 4** — independent review (distinct from spec-compliance checking; see [stages.md](stages.md)). **Gate 5** — boundary verification at the declared target. Both verdicts bind to the exact head SHA. A timed-out review is inconclusive and does not trigger repeated review rounds against a mutable or superseded candidate. |
| **Escalation** | Review reveals a security vulnerability requiring expert intervention; or the only available verification is weaker than the declared target and the gap is material (see [risk-authority-gates.md](risk-authority-gates.md)). |
| **Platform mapping** | **GitHub mode:** review via PR review comments; CI checks as boundary evidence. **Enterprise mode:** review via enterprise review tooling; named approver sign-off recorded; enterprise CI results as boundary evidence. |

### Phase 8 — Readiness, CI/review feedback loops, and exact-final-head re-verification

| Field | Value |
|---|---|
| **Owner** | neckbeard delivery step (core loop step 6); lifecycle mechanics per [lifecycle.md](lifecycle.md) |
| **Input** | Phase 7 output: review and verification verdicts (gates 4 and 5) at a known head SHA. |
| **Output** | Packet group (i) populated: review-submission (PR or equivalent) number, CI status, review status, **final verified head SHA**. The final verified head SHA must equal the actual head of the delivered change. A **material** post-review change (see materiality rule below) invalidates prior verdicts and requires re-entry through phase 7 (review and boundary verification) before readiness can be declared. After a **non-material** change, prior verdicts stand but the recorded head SHA is updated and the update is logged. CI and review feedback loops iterate until both pass at the final head. For lightweight test-hardening in a repository with expensive CI, local design, hermeticity, focused tests, targeted mutation, lint, compilation, and scope checks must pass before the first push; the goal is one stable candidate and one remote verification cycle. |
| **Gate** | **Readiness gate:** CI passes at the exact final head SHA; review is approved at the exact final head SHA; all gate verdicts in group (h) are bound to the final head SHA. This gate declares the change **ready for review submission or merge consideration** — it does **not** authorize merge or release. |
| **Escalation** | CI fails and the failure is not diagnosable from logs after two attempts; or review feedback is irreconcilable with the specification; or a material change after review cannot be re-verified within the granted authority. |
| **Platform mapping** | **GitHub mode:** PR opened with closing-keyword convention discovered per repository; CI monitored until green; review feedback addressed; final verdict bound to the exact head SHA. **Enterprise mode:** review submission via enterprise tooling; enterprise CI monitored; approver sign-off recorded; merge gated on enterprise approval workflow. |

### Phase 9 — Authorized post-merge release and closeout

| Field | Value |
|---|---|
| **Owner** | Release authority holder (explicit authorization required beyond merge authority; see [risk-authority-gates.md](risk-authority-gates.md) and [lifecycle.md](lifecycle.md)) |
| **Input** | Phase 8 output: readiness confirmed at the exact final head SHA; change merged (or equivalent accepted) into the protected target. Packet group (i) shows merge evidence. |
| **Output** | Packet group (i) completed: **terminal lifecycle state** (`merged`, `closed`, `blocked`, or `released`) recorded with evidence — merge commit SHA, release evidence (tag, artifact, deploy confirmation, post-release smoke check), or close reason — plus **rollback/follow-up triggers**: the conditions that would cause re-entry after closeout (e.g., a post-release regression requiring rollback, or an operational discovery); plus **lesson capture** per Stage 6 "Deliver and learn" ([stages.md](stages.md)): either the reusable lesson(s) and their durable destination (skill, memory, or project docs), or an explicit "no reusable lesson identified" determination — silent omission is prohibited. The packet transitions to a terminal state and is not re-opened; operational or post-release discoveries route to a **new** change request via phase 1 intake, never to the terminal packet. |
| **Gate** | **Release gate:** release activity (tagging, publishing, deploying) requires **explicit authorization distinct from merge authority**. Merge alone does not imply release authorization. Post-release verification evidence (smoke check, deploy confirmation) is recorded before the `released` terminal state is declared. |
| **Escalation** | Release authority is not granted; or post-release verification reveals a regression requiring rollback; or a change-freeze window blocks deployment (enterprise mode). |
| **Platform mapping** | **GitHub mode:** release via tag/publish per repository conventions; release authority is a separate grant from merge authority. **Enterprise mode:** release via enterprise pipeline (CAB approval, change-manager sign-off, change-freeze compliance); deploy confirmation recorded. |

---

## No-change-needed termination

Phases 1–2 may discover that **no change is warranted**: the issue is a phantom
(cannot be reproduced and no defect exists), the problem is already fixed, or the
request duplicates existing work. This is a legitimate terminal path.

**Procedure:**

1. The discovery evidence demonstrating no change is needed is recorded in packet
   group (d) with boundary labels and artifact pointers.
2. The packet lifecycle state transitions to **closed** (see
   [delivery-packet.md](delivery-packet.md), allowed transitions: intake/planning
   → closed).
3. The close reason and its evidence are recorded in packet group (i) terminal
   state fields.
4. **No PR or review submission is created.** No code is changed.

This outcome is distinct from **blocked** (a gate failure that stops an active
change) and from the lightweight path (which still delivers a change). It is an
evidence-backed result worth preserving in the record
(see [risk-authority-gates.md](risk-authority-gates.md): "no change needed"
outcomes are legitimate results).

---

## Delivery paths

Four named paths determine which phases are mandatory and which are conditional.
**The single source of truth for the path/phase matrices and their gate
enforcement rules is [stages.md](stages.md) (§ Delivery paths).** The summary
below must remain consistent with that source; when they diverge, stages.md
governs.

Path selection is recorded in packet group (b). Every skipped conditional phase
is recorded in packet group (e) with a concrete reason citing the path's skip
criterion — silent omission is prohibited
(see [delivery-packet.md](delivery-packet.md), skip transparency).

### Path overview

| Path | Character | Mandatory phases | Conditional phases |
|---|---|---|---|
| **Lightweight** | Narrow, low-risk (single-surface fix, test-hardening regression guard, docs-only, config tweak) | 1, 6, 7, 8, 9 | 2, 3, 4, 5 |
| **Full** | Standard feature work | All nine (1–9) | None |
| **Refactor** | Behavior-preserving structural change | 1, 2, 3, 6, 7, 8, 9 | 4, 5 |
| **High-risk** | Safety, security, compliance, or production-criticality | All nine (1–9); all five gates; escalation review at gates 1, 2, and 5 | None — no conditional skips permitted |

The paths **differ in phase sets**: the lightweight path mandates five phases and
drops four; the refactor path mandates seven and conditionally skips two; the
full and high-risk paths mandate all nine but differ in gate enforcement
(high-risk adds escalation review at gate boundaries and prohibits all
conditional skips).

### Lightweight path — dropped phases and skip criteria

This path includes narrow code changes, test-hardening regression guards, docs-only
changes, and config tweaks. For the test-hardening subtype, use the dedicated
contract in [lightweight-test-hardening.md](lightweight-test-hardening.md).

| Dropped phase | Skip criterion |
|---|---|
| 2 — Discovery and reproduction | The change surface is a single function or module and the current behavior is already understood from the change request; no reproduction is needed. For the test-hardening subtype, record the clean behavior and named mutation or controlled weakening instead of requiring a live production repro. |
| 3 — Architecture/design delta | No module boundary, service dependency, cross-component contract, or system-level structure is affected (per the `software-architecture-analysis` skip rule in the [routing table](routing-table.md)). |
| 4 — Specification and decomposition | The change is fully described by the change contract with testable acceptance criteria; no separate `SPEC.md` or phased decomposition is needed (per the `spec-driven-development` skip rule). |
| 5 — Test and verification planning | No `VERIFICATION-PLAN.md` is required beyond the implementer's own focused tests; the change introduces no new verification surface (per the `qa-methodology` skip rule). |

Gates 1, 3, and 2 are conditional on this path (skipped with their phases);
gates 4 and 5 remain mandatory. See [stages.md](stages.md) for the full matrix.
For test-hardening, gate 5 uses clean-baseline pass plus named-mutant failure;
the ordinary production-bug requirement that a new test fail on clean `main`
does not apply. Gate 4 is one bounded final review after the candidate is frozen
unless a risk trigger or repository policy requires more.

### Refactor path — conditional phases

| Conditional phase | Skip criterion |
|---|---|
| 4 — Specification and decomposition | The refactor is fully characterized by the architecture delta and characterization-test plan; no separate `SPEC.md` is needed because no behavior changes. |
| 5 — Test and verification planning | Existing characterization tests cover the affected surface; the test strategy is recorded as "existing suite, no additions." |

Gates 1, 4, and 5 are always mandatory on this path. Gates 3 and 2 are
conditional (skipped only with their phases, with recorded reasons).
Behavior-preservation evidence (characterization tests passing before and after)
is the gate 5 criterion. See [stages.md](stages.md) for the full matrix.

---

## Conditional specialist routing

Each phase that involves specialist work resolves its routing via the
[routing table](routing-table.md). The journey does **not** unconditionally load
every specialist at every phase. Instead:

1. Evaluate each routing row's applicability signal against the change surface.
2. Select the applicable specialists; record the per-stage lead when several
   compose (packet group (e)).
3. For every skipped specialist, record the skip with a reason citing the row's
   skip rule — e.g., "frontend-engineering skipped: no client-side application
   code modified."
4. The `opensource-contributions` skill is loaded **only** for public/OSS
   repositories; for private or enterprise repositories it is skipped with the
   reason "non-public repository."
5. When **no** applicability signal triggers, work proceeds on the neckbeard
   spine and the packet records "no specialist selected — no applicability signal
   triggered."

---

## Materiality and the re-review trigger

A **material** post-review change — one introduced in response to review feedback
after phase 7 has passed — invalidates prior verification and review verdicts and
requires re-entry through phase 7 (independent review and boundary verification)
before the readiness gate (phase 8) can be satisfied.

The canonical material/non-material definition is owned by
[stages.md](stages.md) (§ Gate 5 — Material change definition) and is the single
source of truth referenced by this journey, by
[delivery-packet.md](delivery-packet.md), and by [lifecycle.md](lifecycle.md):

- **Material** (invalidates prior verdicts, requires re-verification): a change
  that alters logic, adds or removes functionality, modifies the verification
  surface, changes test assertions, or alters data flow across a trust boundary.
- **Non-material** (prior verdicts stand; SHA binding updated): typo fixes,
  formatting-only changes, comment-only edits, pure renames without behavior
  change, docs-only changes, and rebases that produce no semantic diff.

After a material change, affected gates re-run and new verdicts are bound to the
new head SHA. After a non-material change, the recorded head SHA is updated and
the update is logged (old SHA → new SHA, materiality: non-material); prior
verdicts are not re-run. The final verified head SHA in packet group (i) must
always equal the actual final head of the delivered change.

---

## Authority boundary: readiness versus release

Phase 8 and phase 9 enforce a **hard authority boundary**:

- **Phase 8** ends with a readiness gate that declares the change ready for
  review submission or merge consideration. It does **not** authorize merge or
  release. "Ready for review" is not "ready to release."
- **Phase 9** begins only after merge (or equivalent acceptance) and requires
  **separate, explicit authorization** for release activity (tagging, publishing,
  deploying). Merge authority does not imply release authority
  (see [risk-authority-gates.md](risk-authority-gates.md)).

A change that passes phase 8 does not automatically enter phase 9. The two
authorities are never conflated.

---

## Phase continuity

The output of each phase is a required input to the next. Outputs flow through
named delivery-packet field groups:

| Phase | Produces (packet group) | Consumed by |
|---|---|---|
| 1 — Intake | (a) provenance, (b) authority/mode/path | Phase 2 (input: change contract) |
| 2 — Discovery | (d) baseline evidence, affected surfaces | Phase 3 (input: current-state evidence) |
| 3 — Design delta | (f) architecture delta, decisions, risks | Phase 4 (input: approved design, gate 1) |
| 4 — Specification | (g) `SPEC.md`, `TASK-PLAN.md` | Phase 5 (input: approved spec, gate 3) |
| 5 — Verification planning | (g) `VERIFICATION-PLAN.md` | Phase 6 (input: approved plan, gate 2) |
| 6 — Implementation | Commits, (c) head SHA updated | Phase 7 (input: complete implementation) |
| 7 — Review + verification | (h) gate 4 + gate 5 verdicts, `VERIFICATION.md` | Phase 8 (input: verdicts at known SHA) |
| 8 — Readiness | (i) PR/CI/review/final verified head SHA | Phase 9 (input: merged change, readiness evidence) |
| 9 — Release + closeout | (i) terminal state + evidence + rollback/follow-up triggers + lesson capture (or "no reusable lesson identified") | Record complete (terminal; triggers and lessons are recorded in the terminal record, not consumed — re-entry starts a new packet via phase 1 intake, carrying the lesson reference) |

Every field group written by a phase is consumed by a named later phase or
recorded as terminal evidence. No output is orphaned.

---

## Gate summary

Five gates block phase progression. Gate numbering groups gates by area and does
not imply chronological order. The execution sequence is:

> gate 1 (phase 3→4) → gate 3 (phase 4 exit) → gate 2 (phase 5→6) → gate 4
> (phase 7) → gate 5 (phase 7→8)

Full definitions, verdict semantics (pass/conditional/blocked), and per-gate
evidence requirements are in [stages.md](stages.md) (§ Change-request gates).
Every gate verdict is recorded in packet group (h) with the gate identifier,
verdict, evidence references, and the exact head SHA.

---

## Escalation and stop rules

Phase escalation conditions are consistent with the stop rules in
[risk-authority-gates.md](risk-authority-gates.md). The hard stops apply at every
phase boundary:

- Never delete data, branches, releases, or infrastructure without an explicit
  human directive.
- Never escalate privileges (credentials, tokens, IAM, secrets).
- Never force-push, rewrite history, or overwrite a protected ref.
- Never deploy or merge when authority was not granted for that class.
- Stop when two materially different approaches have failed.
- Stop when the only available verification is weaker than the declared target
  and the gap is material.
- Stop when an instruction conflicts with a hard constraint.

A gate verdict of **blocked** stops the run and transitions the packet to the
**blocked** lifecycle state; the run does not continue without new authority
(see [delivery-packet.md](delivery-packet.md), blocked-state semantics).
Persistence does not upgrade authority.
