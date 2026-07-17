# Linear Domain And Workflows

Linear organizes work around teams. Issues belong to a team and can be associated with a project
and cycle. A project expresses a larger outcome; a cycle groups time-bounded team work. Use an
issue for actionable work and a document for durable narrative, planning, or reference material.

## Workflow Semantics

Workflow states have types including `triage`, `backlog`, `unstarted`, `started`, `completed`, and
`canceled`. Creating an issue without `stateId` places it in the team's first Backlog state, or in
Triage when that feature is enabled. Priorities are numeric in the API: 0 none, 1 urgent, 2 high,
3 medium, and 4 low.

Issue IDs can be UUIDs or shorthand identifiers such as `ENG-42`. Obtain object UUIDs in Linear
with the command menu's “Copy model UUID” action. A parent issue groups child issues; use children
only when their work is independently actionable and trackable.

## Choosing A Work Item

Start with an existing issue whenever a request refers to known work. Search by distinctive words,
then inspect the result before changing it. Use the issue identifier in follow-up work because it
is shorter and is accepted by the public API.

Use a project when the user asks about a larger initiative or its status. Use a cycle when the user
asks about a team's current or planned timebox. Neither changes the mutation boundary of this CLI:
all writes remain issue-scoped.

Descriptions, comments, and documents support Markdown. Plain Linear URLs to users, issues,
projects, and other resources become mentions in the Linear UI. Collapsible Markdown sections use
`+++ Title` to open and `+++` to close.

## Safe Mutation Recipe

1. Read the target issue and relevant team, project, cycle, or state first.
2. Check for an existing issue with `issue search` before creating another one.
3. State the exact change and recovery path to the user.
4. Run the mutation with `--dry-run --json`; friendly references are only resolved during a live run.
5. Run the same command with `--confirm --json` only after confirmation.
6. Report the returned identifier and outcome. If a change is wrong, use `issue update` or `issue move`
   to restore the prior value rather than guessing.

Use an issue comment for a dated, issue-specific update. Use a document when the information must
remain useful beyond one issue. Do not create duplicates for work that an existing issue already
covers; link or update the existing issue instead.

Do not treat a completed or canceled state as reversible without checking the team's workflow and
the requested recovery path. State names are workspace-defined, so resolve the exact destination
inside the issue's own team rather than assuming a universal “Done” state.
