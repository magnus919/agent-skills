# Decision rights for agentic engineering

Use this reference when deciding what a software factory may do, what accountable humans retain, and what evidence supports those boundaries. Apply the existing scoped earned-autonomy model; an unattended factory is an operating choice, not a maturity requirement. Reuse valid authorization rather than adding approval to every action.

## Assign decisions before delegating execution

Record each decision in `templates/engineering-decision-rights.md`. Separate the accountable owner, the actor who prepares or executes work, the authority to approve changes, and the system that enforces the boundary. A human title alone does not specify any of these.

| Decision | Delegation to consider within an existing grant | Decision retained by accountable owners |
|---|---|---|
| Release intent and non-goals | Research, propose alternatives, identify ambiguity | Select outcomes, resolve material ambiguity, accept tradeoffs and scope changes |
| Decomposition and implementation | Create bounded tasks, order dependencies, implement and repair | Define scope constraints and the conditions requiring renewed review |
| Acceptance criteria and assurance | Propose scenarios, run authorized checks, assemble evidence | Approve the acceptance basis and consequential changes to it; designate who may judge acceptance |
| Merge and staging | Execute an approved pipeline within repository/environment bounds | Set the applicable merge/staging grant and review conditions |
| Integrated intent and residual risk | Demonstrate the candidate and surface gaps | Assign intent acceptance and residual-risk acceptance to named authorized decision makers |
| Production promotion | Prepare a release or execute an already authorized promotion | Set production authority, prerequisites, rollback ownership and expiry |
| Supervision and recovery | Reconcile state, retry or reassign within shared budgets | Approve changes to objectives, authority ceilings or recovery limits |

These are policy design choices, not a universal requirement for a fresh human click at each row. Owners may authorize routine decisions through explicit policy and bounded grants. Record the human-only decisions, prohibited effects, review triggers and expiry for this release. A supervisor cannot infer broader rights from its responsibility to finish work. An agent may propose a policy change without being authorized to activate it.

Separate four judgments in the evidence record: **technical readiness**, **acceptance of intended behavior**, **acceptance of residual risk**, and **authority to promote**. One person may own several where policy permits, but one green test report cannot stand in for all four. Staging access and successful staging validation do not confer production access.

## Make human oversight usable

Choose checkpoints by consequence, uncertainty, reversibility and the demonstrated reliability of the workflow. A small authentication change may need more scrutiny than a large cosmetic change. Do not use ticket count or code size as a risk proxy.

For every reserved human decision, specify:

- The exact candidate and evidence the reviewer receives: intended outcome, material changes, observed behavior, engineering findings, unresolved failures, uncertainty and rollback implications.
- The reviewer's competence, authority, available time and expected review load. Batch size must leave a realistic opportunity to understand the decision.
- The ability to reject, redirect, request evidence or stop work before the consequential action; identify how the execution system honors that decision.
- What happens when review is late, absent or inconclusive. Silence and timeout are not assent. Hold the affected transition or use a previously authorized fallback; unaffected work may continue within valid scope.

Track approval fatigue, unexplained rapid approvals, missed ambiguities and overrides as signals that the checkpoint may be ineffective. Respond by improving the evidence, reducing batch size or unattended scope, or changing reviewer capacity. Do not silently remove the checkpoint to improve throughput. This is an evidence-based operating adjustment, not a failure to reach maximum autonomy.

## Protect the terms of delegation

Identify the artifacts that define authority: release goals and exclusions, policy ceilings, approval rules, acceptance criteria, protected test oracles and gate configuration. Builders and supervisors must not unilaterally rewrite these terms to make their own work pass. Ordinary code and developer-test repair remains allowed where the grant permits it; classify protected artifacts explicitly rather than prohibiting every test edit.

Require a separate authorized revision path for protected changes. Record the owner, rationale, old and new revision, affected candidate, and which evidence must be renewed. A changed acceptance basis invalidates the affected prior acceptance evidence. Preserve unaffected evidence only with a documented scope rationale. Repository prose is not enforcement: give the control owner responsibility for permissions, protected branches, isolated evaluation access and receipts that demonstrate the boundary holds.

Separate implementation, evaluation and acceptance responsibilities enough to expose conflicts of interest. A second agent or fresh context does not establish evaluator independence by itself. Specify who controls the oracle and what the builder can read or modify. Missing isolation evidence is an assurance gap, not independent acceptance. Use the QA skill for the test design and disclosure ledger.

A recovery supervisor needs its own scoped grant. Reassignment must preserve cumulative budgets and approval requirements. Stuck tasks or dependency changes can justify an escalation or a bounded recovery action; they cannot justify quietly changing intent, resetting retry budgets, broadening credentials or declaring human acceptance.

## Worked decision

An invoice feature has authorized implementation and staging grants, passing developer checks and a clean engineering review. The integrated staging demo reveals ambiguous visibility rules. The intended reviewer cannot review the release this week; production promotion has no current grant.

Record technical readiness only to the extent supported by the checks. Hold the affected acceptance decision while the product owner resolves visibility intent. Assign reviewer capacity or reduce the release batch; do not treat absence as approval. If the owner changes the acceptance basis, revise it through the authorized path and renew affected evidence. Continue unrelated work only within still-valid boundaries. Production remains unauthorized until its own conditions and grant are satisfied, even if the revised staging checks pass.

## Implementation handoffs and completion

Governance owns decision rights, acceptable evidence and risk acceptance. Route execution details to:

- `../bmad/SKILL.md`: release intent, checkpoints and integrated acceptance (`../bmad/references/release-intent-acceptance.md` in that skill).
- `../qa-methodology/SKILL.md`: protected holdout scenarios, exposure and contamination (`../qa-methodology/references/holdout-scenarios.md`).
- `../spec-driven-development/SKILL.md`: behavior and engineering review lanes bound to a candidate (`../spec-driven-development/references/factory-review-lanes.md`).
- `../harness-engineering/SKILL.md`: supervisor enforcement, durable state, leases and shared budgets (`../harness-engineering/references/factory-supervision.md`).
- `../release-engineering/SKILL.md`: approved promotion and rollback implementation.

Paths above are relative to the skill root. Complete the governance review when the worksheet identifies owners, effective grants, protected terms, evidence gaps, review capacity and the enforcement handoff. If a consequential decision lacks authority or sufficient evidence, record HOLD for that transition, its owner and next action. A completed governance record is not proof of activated runtime controls.

## Source and interpretation

Cole Medin's [My AI Dark Factory Dream Is Dead (Here's What Actually Works)](https://www.youtube.com/watch?v=GQatuTWSRqY), published October 16, 2026, supplies practitioner examples: release planning outside the factory (9:03), holdouts (10:51), selectable checkpoints (11:48), separate validation/review (14:26), bounded supervision (15:32), protected mission/rules (16:35), and human staging feedback before production (17:40). These are observations from his workflow, not comparative performance evidence or proof that unattended factories cannot work.

The decision-rights matrix, review-capacity conditions and protected-change procedure here are governance synthesis applied to those examples. They extend this skill's existing earned-autonomy guidance; they are not claims that the speaker presented a governance standard.
