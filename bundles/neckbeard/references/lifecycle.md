# Change Lifecycle Integration

The platform mechanics for carrying a change request from intake to an authorized
post-merge release. This reference is loaded by [../SKILL.md](../SKILL.md)
**only** for change-request / issue-to-PR / ticket-to-release work — a request
that will produce a pull request or an equivalent reviewable deliverable. A
single-line edit, an ad-hoc fix, or a review without an issue/ticket trajectory
does **not** load this reference; that work uses the core loop in
[../SKILL.md](../SKILL.md).

The lifecycle does not invent phases or gates. It maps onto the nine-phase
change-request journey ([journey.md](journey.md)) and the five gates
([stages.md](stages.md)). It records its outcomes in the delivery packet
([delivery-packet.md](delivery-packet.md)), field group (i) — PR/review-submission
number, CI status, review status, **final verified head SHA**, and release status
— plus the terminal-state evidence those states require. Stop and escalation
rules live in [risk-authority-gates.md](risk-authority-gates.md).

## Two modes, one structure

The workflow is platform-neutral. Two documented modes share the **same phase
sequence, the same five gates, and the same packet fields**; only the platform
mechanics differ.

| | **GitHub reference mode** | **Enterprise mode** |
|---|---|---|
| Use when | The target repository is **public/open-source** (public remote, open-source license, contribution governance). | The target repository is **private or enterprise-internal**: ticket trackers, private hosting, enterprise review and CI tooling, change governance. |
| Source of truth | An issue in the repository tracker. | A ticket, email thread, or verbal request. |
| Review submission | A pull request. | An enterprise change request / review submission. |
| Authority to merge | Maintainer action on a protected branch. | Enterprise approval workflow / change manager. |
| Authority to release | A separate grant beyond merge. | A separate authorization (CAB, change-manager sign-off, change-freeze window). |

**Mode selection is recorded** in packet group (b). GitHub is a documented
*reference* mode, never the assumed default. Enterprise mode makes no
open-source assumption — no public visibility, no fork-based contribution, no
community norms.

---

## GitHub reference mode

GitHub mechanics are described here; contribution *norms* are delegated to the
catalog skill `opensource-contributions` and are discovered **per repository**,
never hardcoded.

### Contribution-norm delegation (public/OSS only)

> **Load `opensource-contributions` only when the repository is public/OSS**
> (public remote and an open-source license). It owns contribution-norm detail:
> `CONTRIBUTING.md` interpretation, agent disclosure, fork etiquette, commit
> conventions, PR templates, and post-submission etiquette. This reference
> **delegates** to it and does not re-derive its content.

If the repository is private or enterprise-internal, do **not** load
`opensource-contributions`; use enterprise mode below, and record the skip in
packet group (e) with the reason "non-public repository."

### 1. Snapshot the issue and repository context before planning — phase 1

Before any planning or implementation begins, capture **all** of the following
as mandatory intake artifacts. The phase 1 intake gate
([journey.md](journey.md)) cannot be satisfied without them.

- **Issue body** — the full request text.
- **All issue comments** — not just the opening post.
- **Linked and referenced work** — related issues, PRs, and commits that touch
  the same problem.
- **Repository conventions** — `CONTRIBUTING.md`, `AGENTS.md`, `.github/`
  templates, or equivalent, **discovered per repository**.
- **Base ref** — the current base branch ref the change will target.

Record these in packet group (a). Planning may not start until the snapshot is
complete.

### 2. Classify authority — phase 1

Classify the granted authority into **four separate classes** and record each
before implementation. These complement the authority classes in
[risk-authority-gates.md](risk-authority-gates.md) (Explore / Modify / Publish /
Deploy / Merge); they are never collapsed into a single "has access" judgment.

| Class | Scope |
|---|---|
| **Contributor** | Can fork, branch, and open a PR. |
| **Maintainer** | Can approve, review, and close. |
| **Merge** | Can land a change into a protected branch. |
| **Release** | Can tag, publish, or deploy. |

