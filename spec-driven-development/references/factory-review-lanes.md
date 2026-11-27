# Behavior and engineering review in a software factory

Load when a factory produces plausible PRs but functional correctness and long-term
maintainability need distinct evidence. Preserve the existing four SDD gates.
Gate 3 checks task/spec compliance; assign an additional engineering review lane
before integration. Gate 4 reconciles required lanes for the integrated release.
The lanes may share a review record, but one lane's PASS cannot substitute for another.

## Minimum planning handoff

Accept an existing approved PRD, architecture document or issue set when it supplies:
owner and version; desired user outcome; in/out-of-scope behavior; observable
acceptance and relevant NFRs; interfaces/dependencies; unresolved decisions with
owners and latest safe decision points; and allowed integration/promotion actions.
Map requirement IDs to tasks and verification. Add only missing information rather
than copying a sound document into a competing source of truth. Gates validate
content and traceability, not a required filename.

Choose a release small enough to demonstrate integrated outcomes, inspect its
engineering consequences and recover within the team's budget. Ticket count is
not a universal sizing rule. Route work by both complexity and consequence: a
one-line authorization change may need a fast implementation but deep security
verification. Existing permission and regulatory requirements remain binding.

For a feature that users describe differently from how the repository names it,
link a [feature map](../templates/FEATURE-MAP.md) from the planning handoff.
It maps user language to a running journey, initial state, transition, evidence
and a reusable driver. It points to existing acceptance criteria; it is not a
parallel specification or proof that the journey passed.

## Two evidence lanes

| Lane | Question | Evidence | Typical finding |
|---|---|---|---|
| Behavioral acceptance | Does the candidate do what the contract requires at the relevant surface? | Executed user/service journeys, persisted state, negative cases, contracts and NFR checks | UI says saved but state disappears on reload |
| Engineering review | Can the team responsibly maintain and evolve this implementation? | Inspected diff and surrounding architecture, ownership, coupling, dependency changes, error paths and relevant checks | Three PRs introduce competing representations of the same domain concept |

Choose user-surface checks appropriate to the change; a documentation edit does
not require a browser run. A screenshot or successful unit suite alone does not
prove an end-to-end interaction. A working journey does not establish maintainability.
Assign reviewers and explicit criteria before execution. Separate review context
helps but does not itself prove independence of errors.

Use [the factory review record](../templates/FACTORY-REVIEW.md). Both lanes bind
the same candidate/content hash, accepted contract and relevant environment.
Task evidence remains useful history after integration; it cannot silently become
release evidence. Inspect combined changes and rerun affected checks against the
integrated candidate. Record justified reuse of unaffected evidence.

## Route evidence before spending on review

Run the applicable inexpensive, trusted checks first when failure would make
specialist review premature. Keep acceptance criteria and the check definition
under the appropriate owner, not editable by the candidate to obtain a pass.
Fix or explain a failed build before paying for semantic review of that revision.
Choose specialist lanes from changed surfaces and consequences, not a fixed
agent roster. For example, a course-access change needs behavioral cases for
eligible and ineligible users and a policy-owner decision if entitlement changes.
A passing build or a model verdict cannot authorize that policy change. Reclassify
the lanes if repair touches a new surface.

See the [factory handoffs evidence ledger](https://github.com/magnus919/agent-skills/blob/main/docs/research/factory-handoffs-and-review/evidence.md)
for the source case and where the evidence stops.

## Disposition and bounded repair

- Failed behavior: route to implementation unless the contract/oracle is wrong.
- Unclear intent: route to the contract owner; do not patch repeatedly toward a guess.
- Engineering defect: give a concrete maintainability consequence and required fix,
  rather than imposing personal style or a new abstraction without justification.
- Missing evidence: keep the lane unresolved; do not infer PASS from silence.
- Candidate, contract, dependency or configuration change: supersede affected verdicts.

Keep retry/time limits and a named escalation owner. A repair that changes risk or
scope must be reclassified; it does not automatically qualify for the fast path.
Required failed or unresolved lanes block integration/promotion at their declared
boundary. Exceptions follow the existing authorized policy and record scope,
reason and owner; a model cannot waive its own gate. Preserve SDD's
APPROVED/CONDITIONS/REJECTED vocabulary for the overall gate decision.

## Worked integration example

Three workers add invoice creation, export and notifications. Each task passes
against its own snapshot. After integration, export reads a stale invoice status,
and notifications duplicate a state mapping. Behavioral review fails the exported
status; engineering review identifies competing mappings. Repair and rerun the
invoice-to-export-to-notification journey on the new integrated candidate, then
review the resulting shared contract. Three green task reports cannot close either
release-level finding.

Complete when all required lanes have current evidence and a disposition that
permits the next boundary, or escalate the unresolved criterion with its owner.
QA owns test/oracle design; verification-methodology owns evidence judgments;
bmad owns intent changes; release-engineering owns promotion and rollback.

## Worked review: settings to export

Use the [mapped journey](../templates/FEATURE-MAP.md#example-settings-to-export)
and [driver qualification](../../verification-methodology/references/evidence-standards.md#worked-example-a-disposable-settings-to-export-driver).
In this illustrative review, the baseline preserves the reference-column setting
after reopening, but the downloaded header omits it. The candidate preserves the
setting and writes the column and both expected rows. With the option off, both
revisions omit the optional column and still export both rows. These observations
would establish the regression and its repair on the exercised path.

Assign distinct probes based on consequences. One reviewer exercises save,
reopen, and rejected save. Another starts from an independently seeded equivalent
profile and observes how export consumes each preference state, including a
normal download and the empty-data path. Record explicit coverage and reconcile
overlap. If an entitled scheduled export is required but unavailable, leave that
criterion unresolved and keep the required lane open. When a dependency change
affects serialization during integration, exercise the export again against the
actual integration candidate. Keep the engineering assessment and policy decision
in their existing lanes.

## Source and limits

Cole Medin distinguishes [validation and code review at 14:26](https://www.youtube.com/watch?v=GQatuTWSRqY&t=866s)
and discusses [release planning at 9:03](https://www.youtube.com/watch?v=GQatuTWSRqY&t=543s)
in his 16 October 2026 practitioner account. The lane contract is our synthesis,
not a measured improvement or a universal requirement for human review of every PR.
