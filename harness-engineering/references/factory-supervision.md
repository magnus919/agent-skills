# Reconcile a batch of factory work

Load when individually bounded workers share a release and local success can hide
stale dependencies, abandoned ownership or broken integration. Reuse the existing
state owner and integration process. A supervisor is a responsibility, not a
requirement to add another model or polling service.

## Define the batch before dispatch

Record accepted scope/contract version, task dependency graph, shared resources,
interface versions, worker claims/leases, candidate identities and integration
owner. Set the supervisor's permitted actions, total repair/time/cost budget,
no-progress limit, escalation recipient and unreachable-recipient behavior.
Choose event triggers or a bounded cadence appropriate to recovery latency; the
video's hours-based schedule is an example, not a default.

A supervisor may act only within existing authorization. This reference does not
authorize delegation, scheduling, merge, deployment, policy edits or messaging.

## Reconciliation pass

1. Read authoritative task, repository, CI and runtime state, with revision/time.
   Treat labels and worker reports as discovery, not proof of ownership or success.
2. Reconcile each claim against its actual lease and observed effects. Before
   reassigning an expired worker, fence stale writes and determine whether its PR,
   commit or external action already exists. Preserve pending/unknown effects.
3. Compare current prerequisite/interface versions with each worker's input
   snapshot. Mark dependent work stale when a relevant contract changed; include
   transitive dependents. Pause affected integration until replan/reverification.
4. Check budgets and convergence across attempts, including replacements and
   supervisor repairs. Reassignment must not reset the batch's exhausted budget.
5. Choose an authorized action: continue unaffected work; retry a transient failure;
   replan dependent work; request a bounded repair; or escalate intent/authority gaps.
   Acquire ownership before taking over; never race the live worker or silently
   expand the release. Unknown state stays unresolved.
6. Inspect combined behavior and architecture on the integrated candidate. Invalidate
   affected evidence after conflict resolution, dependency or environment changes;
   rerun affected checks. Preserve justified reuse of unaffected results explicitly.
7. Write one durable reconciliation record with source revisions, actions, evidence,
   unresolved dependencies and the next decision owner. Notifications carry the
   actionable gap and evidence, within existing communication authorization.

Use [the batch record](../templates/factory-batch-record.md). Stop a pass when each
observed discrepancy has an owned disposition. Stop autonomous repair when the
budget/no-progress bound is reached or authority/intent is missing; preserve state
and escalate. A pass with unknown evidence is not a release acceptance verdict.

## Protected control artifacts

The accepted mission, engineering rules, permission policy, evaluator fixtures and
required gate configuration must not be editable by the workers whose behavior
they govern. Record exact protected resources, owners, revisions and enforcement:
for example worker-excluded write paths and credentials, plus a trusted integration
check using a baseline outside the candidate's control. Apply equivalent controls
to supervisor repairs. Read protection is additionally needed for withheld cases.

A path list in a prompt is not enforcement. A CI check that the same worker can
edit or bypass is not sufficient by itself. Exercise a prohibited change in an
isolated test and verify denial/no effect or a trusted rejection before integration.
If enforcement cannot be checked, report it as unverified. Hash comparison detects
change but cannot establish access isolation on its own.

Workers can propose a rule revision through a separately authorized owner workflow.
Review the reason, scope and rollback; version an accepted revision and re-evaluate
pending work/evidence against it. Do not weaken a test, widen permissions or edit
mission constraints merely to make the current batch green. This does not prohibit
legitimate user-authorized maintenance of those files in a separately scoped task.

## Worked dependency-drift recovery

Illustrative batch: A publishes invoice status v1; B implements export against v1;
C implements notifications. All three task branches pass independently. During
integration A changes status semantics to v2. The integrated export now omits paid
invoices; notifications introduce a competing status mapping.

The supervisor records v1→v2, marks B and any other consumers' evidence stale,
and asks the contract owner whether v2 is intended. If approved, replan consumers
against v2, inspect the shared mapping and run the combined invoice/export/
notification journey on the final integrated hash. If v2 was accidental, repair A
under the accepted v1 contract and still recheck the combined candidate. Unaffected
work can continue. A late v1 worker cannot publish over current work; its expired
lease is fenced. Neither three green task reports nor a manager's confidence
establishes release acceptance.

## Ownership and source

Route test/oracle design to qa-methodology, review lane aggregation to
spec-driven-development, intent repair to bmad, and promotion/rollback to
release-engineering. Runtime production operations remain with agent-production-operations.

Motivation: Cole Medin's [manager agent, 15:32](https://www.youtube.com/watch?v=GQatuTWSRqY&t=932s)
and [protected files, 16:35](https://www.youtube.com/watch?v=GQatuTWSRqY&t=995s),
16 October 2026. His account reports practical benefit; the recovery and enforcement
procedure here is catalog synthesis, not a reproduced benchmark or a deployed runtime.