Record the granted class per row in packet group (b). A contributor grant does
not imply merge or release authority. Merge authority does not imply release
authority (see [Authority boundary](#authority-boundary-readiness-vs-release)).

### 3. Pre-work integrity checks — phases 1–2

These checks run **before** a branch is created and before work proceeds. Each
has its own recorded outcome in the packet; they are distinct, not one merged
check.

| Check | What it does | Recorded outcome |
|---|---|---|
| **Duplicate-issue search** | Search the repository issue tracker for an existing issue describing the same or overlapping problem. | "duplicate found and handled" or "no duplicate." |
| **Existing-PR search** | Search for **open and recently closed** PRs addressing the same issue or problem, including PRs from other contributors not linked to the issue. | "PR found — see handling" or "no existing PR." |
| **Conflicting-branch check** | Check whether another contributor has already pushed a branch targeting the same issue or change surface. | Coordinate, wait, or proceed-with-awareness decision. |
| **Maintainer-direction review** | Review issue comments, assignments, labels, and governance docs for explicit direction ("I'll handle this," "don't work on this yet," "assigned to X," a deferral label). | Proceed, or **stop/escalate** if direction conflicts. |

**Maintainer direction is a hard gate.** If maintainer direction conflicts with
proceeding, the agent must **not** proceed regardless of the other checks. This
is consistent with the stop rules in
[risk-authority-gates.md](risk-authority-gates.md).

**Handling an existing open PR (no duplicate work).** When the existing-PR
search finds an open PR addressing the same problem, decide and record:

- **Continue/assist** if it is the agent's own prior work — resume from packet
  state ([delivery-packet.md](delivery-packet.md), resumability).
- **Coordinate or defer** if another contributor owns it.
- **Never open a duplicate PR.** The decision is recorded in the packet.

### 4. Determine fork-vs-branch before PR creation — phase 6

Before creating a branch or PR, determine the repository's contribution workflow
from `CONTRIBUTING.md`, `.github/` conventions, or maintainer direction —
**per repository**, never assumed:

- **Fork-and-PR** vs **branch-in-repo**.
- Record the choice in the packet, and apply fork etiquette via
  `opensource-contributions` when a fork is required.

The lifecycle never assumes a branch-in-repo workflow or leaves the mode
implicit.

### 5. PR readiness, submission, and merge are separate states — phases 6–8

These three states are explicitly distinct; reaching one does not grant the next.

| State | Meaning | Who controls it |
|---|---|---|
| **Ready** | Code complete, self-reviewed, tests pass locally, verification evidence recorded. | The agent can reach this independently. |
| **Submitted** | The pull request is opened. | The agent performs the act of opening. |
| **Merged** | The change lands in the protected target. | Requires **maintainer action** plus passing CI and approved review — **not** the agent's own readiness assessment. |

Merge is gated on external authority beyond the agent's readiness declaration.

**Issue linkage and closing keywords.** The PR body must (a) reference the
source issue by number and (b) use the repository's own closing-keyword
convention, discovered from `CONTRIBUTING.md` or project norms (e.g.,
`Closes #N`, `Fixes #N`, `Resolves #N`). If the repository specifies no
convention, use a defensible default: `Closes #N`.

**PR body content.** Beyond the issue link and closing keyword, the PR body
describes the change — **what** it does, **why**, and **how it was verified** —
and follows the repository's PR template if one exists (discovered per
repository).

### 6. Post-submission monitoring — phase 8

After the PR is submitted, both monitors are mandatory and run until they
terminate; checking once is not enough.

**CI monitoring.** Monitor CI status until CI completes. CI failure is a
**blocking** condition: the PR is never merge-ready while CI is red. When CI is
red, **triage** it:

1. **Diagnose** the failure from the logs.
2. **Fix** it if the failure is attributable to the change.
3. **Escalate** when the failure is undiagnosable after two attempts
   (per [risk-authority-gates.md](risk-authority-gates.md)).

Never consider the PR merge-ready, and never merge it, while CI is failing.

**Review monitoring.** Monitor for review feedback (comments, change requests,
approvals) and respond to **material** feedback with code changes rather than
argument. Review monitoring is distinct from CI monitoring.

### 7. Material change and exact-head binding — phases 7–8

Every material change pushed after initial submission — any change that alters
behavior, fixes a bug, or responds to review feedback beyond a trivial typo fix
— **invalidates prior verification verdicts** and must return through both
independent review (**gate 4**) and boundary verification (**gate 5**) before
the PR is merge-ready again. A stale verdict on a superseded head SHA is never
carried forward; the new head is independently verified.

Materiality uses the **canonical definition** owned by [stages.md](stages.md)
(§ Gate 5 — Material change definition):

- **Material** (invalidates verdicts, re-verify): alters logic, adds/removes
  functionality, modifies the verification surface, changes test assertions, or
  alters data flow across a trust boundary.
- **Non-material** (verdicts stand, SHA binding updated): typo fixes,
  formatting-only, comment-only edits, pure renames without behavior change,
  docs-only changes, and rebases with no semantic diff.

**The merge-readiness verdict is bound to the exact full head SHA.** No verdict
is valid without a bound SHA, and a verdict referencing a different SHA (e.g.,
from before a rebase or force-push) is explicitly **stale and insufficient**.

**Update the final-verified-head-SHA field after every review round.** Each
review round ends with packet group (i) **final verified head SHA** refreshed to
the current head and fresh verification evidence recorded for that head:

- A round that pushes a change updates the field and re-runs verification.
- A round that changes nothing keeps the existing SHA.

The final verdict is always bound to the exact final head of the delivered
change. This is the same rule expressed in [journey.md](journey.md) phase 8 and
in the packet's exact-head-binding section.

---

## Enterprise mode

Enterprise mode uses the **same nine phases and five gates** as GitHub mode. It
makes no open-source assumption and does not reference `opensource-contributions`.

### 1. Source-of-truth snapshot — phase 1

Capture the authoritative request from wherever it actually lives — it is **not**
assumed to be a GitHub issue:

- A **ticket-tracker** entry (ticket ID, description, comments), **or**
- an **email thread**, **or**
- a **verbal** request (transcribed with attribution).

Record the snapshot, the repository, and the base ref in packet group (a). The
phase 1 intake gate cannot be satisfied without it.

### 2. Duplicate / existing-change-request check — phases 1–2

Equivalent to the GitHub duplicate-issue and existing-PR checks:

- Search the ticket tracker for an **open change request** covering the same
  problem.
- Search for any **existing change branch / CR in flight**.
- **Record the result.** If one exists, coordinate or defer.

Enterprise intake does not end at snapshotting the ticket; the dedup outcome is
recorded in the packet.

### 3. Authority classification and approval gate — phases 1, 7

Classify authority using the same four classes as GitHub mode (contributor,
maintainer-equivalent, merge, release) and record them in packet group (b).

**Explicit approval gate.** Enterprise review requires a named approver sign-off
that the **merge gate depends on**:

- a **named reviewer/approver**;
- a **recorded verdict** in the packet;
- the verdict **feeds the merge gate** (phase 8 readiness → merge).

This is the enterprise equivalent of GitHub review approval (gate 4). Review is
not merely "integrating with review tooling" — it produces a recorded approval
verdict.

### 4. Enterprise CI and change governance — phase 8

- **Enterprise CI.** Integrate with the enterprise CI system (not assumed to be
  any particular provider); monitor it after submission exactly as GitHub mode
  monitors CI, and triage red CI (diagnose, fix, or escalate). The PR/change is
  never merge-ready while CI is red.
- **Change-governance boundaries.** Respect **CAB approval**, segregation-of-
  duties constraints, and **change-freeze windows**. A change-freeze that blocks
  deployment is an escalation condition ([journey.md](journey.md) phase 9).

### 5. Release authority separation — phase 9

Release activity (deploy, publish, promote) requires **explicit authorization
distinct from merge approval** — for example CAB approval, change-manager
sign-off, or change-freeze-window clearance. The merge/approval gate alone does
**not** authorize release. Record the authorization in the packet's
**release status** field. This mirrors the GitHub-mode authority boundary and
the release gate in [risk-authority-gates.md](risk-authority-gates.md).

### Packet portability across modes

The packet is mode-agnostic: the same nine field groups, with the same field
names and semantics, are populated in both modes. GitHub-only fields have
documented enterprise equivalents:

| Packet field (group i) | GitHub mode | Enterprise equivalent |
|---|---|---|
| PR (review-submission) number | Pull-request number | Enterprise change-request / review ID |
| CI status | Hosted CI result | Enterprise CI result |
| Review status | PR review approval | Named-approver sign-off verdict |
| Final verified head SHA | Head commit SHA | Head commit SHA (identical) |
| Release status | Tag/publish disposition | Deploy/promote disposition (CAB/clearance) |

No packet field is fillable only in GitHub mode.

---

## Authority boundary: readiness vs release

Pre-merge **release readiness** and post-merge **release activity** are separate
gates with separate authority, in both modes.

- **Release readiness (pre-merge, assessable):** the change is releasable —
  version bumped, changelog updated, migration documented, rollback plan exists.
  This can be confirmed before merge and feeds the readiness gate (phase 8).
- **Release activity (post-merge, gated):** tagging, publishing artifacts,
  deploying, announcing. This is a **separate gate requiring explicit
  authorization beyond merge authority.** Merge does not imply release.

The merge gate verifies readiness; release execution is gated on a separate
explicit authorization. See [risk-authority-gates.md](risk-authority-gates.md)
for the merge gate and release gate definitions.

### Release execution records post-release verification

The release gate does **not** end at the authorization grant. Before the
`released` terminal state is declared, record **post-release verification
evidence** — a post-release smoke check, deploy/tag confirmation, or artifact
checksum — in the packet's **release status** field.

---

## Terminal states

Exactly four terminal states end a lifecycle, each requiring specific evidence
recorded in packet group (i). There is no ambiguous "done" without evidence.

| Terminal state | Meaning | Required evidence |
|---|---|---|
| **merged** | Landed into the protected target. | The **merge commit SHA**. |
| **closed** | Not merged; ended without code. | The **close reason** (e.g., duplicate, already fixed, withdrawn). |
| **blocked** | Cannot proceed. | **Blocker evidence** — the blocking condition and any escalation outcome. |
| **released** | Authorized post-merge release completed. | **Release evidence** (tag, artifact, deploy confirmation, post-release smoke check). Terminal — no transitions out. |

These are the same terminal states defined by the packet
([delivery-packet.md](delivery-packet.md), lifecycle states) and by journey
phase 9 closeout ([journey.md](journey.md)). A terminal packet is never
re-opened; new work starts a new packet.

### Reduced paths still terminate with evidence

A reduced (lightweight) run terminates in a defined terminal state, not an
unspecified early stop:

- A **no-change-needed** run records the determination and transitions to
  **closed** with the close reason and its evidence (no PR created).
- A **docs-only** change that ships reaches **merged** with the merge SHA (doc-
  update evidence).

The packet's terminal lifecycle state field is populated on every reduced path.

### External cancellation mid-flight

If the change request is closed or cancelled by an external actor at any phase
after intake — a maintainer closes the issue, a ticket is withdrawn, a PR is
closed by a maintainer — the packet transitions to the appropriate terminal
state (**closed** or **blocked**) with the **external closure as evidence**, and
the remaining phases are **not** executed. This is distinct from the
no-change-needed termination ([journey.md](journey.md)) and from the
gate-failure **blocked** state ([delivery-packet.md](delivery-packet.md)).

---

## Delivery-packet fields this reference reads and writes

The lifecycle records its outcomes in the packet. It reads provenance and
authority from groups (a)–(b) and writes to the groups below; every named field
exists in [delivery-packet.md](delivery-packet.md).

| Lifecycle step | Packet field(s) | Group |
|---|---|---|
| Snapshot the issue / source of truth | Issue snapshot (request text, comments, linked work) | (a) |
| Classify authority | Authority class (contributor / maintainer / merge / release) | (b) |
| Record mode and pre-work check outcomes | Workflow mode; dedup/PR/branch/maintainer-direction decisions | (b), (e) |
| Open the PR / review submission | PR (review-submission) number | (i) |
| Monitor CI | CI status | (i) |
| Monitor review | Review status | (i) |
| Bind verdicts per review round | **Final verified head SHA** | (i) |
| Assess release readiness and execute release | Release status (with post-release verification evidence) | (i) |
| Close out | Terminal lifecycle state + terminal-state evidence (merge SHA / close reason / blocker evidence / release evidence) | (i) |

Field group (i) — PR number, CI status, review status, final verified head SHA,
release status, and terminal-state evidence — is the exact set this reference
populates; the match is bidirectional (no field here that the packet lacks, and
no group-(i) field the lifecycle never writes).

## Lifecycle-to-journey mapping

Every lifecycle step and every packet lifecycle state maps onto a journey phase
that [journey.md](journey.md) defines. No phase here is invented or renamed.

| Lifecycle step | Journey phase |
|---|---|
| Snapshot, authority classification, pre-work checks, fork-vs-branch decision | Phase 1 (intake and provenance) and phase 6 (implementation) for branch creation |
| Duplicate / dedup and discovery | Phase 2 (current-state discovery and reproduction) |
| Implementation commits | Phase 6 (domain-specific implementation) |
| Independent review, boundary verification, CI/review monitoring, exact-head re-verification, readiness | Phase 7 (independent review and boundary verification) and phase 8 (readiness, CI/review loops) |
| Merge / approval gate | Phase 8 → phase 9 boundary |
| Authorized release, closeout, terminal-state evidence | Phase 9 (authorized post-merge release and closeout) |

| Packet lifecycle state | Journey phase |
|---|---|
| intake | Phase 1 |
| planning | Phases 2–5 |
| implementation | Phase 6 |
| in-review | Phases 7–8 |
| ready | End of phase 8 (readiness gate passed) |
| merged / closed / blocked / released | Phase 9 (terminal closeout) |
