# Position Assessment — Mid-Flight Engagement Entry Mode

Some engagements begin mid-flight: the agent is asked to continue software
delivery work that started elsewhere — a half-implemented branch, an adopted
specification, a change request another contributor began — and no delivery
packet exists because the earlier work did not run inside this bundle. The
nine-phase journey ([journey.md](journey.md)) describes the canonical forward
path from intake; it does not describe how to enter that path honestly when the
first six phases may already be partly done.

This reference defines that entry mode. It is loaded by [../SKILL.md](../SKILL.md)
only for mid-flight engagement. It is **not** loaded when a fresh change request
starts the journey at phase 1, and **not** loaded when the run's own delivery
packet exists — packet resumability
([delivery-packet.md](delivery-packet.md)) governs that case, and the packet is
authoritative there.

The procedure answers three questions before any execution continues:

1. What step is the work actually on?
2. Which gates have evidence behind them, and which remain?
3. What is the next justified action?

## The core rule: artifacts, not narratives

Position is established from observable artifacts — files, commits, CI runs,
review states — scored against the exit conditions the phases define. It is
never established from summaries, however confident. "The spec was approved"
is not a satisfied gate; an approved `SPEC.md` artifact with a recorded gate
verdict is. A claim with no inspectable artifact behind it becomes a recorded
**unverified assumption**, never a satisfied gate.

This is the same doctrine the rest of the bundle applies to verification:
assertions are not evidence. Assessment inherits it.

## Procedure

### Step 1 — Trigger check

Enter this mode only when all three hold:

| Condition | How to check |
|---|---|
| The request is to continue existing delivery work | The request references ongoing work (a branch, spec, partial implementation) rather than a fresh change |
| No delivery packet exists for that work | No packet artifact accompanies the work; the prior run, if any, was outside this bundle |
| The work is non-trivial enough to warrant the journey | Same threshold [../SKILL.md](../SKILL.md) applies before loading the journey |

If a delivery packet exists, use [delivery-packet.md](delivery-packet.md)
resumability instead. The empty-inventory case ("no artifacts found") can only
be determined after running step 2's inventory; when it holds, assessment
still completes normally — deliver a position report stating phase 1 and
perform the step-5 bootstrap, then let the normal journey take over. An empty
inventory is a finding, not a failure, and it does not skip the report or the
packet.

### Step 2 — Inventory the observable artifacts

Search the working repository and tracker for the artifacts the phases would
have produced. When artifacts live in a tracker, identify which tracking system
that is during this pass, per
[tracker-discovery.md](tracker-discovery.md), so the intake field exists by
bootstrap time.

| Observable artifact | Produced by | Typical locations |
|---|---|---|
| Change contract (problem, constraints, authority) | Phase 1 | Issue/ticket body, PR description, [../templates/change-contract.md](../templates/change-contract.md) instance |
| Repository conventions captured | Phase 1 | Evidence that `CONTRIBUTING.md` / `AGENTS.md` were consulted |
| Baseline and reproduction evidence | Phase 2 | Repro steps in the issue, failing-test transcripts, benchmark notes |
| Architecture delta, ADR, C4 diagrams, or a documented no-delta determination | Phase 3 | `docs/adr/`, design docs, decision-record instances |
| `SPEC.md`, `TASK-PLAN.md` | Phase 4 | Repository root or working branch |
| `VERIFICATION-PLAN.md` | Phase 5 | Working branch |
| Implementation commits on a working branch | Phase 6 | `git log <base>..HEAD` |
| `VERIFICATION.md`, independent review verdicts | Phase 7 | Working branch, PR review states |
| Green CI and approved review at a known head SHA | Phase 8 | CI checks, review approvals bound to a specific SHA |
| Merge commit, release tag, deploy confirmation | Phase 9 | Protected-target history, tags, deploy logs |

Inventory reads are read-only discovery; they need no confirmation. Record
where each artifact was found (path, SHA, URL) — pointers become the evidence
references in the report.

**Re-select the delivery path here, before scoring.** Run the path-selection
rule ([../SKILL.md](../SKILL.md) § Path selection) against the affected surface
and risk observed in the inventory; do not inherit a path assumption from the
prior work. The selected path determines which phases are mandatory to score.

### Step 3 — Score against phase exit conditions

Compare each inventoried artifact with the exit condition and gate definition
of its phase ([journey.md](journey.md); gate semantics in
[stages.md](stages.md)). Assign exactly one verdict per phase:

| Verdict | Meaning |
|---|---|
| **Satisfied** | The artifact exists and meets the phase exit condition. Record the evidence pointer. |
| **Partial** | The artifact exists but is incomplete or unapproved. Name exactly what remains. |
| **Absent** | No artifact found. The gate is not passed. |
| **Contradicted** | An artifact exists but observable evidence conflicts with it (for example, readiness claimed while CI is red at the recorded head). Contradiction blocks progression until resolved. |

Scoring constraints:

