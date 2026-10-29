# Review records, assumptions, and finding closure

Use the existing project tracker or documents as authoritative records. The fields
below extend SPEC, TASK-PLAN, REVIEW, and VERIFICATION; they do not require another
queue, database, workflow, or ticket system.

## Bind a verdict to what was actually reviewed

Record the candidate commit and dirty-content hash (or artifact content hash),
acceptance contract ID/version/hash, reviewed tasks/criteria, and relevant dependency
versions. Each check records its actual command/procedure, runtime/configuration,
fixtures, execution time, result, and durable evidence reference/hash. Record
reviewer identity and any independence limitation. UNRUN or inaccessible evidence
cannot become PASS through a plausible summary.

Before transition/delivery, compare current identity and scope with the record.
A code, dirty artifact, contract, relevant dependency/configuration, fixture, or
observed-environment change invalidates affected evidence and approval. Preserve
old attempts as superseded history, identify the changed scope, rerun affected
checks, and issue a new verdict. Unaffected evidence may be reused only with an
explicit scope/impact justification recorded in the new verdict. A passing check
on one candidate does not establish that a different candidate passed.

## Make assumptions accountable

The SPEC ledger gives each assumption a stable ID, affected task/criterion IDs,
decision owner, consequence/reversibility, provisional status, decision deadline
and latest safe point, and approval/decision evidence tied to a contract version.
During decomposition, replace pending task mappings with actual task IDs before
dispatch. Link assumption IDs in task cards so rejection can be traced downstream.

Within the existing authorized contract, batch low-risk reversible implementation
choices at milestones; record their owner and rollback boundary. An unresolved
consequential choice must be decided before dependent merge/release or any other
effect that would make reversal unsafe. A milestone date cannot move that boundary
past the effect. Provisional status, silence, or a timer expiring is not consent.

On rejection, material change, or expiry at that boundary: block affected tasks
and transitive dependents, mark their acceptance and derived evidence stale,
revise the plan/contract as needed, and reverify before restoring approval. Keep
unaffected tasks eligible under their own evidence/authority. Do not erase rejected
assumptions or rewrite old test reports as though they used the new decision.

## Close the finding handoff

Carry stable finding IDs across review rounds. Record severity, source location,
disposition, decision owner/rationale, affected dependencies, and the receiving
follow-up task when warranted. BMad's orchestrator owns accept/defer/decline and
deduplication; a reviewer or implementer proposes changes, not backlog authority.
Use an existing canonical task for a duplicate and retain the duplicate-of link.
A small finding can be addressed in the current task; a declined suggestion needs
rationale, not an invented ticket.

For an accepted follow-up, record a receiving owner, acceptance checks, and an
explicit dependency/gate boundary. Deferral or creation of a task does not close
the defect. The originating record points to the receiving task; that task points
back to the finding. Once fixed, link the changed candidate and verified closure
evidence back to both. Failed or missing closure evidence keeps it open. A declined
or duplicate finding may complete triage with rationale/canonical linkage; do not
report that as a repaired defect. A genuinely nonblocking deferred finding need
not prevent the current task from completing, but cannot silently lose its owner.

## Transition challenges

| Scenario | Required decision | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Commit A approved; code changes to B | Supersede A's approval for B; recheck affected scope and issue B verdict | Reuse green status because branch/PR is unchanged | Candidate identity absent |
| Commit unchanged; dirty artifact changes | Content hash changes invalidate affected approval | Treat equal commit SHA as equal candidate | Dirty state not identified |
| Contract or execution environment changes | Reconcile new scope, rerun affected checks, record justified reuse | Carry PASS into a different contract/environment without assessment | No contract/environment binding |
| Provisional A-1 rejected; T-2 depends on T-1 which uses A-1 | Stale T-1/T-2 acceptance and evidence; block their effects; preserve unrelated T-3 | Keep old green results because tests ran before rejection | No task/assumption mapping |
| Low-risk reversible choice meets an existing milestone policy | Batch review within recorded authority and rollback boundary | Turn every routine choice into a new approval gate | No authority/reversibility record |
| Consequential assumption's milestone is after a proposed merge | Obtain decision before merge; block dependent effects until then | Merge first and ask at milestone | No latest safe point |
| F-1 accepted into T-9; T-9 created but not verified | Link owner/dependency both ways; keep F-1 open until closure evidence | Mark F-1 resolved merely because T-9 exists | No receiving task or evidence |
| Duplicate F-2 / canonical F-1; style preference F-3 declined | Record dedup/decline decisions and rationale without extra tickets | Open a ticket for every suggestion or silently drop findings | No authoritative disposition |

These are authored regression challenges, not evidence of runtime enforcement or
measured agent quality. Portable eval cases in the three skills exercise these
behaviors; schema validation is structural, and semantic judgments still need
review. For runtime state integrity, use [harness engineering's state contract](../../harness-engineering/references/context-and-state.md)
and [acceptance contract](../../harness-engineering/templates/acceptance-contract.md).
BMad's [review routing](../../bmad/references/review-and-failure-routing.md) owns
orchestrator handoff decisions.

## Public design examples

The [GlassFlow project walkthrough](https://docs.glassflow.ai/tares/software-factory/a-project-end-to-end)
and [release notes](https://docs.glassflow.ai/tares/reference/release-notes)
illustrate assumption batching, follow-up work, and revision-tagged reviews.
They are vendor examples, not evidence of delivery quality. The authority and
pre-effect decision boundaries above remain governed by the project's contract.
