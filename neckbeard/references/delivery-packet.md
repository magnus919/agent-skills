# Delivery Packet

The delivery packet is the **durable cross-phase handoff** for a change-request
run. It is the coordination contract that lets one phase hand verified state to
the next — and lets an agent resume after a context boundary or a review round
without guessing what was already decided, verified, or gated.

## Purpose: a handoff, not a duplicate

> The delivery packet carries **pointers, summaries, and verdicts** — not the
> specialist content itself. It is a coordination artifact, **not** a
> replacement for or duplicate of the artifacts it references (change contract,
> architecture delta / ADR / C4 output, `SPEC.md`, QA verification plan,
> `TASK-PLAN.md`, `VERIFICATION.md`, evidence ledger). Each specialist artifact
> is owned by exactly one phase (see the ownership map below); the packet points
> to it and records its verdict, it does not absorb it.

When a field and a specialist artifact would say the same thing, the packet holds
a path plus a one-line summary and the artifact holds the detail. If they ever
disagree, the specialist artifact is authoritative for its content and the packet
is authoritative for the cross-phase verdict and head-SHA binding.

Fillable template: [../templates/delivery-packet.md](../templates/delivery-packet.md).

## The nine field groups

Every packet records exactly these nine groups, labeled (a)–(i). None is merged
into another or left to implication.