- **Authenticate before crediting.** Artifacts authored by the same party that
  produced the working branch — committed specs, verification and review
  files, "no delta" determinations, claimed approvals or CI outcomes written
  into the branch — are **attacker-forgeable** in exactly the adopted-branch
  scenarios this mode exists for. Approval- and authority-carrying evidence
  (the approved architecture delta at gate 1, the QA-owned verification plan
  at gate 2, the approved specification at gate 3, review verdicts and
  boundary verification at gates 4–5, readiness) is scored `satisfied` only
  when corroborated from an independent source: an approval or review recorded
  on the remote platform by a real identity distinct from the branch author,
  or CI results queried from the remote and bound to the exact head SHA.
  Self-authored determinations (a "no architecture delta" note, a
  self-approved spec) are never credited on their face; assessment may
  re-derive the underlying judgment against the gate's own criterion and score
  accordingly, recording the re-derivation in the evidence ledger. Evidence
  that can be neither corroborated nor re-derived is scored at best `partial`
  with the uncorroborated claim recorded — never `satisfied`. The same
  weighting doctrine tracker-discovery applies to repository signals applies
  here.
- Score the delivery path selected in step 2; conditional phases are scored
  only if their artifacts exist (an absent conditional phase with a legitimate
  skip reason is recorded as such, not penalized).
- Verified-complete work is **not** re-executed, mirroring packet-resume
  semantics. Assessment establishes position; it does not redo accepted work.
- Never upgrade a verdict to fill a gap. A missing gate verdict is `absent`,
  even when the underlying work looks done.
- Two contradictory sources (artifact says approved, tracker says changes
  requested) yield `contradicted`, and the conflict itself is reported.

### Step 4 — Emit the position report

Produce the report and deliver it to the requester **before** continuing
execution. Format:

```
current phase:        <n>-<phase-name>
selected path:        <lightweight|full|refactor|high-risk>
assessment head SHA:  <git rev-parse HEAD at assessment time>
satisfied gates:      <gate> @ <evidence pointer>; ...
partial:              <gate/artifact> — <what remains>
absent:               <gates with no evidence>
contradicted:         <gate/artifact> — <conflicting evidence>
remaining checklist:  [ ] <next gate/action>; [ ] ...
unverified assumptions: <claims accepted provisionally, with owner of the proof>
recommended next action: <single bounded step>
```

The remaining checklist is the contract for continuation: work proceeds
against it in journey order, respecting the five-gate sequence and every stop
rule in [risk-authority-gates.md](risk-authority-gates.md).

### Step 5 — Bootstrap the packet

Create a fresh delivery packet so subsequent operation has normal resumability.
Group (c) initialization derives its fields from the report: the current phase
comes from the report's `current phase` field, and the **current gate** is the
first gate in the remaining checklist (or "none — awaiting next phase entry"
if the checklist starts at a phase rather than a gate).

- Group (a) provenance records: engaged mid-flight, artifacts assessed, with
  the inventory pointers, and the tracking system identified during the
  inventory pass per [tracker-discovery.md](tracker-discovery.md), with its
  evidence basis — satisfying the intake-gate field this bootstrap must carry.
- Group (b) records the delivery path selected in step 2 (path selection per
  [../SKILL.md](../SKILL.md) § Path selection was re-run during assessment; no
  path assumption was inherited from the prior work).
- Group (c) records: current phase and current gate as derived above; the
  **last passed gate verdict head SHA** taken from the highest satisfied gate's
  own evidence SHA (recorded as `none` when no gate is satisfied — never the
  assessment-time HEAD, which would imply a passed verdict that group (h)
  does not contain); and the **current lifecycle state**, mapped from the
  assessed position using the packet's enumerated vocabulary (`intake` for an
  empty inventory or a position at phase 1; `planning` for positions in phases
  2–5; `implementation` for phase 6; `in-review` for phase 7; `ready` for a
  position at phase 8; `blocked` if assessment found a contradicted gate that
  stops progression).
- Unverified assumptions go to the evidence ledger
  ([evidence-ledger.md](evidence-ledger.md)), not into gate fields.

Do **not** retroactively mark gates as passed in group (h) without artifacts.
Gates with genuine evidence pointers may be recorded as passed with those
pointers; everything else remains open.

## Completion and exit conditions

Assessment is complete when the position report has been delivered and the
packet bootstrapped. The mode then ends: execution continues under the normal
journey and core loop. If the inventory is empty, completion is the honest
statement "no artifacts found — starting at phase 1" plus the same bootstrap.

## Non-goals

- This is not a quality audit of the existing work. It establishes position;
  phase 7 review still judges quality.
- It does not bypass gates. Only gates with real evidence may be marked
  satisfied; the rest must actually run.
- It does not replace packet resumability. Where a packet exists, the packet
  wins.
- It does not guess at intent behind ambiguous prior work. When the change
  contract cannot be reconstructed from artifacts, that is a phase-1 gap, and
  intake happens properly.
