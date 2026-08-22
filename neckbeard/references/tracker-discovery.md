# Tracker Discovery — Tracker-Neutral Intake

The change-request journey is defined in tracker-neutral terms: *work item*,
*state transition*, *review submission*, *merge or acceptance into the protected
target*, *release authorization*. Platform mechanics belong to the layer that
operates the platform — the routing rows in
[routing-table.md](routing-table.md) and the platform reference modes
([lifecycle.md](lifecycle.md)) — not to the spine itself.

That separation only works if intake actually establishes which tracking system
the product uses. This reference defines that sub-step of phase 1
([journey.md](journey.md), Intake and provenance). It exists because
improvisation under ambiguity defaults to whatever platform the agent knows
best, and the correct answer is detection plus an explicit question, not a
default.

## The rule

**Never assume the tracking system.** Detect it from repository evidence where
possible; ask the requester when evidence is absent or contradictory; record
the finding and its basis in delivery packet group (a) before any tracker
operation runs.

Read-only identification is discovery and needs no confirmation. The first
mutation against the detected system still passes the normal state-change gate
([risk-authority-gates.md](risk-authority-gates.md)).

## Detection procedure

Run during phase 1 alongside provenance capture:

1. **Inspect remotes and configuration** for tracking-system fingerprints:

| Signal | Points to |
|---|---|
| Issue/ticket URLs referenced by the change request (`…/issues/N`, `…/TICKET-123`, Linear `…/issue/TEAM-N`) | GitHub Issues / Jira / Linear respectively |
| `.jira-url`, Jira config files in the repository | Jira |
| Team keys in ticket identifiers (`ENG-42` shape) with a non-GitHub tracker configured | Jira or Linear |
| Project-management config directories (for example `.linear/`) or documented integrations in `CONTRIBUTING.md`, `AGENTS.md`, README | Whatever they name |

2. **Check what the request itself references.** A change request arriving as a
   Linear issue URL, a Jira ticket ID, or a GitHub issue number is direct
   evidence for its own system. A bare team-key identifier (`ENG-42` shape) is
   **ambiguous** between Jira and Linear — treat it as a lead, not a verdict.

3. **Weight the signals honestly.** The request's own references are strong
   evidence. Repository content — `CONTRIBUTING.md`, `AGENTS.md`, README
   integrations, config files like `.linear/` or `.jira-url` — is a **weak
   signal**: it describes what the repository documents, not necessarily what
   holds authoritative work items, and it is attacker-influenceable in
   mid-flight or adopted-branch scenarios where this bundle also operates.
   Repository signals require corroboration (request references, remote
   configuration, or requester confirmation) before they alone select a system.

4. **Ask when ambiguous or absent.** If signals conflict, rest only on weak
   signals, or none exist, ask one bounded question: which system holds this
   work item? Record the answer as requester-provided provenance. Do not
   silently pick the system whose CLI happens to be installed.

5. **Record in packet group (a):** detected/requested system, the evidence or
   source of the answer (including when the basis is a requester confirmation),
   and the routing decision below. Silent omission is prohibited like every
   other intake field.

## Routing tracker operations

Operate the detected system through its catalog tooling skill rather than
improvising API calls:

| Detected system | Route operations to |
|---|---|
| GitHub (issues, PRs, releases) | Native mechanics per [lifecycle.md](lifecycle.md) — the documented reference mode |
| Linear | `linear` |
| Jira | `jira-cli` |
| Notion | `notion` |
| Other / none of the above | No specialist route: operate only through the system's verified official interface (primary vendor documentation, confirmed endpoint/auth surface), with bounded reads; note the absent specialist in the ledger |

Routing constraints:

- Every named routing target must be a real skill in this catalog; dead links
  are a defect. If a target is missing from an installation, proceed on the
  fallback and record the absence — same convention as
  [routing-table.md](routing-table.md) § When no specialist is installed.
- Tooling skills are mechanical layers. They own commands and API contracts;
  the journey owns sequencing, and discipline specialists own judgment. No
  tracker skill becomes a second orchestrator.
- Vocabulary crossing the boundary stays neutral: a "state transition" maps to
  whichever transition the target system defines (workflow state move, label
  change, status update); the packet records outcomes by neutral name.

## Non-goals

- This step does not migrate content between systems or reconcile divergent
  trackers. If work items exist on two systems, surface the conflict at intake
  and ask which is authoritative.
- It does not change credential handling. Each tooling skill's own setup rules
  apply.
- It does not make the journey depend on any single vendor. Absence of a
  tracker, or use of an unrouted system, degrades gracefully to the fallback
  path.