| Group | Name | Fields |
|---|---|---|
| **(a)** | **Change-request provenance** | Change-request URL or number; source type (issue / ticket / email / verbal); repository; base ref; issue/comment snapshot (request text, comments, and linked work captured at intake); tracking system identified at intake per [tracker-discovery.md](tracker-discovery.md), with its evidence basis (detected from the request's own reference, repository-detected, or requester-confirmed); head SHA at intake. |
| **(b)** | **Granted authority + workflow mode/path** | Authority class granted (Explore / Modify / Publish / Deploy / Merge — see [risk-authority-gates.md](risk-authority-gates.md)); selected workflow mode (GitHub reference mode or enterprise mode); selected path (lightweight / full / refactor / high-risk). |
| **(c)** | **Resumable phase/gate state + current head SHA** | Current phase name; current gate name; the head SHA at which the last successful gate verdict was recorded; the current lifecycle state (see below). |
| **(d)** | **Problem / baseline evidence / scope / non-goals / affected surfaces** | User-visible problem; baseline (pre-change) evidence with boundary labels; in-scope work; explicit non-goals; affected surfaces (paths, contracts, boundaries). |
| **(e)** | **Routing: selected skills + explicitly skipped skills with reasons** | Specialist skills selected (with per-stage lead when several compose); every skipped phase and every skipped skill with a concrete reason; the no-specialist fallback decision when no applicability signal triggers. |
| **(f)** | **Design: architecture delta / decisions / risks / compatibility / migration / rollback** | Architecture delta (or a documented "no delta" determination); decisions and rejected alternatives; risks; compatibility analysis; migration strategy; rollback plan. |
| **(g)** | **Plan: spec / acceptance criteria / test strategy / task plan / verification report paths** | Path to `SPEC.md`; acceptance criteria mapping; test strategy; path to `TASK-PLAN.md`; path to the QA verification plan; verification report paths. |
| **(h)** | **Gates: verdicts / assumptions / rejected alternatives / unresolved boundaries / evidence pointers** | A verdict per gate (identifier, pass/conditional/blocked, evidence, head SHA); assumptions; rejected alternatives; unresolved boundaries; pointers to evidence artifacts. |
| **(i)** | **Lifecycle: PR number / CI status / review status / final verified head SHA / release status** | PR (or review-submission) number; CI status; review status; the **final verified head SHA**; release status; terminal lifecycle state and its evidence; **rollback/follow-up triggers** recorded at closeout (what would cause re-entry). |

Group (e) and group (h) carry the fields that make skip transparency and gate
discipline auditable; see their rules below.

## Field-group write ownership per phase

Each field group is written by one owning phase (or an explicit continuous span)
so no group is overwritten by competing writers and none is orphaned. Later
phases **read** every earlier group and **append** only to the groups they own.

| Group | Written by |
|---|---|
| (a) Provenance | Phase 1 — intake and provenance |
| (b) Authority + mode/path | Phase 1 — intake and provenance |
| (c) Resumable phase/gate state + head SHA | Updated by every phase at its gate; owned as a continuous field across phases 1–9 |
| (d) Problem / baseline / scope / non-goals / surfaces | Phases 1–2 — phase 1 frames the problem, scope, non-goals, and affected surfaces; phase 2 (discovery and reproduction) completes the baseline evidence |
| (e) Routing: selected + skipped skills | Phase 1 selects the path; each phase records its own routing/skip decisions as it runs (continuous, appended per phase) |
| (f) Design | Phase 3 — architecture/design delta and risk assessment |
| (g) Plan | Phases 4–5 — specification and decomposition (4) and pre-implementation test/verification planning (5) |
| (h) Gates | Each gate's owning phase writes its own verdict (see the gate→phase mapping in the change-request journey, `references/journey.md`); assumptions and rejected alternatives are appended by the phase that produced them; evidence pointers updated throughout |
| (i) Lifecycle (PR/CI/review/final SHA/release) | Phases 8–9 — readiness and re-verification (8) and authorized release and closeout (9) |

Evidence pointers (in group (h)) and the resumable state (group (c)) are the two
continuously-maintained fields; everything else has a single owning phase.

## Artifact ownership map

Every cross-phase artifact has exactly one owning phase — or, for the evidence
ledger, an explicit continuous span. The map names who writes it, who reviews it
(or which gate reviews it), and its canonical repo-relative path, so
responsibility never needs to be inferred. The packet references these; it does
not contain them.

| Artifact | Owning phase | Writer | Reviewer / gate | Canonical path |
|---|---|---|---|---|
| Change contract | Phase 1 — intake and provenance | neckbeard framing step | Reviewed at the phase 1 intake gate | `CHANGE-CONTRACT.md` (from [../templates/change-contract.md](../templates/change-contract.md)) |
| Architecture delta / ADR / C4 output | Phase 3 — architecture/design delta and risk | `software-architecture-analysis`, `adr-authoring`, `c4-diagramming` as applicable | Approved at **gate 1** (architecture/design delta) | `ARCHITECTURE-DELTA.md` and any ADR/C4 files it links |
| SDD `SPEC.md` | Phase 4 — specification and work decomposition | `spec-driven-development` | Approved at **gate 3** (spec + task-plan completeness) | `SPEC.md` |
| QA verification plan | Phase 5 — pre-implementation test and verification planning | `qa-methodology` | Approved at **gate 2** (QA-owned test and verification plan) | `VERIFICATION-PLAN.md` (from [../templates/verification-plan.md](../templates/verification-plan.md)) |
| `TASK-PLAN.md` | Phase 4 — specification and work decomposition | `spec-driven-development` | Approved at **gate 3** (spec + task-plan completeness) | `TASK-PLAN.md` |
| `VERIFICATION.md` | Phase 7 — independent review and boundary verification | `verification-methodology` | Reviewed at **gate 5** (boundary verification) | `VERIFICATION.md` |
| Evidence ledger | Phases 1–9 — continuous span | Every phase appends | Audited at every gate and at closeout | `EVIDENCE-LEDGER.md` (from [../templates/evidence-ledger.md](../templates/evidence-ledger.md)) |

Gate numbers group gates by area; their chronological execution order in the
journey is gate 1 → gate 3 → gate 2 → gate 4 → gate 5. Gate definitions live in
the stages reference (`references/stages.md`); the packet records their verdicts.

## Lifecycle states

A packet occupies one lifecycle state at a time. States:

| State | Meaning / entry condition |
|---|---|
| **intake** | Change request captured; provenance and authority recorded; not yet planned. |
| **planning** | Discovery, design, specification, and verification planning are in progress. |
| **implementation** | Domain implementation is in progress under an approved plan. |
| **in-review** | A review submission exists; CI and independent review feedback loops are active. |
| **ready** | Readiness gate passed at the exact final head SHA; ready for merge/approval, not yet merged. |
| **merged** | Change merged (or equivalent accepted) into the protected target. |
| **closed** | Run terminated without code (e.g., discovery showed no change is warranted, duplicate, already fixed) — recorded with evidence. |
| **blocked** | A gate verdict of blocked stopped the run; blocker evidence and escalation recorded. |
| **released** | Authorized post-merge release activity completed. |

### Allowed transitions

Only these transitions are valid; any other transition is a protocol error.

```
intake → planning → implementation → in-review → ready → merged → released
   │         │            │             │          │        │
   └─────────┴────────────┴─────────────┴──────────┴────────┴──→ blocked
intake/planning → closed
```

- **Forward path:** intake → planning → implementation → in-review → ready →
  merged → released.
- **blocked** is reachable from any non-terminal active state (intake, planning,
  implementation, in-review, ready) when a gate verdict is blocked.
- **closed** is reachable from intake or planning when discovery shows no change
  is warranted (a legitimate no-code terminal path, distinct from blocked).
- **released** is reachable **only** from merged. A packet that is not merged
  cannot become released.

### Terminal semantics

**merged**, **closed**, **blocked**, and **released** are terminal: a packet in a
terminal state is **not re-opened by a later phase**. New work starts a new packet
(a new change request), it does not resurrect a terminal one. In particular, a
**ready** packet that fails a gate or CI returns to **in-review** (not terminal);
only a blocked verdict makes it **blocked**.

Rollback/follow-up triggers are recorded **in** the terminal record at closeout
(see group (i)); they document what would cause re-entry but do not re-open the
packet. When a recorded trigger fires, the follow-up work starts as a new change
request through phase 1 intake, carrying the trigger reference from the closed
packet's record.

## Blocked-state semantics

Any gate verdict of **blocked** transitions the packet to the **blocked**
lifecycle state and requires all of the following to be recorded (none optional):

- the **failing gate identifier** (which gate blocked);
- the **phase** at which it occurred;
- the **blocking evidence** (what was observed that failed the gate);
- the **escalation outcome** per [risk-authority-gates.md](risk-authority-gates.md)
  (the decision or authority needed to proceed, and any safe partial result).

> A resuming agent **must not** continue from a blocked packet without new
> authority or instructions. A blocked verdict cannot coexist with a non-blocked
> packet state: if a gate is blocked, the packet is blocked.

A blocked verdict may instead resolve to a **conditional** verdict (recorded
conditions tracked and closed before the next gate) or a **pass**; only a blocked
verdict drives the blocked state.

## Resumability rules

The packet exists so a run can stop and resume without re-doing verified work.

1. **Recorded resumable state.** Group (c) always holds the current phase name,
   the current gate name, and the head SHA at which the last successful gate
   verdict was recorded.
2. **Passed gates are not re-executed.** A phase whose gate is recorded as
   **passed** must not be re-executed or re-verified **unless the head SHA has
   changed materially** since that verdict was recorded.
3. **Resume by reading the packet.** On resume, an agent reads group (c) to find
   where to continue and reads group (h) to see which gates already passed — it
   does not re-derive this from scratch.

### Changed-head procedure

When the recorded head SHA (from the last passed gate) differs from the actual
current head, the resuming agent runs this procedure before continuing:

1. **Assess materiality** against the canonical material/non-material definition
   owned by the change-request journey and lifecycle/stages references
   (`references/journey.md`, `references/lifecycle.md`, `references/stages.md`).
   Do not redefine "material" here; those references are the single source of
   truth.
2. **If the change is material** (e.g., it alters logic, adds or removes
   functionality, or changes the verification surface): every verdict bound to
   the stale SHA is **invalid**. Re-run the affected gates and re-verify, binding
   the new verdicts to the new head SHA.
3. **If the change is non-material** (e.g., a rebase, whitespace- or comment-only
   edit, docs-only change, or pure rename without behavior change): prior
   verdicts **stand**, but the recorded head SHA in group (c) is updated to the
   current SHA.
4. **Record the SHA update.** The SHA change itself is recorded in the packet
   (old SHA → new SHA, with the materiality determination), whether or not
   re-verification was required. Never silently carry a stale SHA.

### Concrete example: resuming after a context boundary

A run stopped overnight after independent review. The packet's resumable state
(group c) reads:

```
current phase:  phase-7-independent-review
current gate:   gate-4-independent-review
last passed gate verdict: passed @ head SHA 9f2c1ab
lifecycle state: in-review
```

The resuming agent reads this and knows: phases 1–6 and gate 1, gate 3, gate 2
are recorded as passed in group (h) and are **not** re-executed; the run resumes
at phase 7, completing gate 4 (independent review) and then gate 5 (boundary
verification). It then compares the recorded SHA `9f2c1ab` to the actual head:

- If the head is still `9f2c1ab`, it continues directly.
- If the head moved to `7b40de2` because a reviewer's typo fix landed
  (non-material), it updates group (c) to `7b40de2`, records the SHA change, and
  continues without re-running the passed gates.
- If the head moved to `7b40de2` because review feedback changed logic
  (material), the verdicts bound to `9f2c1ab` are invalid; it re-enters review
  and verification and rebinds the new verdicts to `7b40de2`.

## Exact-head binding

> Every gate verdict, verification report, and review outcome recorded in the
> packet **must include the exact commit SHA** to which it applies. This is a
> mandatory field on every verdict, not optional metadata.

A material post-verdict change to the head SHA invalidates any prior verdict not
bound to the new SHA; the packet then records the new head alongside the
re-verification evidence (see the changed-head procedure). The final verdict in
group (i) — the **final verified head SHA** — must equal the actual final head of
the delivered change. A final verdict bound to a stale SHA does not satisfy the
readiness or boundary-verification gates.

## Baseline vs post-change evidence

The packet keeps **baseline (pre-change) evidence** distinct from **post-change
verification evidence**, so a reviewer can always tell what was true before the
change versus after it.

- **Baseline evidence** is captured in group (d) as phase 2 output (current-state
  discovery, and reproduction output for a bug). It is labeled `baseline`.
- **Post-change verification evidence** is captured in groups (g) and (h) as the
  verification verdicts produced after implementation. It is labeled
  `post-change`.

Every verification verdict and every evidence entry carries **both** labels:

- an **evidence stage** label: `baseline` or `post-change`; and
- a **boundary** label naming the boundary actually exercised: `component`,
  `integration`, `end-to-end`, or `production` (per the boundary rule in
  [evidence-ledger.md](evidence-ledger.md)).

A completed packet lets a reviewer separate baseline from post-change evidence
and see which boundary each verdict covered. A verdict that omits either label is
incomplete.

## Skip transparency

> Every skipped phase and every skipped specialist skill is recorded in group (e)
> with a **concrete reason**. Silent omission is prohibited.

A skip reason must let a reviewer see why the phase or skill was not applied —
for example, "lightweight path: architecture delta conditional, skipped because
the change is a single-function bug fix," or "frontend-engineering skipped: the
change touches the backend API only." When **no** routing signal triggers, the
packet records "no specialist selected — no applicability signal triggered," and
work proceeds on the neckbeard spine; this is neither a silent omission nor a
fabricated reason. The stages reference (`references/stages.md`) and routing table
(`references/routing-table.md`) define the signals and skip rules cited here.

## Portability

> The delivery packet is portable: it assumes **no private infrastructure** and
> **no particular agent runtime or harness**.

Every field value is expressible as plain text, a repository-relative file path,
or a public URL. No field requires a specific vendor's platform, an internal
service endpoint, or proprietary tooling to populate or read. Platform-specific
mechanics (for example, GitHub `gh` commands or an enterprise ticket tracker)
live in the lifecycle reference (`references/lifecycle.md`), not in the packet's
field definitions — the packet records the outcome (a PR number, a CI status, a
review status) in a platform-neutral way.
