# Delivery Packet

> Fill one packet per change-request run. Each section mirrors a field group from
> [../references/delivery-packet.md](../references/delivery-packet.md). Replace
> every `_[fill: ...]_` marker with your value. The packet is a coordination
> handoff — record pointers, summaries, and verdicts, not specialist content.

## (a) Change-request provenance

<!-- Written at intake (phase 1). Identify the change request this work responds to. -->

- **Change-request URL or number:** _[fill: URL or tracker number, e.g. `https://github.com/org/repo/issues/42` or `JIRA-123`]_
- **Source type:** _[fill: issue / ticket / email / verbal]_
- **Repository:** _[fill: repo path or URL, e.g. `https://github.com/org/repo`]_
- **Base ref:** _[fill: branch or ref the change is based on, e.g. `main`]_
- **Issue/comment snapshot:** _[fill: request text, comments, and linked work captured at intake — paste inline or link to a snapshot file]_
- **Tracking system:** _[fill: system identified per ../references/tracker-discovery.md, e.g. `Linear (requester-confirmed)` / `GitHub Issues (detected: issue URL in request)`]_
- **Head SHA at intake:** _[fill: `git rev-parse HEAD` at intake, e.g. `a1b2c3d`]_

## (b) Granted authority + workflow mode/path

<!-- Written at intake (phase 1). See [../references/risk-authority-gates.md](../references/risk-authority-gates.md) for authority classes. -->

- **Authority class:** _[fill: Explore / Modify / Publish / Deploy / Merge — if unclear, write "explore (assumed)" and flag that confirmation is needed]_
- **Workflow mode:** _[fill: GitHub reference mode / enterprise mode]_
- **Selected path:** _[fill: lightweight / full / refactor / high-risk]_

## (c) Resumable phase/gate state + current head SHA

<!-- Updated by every phase at its gate. On resume, read this section first.
     Do not re-execute phases whose gates are recorded as passed unless the
     head SHA has changed materially (see the changed-head procedure in
     ../references/delivery-packet.md). -->

- **Current phase:** _[fill: phase name, e.g. `phase-7-independent-review`]_
- **Current gate:** _[fill: gate name, e.g. `gate-4-independent-review`]_
- **Last passed gate verdict head SHA:** _[fill: exact SHA at which the last gate passed, e.g. `9f2c1ab`]_
- **Current lifecycle state:** _[fill: intake / planning / implementation / in-review / ready / merged / closed / blocked / released]_

**Example (populated after a context boundary):**

```text
Current phase:                     phase-7-independent-review
Current gate:                      gate-4-independent-review
Last passed gate verdict head SHA: 9f2c1ab
Current lifecycle state:           in-review
```

A resuming agent reads: phases 1–6 and gates 1, 3, 2 are recorded as passed in
section (h) and are not re-executed. Resume at phase 7, completing gate 4 then
gate 5. Compare the recorded SHA `9f2c1ab` to the actual head; if they differ,
run the changed-head procedure in
[../references/delivery-packet.md](../references/delivery-packet.md) before
continuing.

## (d) Problem / baseline evidence / scope / non-goals / affected surfaces

<!-- Phase 1 frames the problem, scope, non-goals, and affected surfaces;
     phase 2 (discovery and reproduction) completes the baseline evidence.
     Label every evidence entry as baseline or post-change and name the
     boundary exercised. -->

- **User-visible problem:** _[fill: one or two sentences — what is wrong or missing from the user's point of view]_
- **Baseline (pre-change) evidence:** _[fill: reproduction output, current-state observations — label boundary: component / integration / end-to-end / production; label stage: baseline]_
- **In-scope work:** _[fill: what this change will do]_
- **Non-goals:** _[fill: what this change will explicitly NOT do]_
- **Affected surfaces:** _[fill: paths, contracts, boundaries touched]_

## (e) Routing: selected skills + explicitly skipped skills with reasons

<!-- Phase 1 selects the path; each phase appends its routing decisions as it
     runs. Every skipped phase and every skipped skill must carry a concrete
     reason — silent omission is prohibited. See
     [../references/routing-table.md](../references/routing-table.md) for
     applicability signals and skip rules. -->

- **Selected skills:** _[fill: skill name + per-stage lead when several compose, e.g. "backend-engineering (lead: implementation), api-design-and-evolution (lead: contract design)"]_
- **Skipped phases with reasons:**
  - _[fill: e.g. "phase 3 (architecture delta): lightweight path, single-function bug fix, no architecture impact"]_
- **Skipped skills with reasons:**
  - _[fill: e.g. "frontend-engineering: change touches backend API only"]_
- **No-specialist fallback:** _[fill: "no specialist selected — no applicability signal triggered" when no routing row triggers; otherwise "N/A"]_

## (f) Design: architecture delta / decisions / risks / compatibility / migration / rollback

<!-- Written by phase 3. If there is no architecture impact, record a
     documented "no delta" determination rather than leaving this blank. -->

- **Architecture delta:** _[fill: path to `ARCHITECTURE-DELTA.md`, or "no delta — <reason>"]_
- **Decisions:** _[fill: key design decisions and their rationale]_
- **Rejected alternatives:** _[fill: approaches considered and why each was not chosen]_
- **Risks:** _[fill: what could go wrong; blast radius; what depends on this area]_
- **Compatibility:** _[fill: backward/forward compatibility analysis]_
- **Migration strategy:** _[fill: migration steps, or "none required"]_
- **Rollback plan:** _[fill: how to revert if this change fails]_

## (g) Plan: spec / acceptance criteria / test strategy / task plan / verification report paths

<!-- Written by phases 4–5. Link to specialist artifacts; do not duplicate
     their content here. -->

- **SPEC.md path:** _[fill: e.g. `SPEC.md`]_
- **Acceptance criteria mapping:** _[fill: AC identifiers mapped to change-contract acceptance criteria]_
- **Test strategy:** _[fill: test levels (unit / integration / end-to-end), regression coverage strategy]_
- **TASK-PLAN.md path:** _[fill: e.g. `TASK-PLAN.md`]_
- **QA verification plan path:** _[fill: e.g. `VERIFICATION-PLAN.md`]_
- **Verification report paths:** _[fill: e.g. `VERIFICATION.md`, test output logs]_

## (h) Gates: verdicts / assumptions / rejected alternatives / unresolved boundaries / evidence pointers

<!-- Each gate's owning phase writes its verdict here. Every verdict MUST
     include the exact head SHA to which it applies. Gate numbers group by
     area; chronological execution order is gate 1 → gate 3 → gate 2 →
     gate 4 → gate 5. -->

| Gate | Verdict | Head SHA | Evidence | Conditions / blocker |
|------|---------|----------|----------|---------------------|
| gate-1 (architecture/design delta) | _[fill: pass / conditional / blocked]_ | _[fill: e.g. `a1b2c3d`]_ | _[fill: path to evidence artifact]_ | _[fill: unresolved conditions or blocker reason, or "none"]_ |
| gate-2 (QA test & verification plan) | _[fill: pass / conditional / blocked]_ | _[fill: SHA]_ | _[fill: path]_ | _[fill: or "none"]_ |
| gate-3 (spec + task-plan completeness) | _[fill: pass / conditional / blocked]_ | _[fill: SHA]_ | _[fill: path]_ | _[fill: or "none"]_ |
| gate-4 (independent review) | _[fill: pass / conditional / blocked]_ | _[fill: SHA]_ | _[fill: path]_ | _[fill: or "none"]_ |
| gate-5 (boundary verification) | _[fill: pass / conditional / blocked]_ | _[fill: SHA]_ | _[fill: path]_ | _[fill: or "none"]_ |

**Verdict semantics:** pass = phase may exit, next phase may start. conditional =
phase may exit only with recorded conditions tracked and closed before the next
gate. blocked = phase may not exit, run stops and escalates per
[../references/risk-authority-gates.md](../references/risk-authority-gates.md),
packet transitions to blocked.

**Example (populated gate verdict):**

```text
gate-1 (architecture/design delta) | pass | a1b2c3d | ARCHITECTURE-DELTA.md | none
```

- **Assumptions:** _[fill: unverified assumptions stated explicitly]_
- **Rejected alternatives:** _[fill: design or approach alternatives rejected during gate reviews]_
- **Unresolved boundaries:** _[fill: boundaries not yet verified, or "none"]_
- **Evidence pointers:** _[fill: repo-relative paths to evidence artifacts, updated throughout the run]_

## (i) Lifecycle: PR / CI / review / final verified head SHA / release status

<!-- Written by phases 8–9. The final verified head SHA MUST equal the actual
     final head of the delivered change. -->

- **PR (or review-submission) number:** _[fill: e.g. `#42` or enterprise review ID]_
- **CI status:** _[fill: passing / failing / pending / not-applicable]_
- **Review status:** _[fill: approved / changes-requested / pending / not-applicable]_
- **Final verified head SHA:** _[fill: exact SHA at which all verdicts were re-confirmed, e.g. `7b40de2`]_
- **Release status:** _[fill: not-released / release-ready / released / not-applicable]_
- **Terminal lifecycle state:** _[fill: merged / closed / blocked / released]_
- **Terminal state evidence:** _[fill: merge commit SHA, closure reason, or blocker reference]_
- **Rollback/follow-up triggers:** _[fill: conditions that would cause re-entry after closeout — e.g., a post-release regression requiring rollback or an operational discovery; write "none identified" if there are none. Recorded in the terminal record; any follow-up starts a new change request via phase 1 intake, never by re-opening this packet.]_

**Example (populated lifecycle):**

```text
PR (or review-submission) number: #42
CI status:                        passing
Review status:                    approved
Final verified head SHA:          7b40de2
Release status:                   release-ready
Terminal lifecycle state:         merged
Terminal state evidence:          merge commit 8c31ef4
Rollback/follow-up triggers:      post-release smoke check failure in the
                                  export path; operational discovery of
                                  multi-byte handling in adjacent endpoints
```

### Blocked-state record

<!-- Complete this subsection ONLY if any gate verdict in section (h) is
     blocked. A blocked verdict transitions the packet to the blocked
     lifecycle state. Do not continue from a blocked packet without new
     authority or instructions. -->

- **Failing gate identifier:** _[fill: e.g. `gate-4-independent-review`]_
- **Phase at which it occurred:** _[fill: e.g. `phase-7-independent-review`]_
- **Blocking evidence:** _[fill: what was observed that failed the gate]_
- **Escalation outcome:** _[fill: decision or authority needed to proceed, per ../references/risk-authority-gates.md]_

## Shared field reference

The following field categories share identical names and semantics with
[change-contract.md](change-contract.md) and
[evidence-ledger.md](evidence-ledger.md):

- **Change-request provenance** — change-request URL or number; source type
  (issue / ticket / email / verbal); repository; base ref.
- **Skip reason** — a concrete reason why an expected action was skipped or
  deemed unnecessary; silent omission is prohibited.
- **Gate verdict** — gate identifier; verdict (pass / conditional / blocked);
  supporting evidence; head SHA at which the verdict was reached.
- **PR / CI status** — PR (or review-submission) number; CI status.
- **Release status** — release disposition: not-released / release-ready /
  released / not-applicable.
