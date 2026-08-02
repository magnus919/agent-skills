# Verification and Closure

Closure of an incident-learning follow-up item requires evidence that the intended change occurred and had the intended effect. Ticket creation is a process step — not closure. This reference defines the closure standard and the evidence required at each stage.

## The closure standard

A follow-up item is closed when three conditions are met:

1. **Implementation evidence:** The follow-up work was implemented. A code change was merged, a monitor was deployed, an eval case was added to the dataset, a requirement was updated and approved, a policy was enacted.
2. **Verification evidence:** The implementation was verified against the intended change. The code change passes tests, the monitor fires under the incident condition, the eval case catches the failure mode, the policy is audited.
3. **Effect evidence:** The intended effect was observed — or a revised hypothesis was recorded. The failure mode no longer occurs, the alert fires before the condition becomes critical, the eval case prevents regression. If the intended effect cannot yet be observed (e.g., the condition has not recurred), the follow-up remains open with a re-evaluation date.

## What is NOT closure

The following are explicitly NOT sufficient for closure:

- **Ticket creation.** Creating a Jira ticket, Linear issue, GitHub issue, or any task-tracker item is a process action — not evidence of change. A ticket is a container for follow-up work, not the work itself.
- **Ticket assignment.** Assigning a ticket to an owner is a delegation action — not evidence of change.
- **Ticket status transition.** Moving a ticket to "Done," "Resolved," or "Closed" in a tracker is a workflow action — not evidence of change. The tracker status and the incident-learning closure are independent; one can be "Done" while the other remains "Not Verified."
- **Acceptance in a sprint review.** A demo or sprint review acceptance is a process checkpoint — not verification that the change prevents the incident from recurring.
- **"We'll handle it in the next cycle."** Deferral is not closure. A deferred follow-up item remains open with a revised target date and a documented reason for deferral.
- **"The team discussed it and decided it's not a priority."** A deprioritization decision is a rejection of the follow-up item — not closure. Rejected items must be recorded with a rejection reason and an explicit acceptance of the residual risk.

## The closure record

Each follow-up item has a verification and closure record with these fields:

| Field | Description | Required for closure |
|---|---|---|
| **Follow-up ID** | Link to the follow-up work map item | Yes |
| **Implementation evidence** | What was implemented, with a reference (commit SHA, config change ID, document URL) | Yes |
| **Implementation date** | When the implementation was completed | Yes |
| **Verification evidence** | How the implementation was verified against the intended change, with a reference (test run, monitor fire log, eval result) | Yes |
| **Verification date** | When the verification was completed | Yes |
| **Effect evidence** | Evidence that the intended effect was observed, or a plan for when it will be observable | Yes (or a re-evaluation date if not yet observable) |
| **Closure authority** | Who approved the closure | Yes |
| **Closure date** | When the follow-up was closed | Yes |
| **Revised hypothesis** | If the effect was not as expected, what was learned and what follow-up replaces this one | If applicable |

## Closure states

| State | Meaning | Evidence required |
|---|---|---|
| **Verified closed** | All three conditions met (implementation, verification, effect) | Full closure record with all required fields |
| **Verified closed — effect pending** | Implementation and verification complete; effect not yet observable (condition has not recurred) | Implementation and verification evidence; re-evaluation date; rationale for why effect cannot yet be observed |
| **Rejected** | Follow-up work was evaluated and intentionally not pursued | Rejection reason; acceptance of residual risk; rejection authority; rejection date |
| **Superseded** | Follow-up work was replaced by a different follow-up that addresses the same finding | Link to the superseding follow-up item; reason for replacement |
| **Open** | Follow-up work is in progress or not yet started | Current status; owner; target date |

## Closure verification per domain

| Domain | Implementation evidence | Verification evidence | Effect evidence |
|---|---|---|---|
| **Product** | Updated requirement document, specification, or design decision record | Review approval, specification acceptance | The requirement is referenced in implementation; the gap does not recur in subsequent incidents |
| **Code** | Merged commit or PR | Tests pass; the specific failure mode is reproduced and confirmed fixed | The failure mode does not recur in production |
| **Tests** | Test added to the test suite | Test passes; test fails when the original failure condition is reintroduced (mutation verification) | The test catches a regression or near-miss in a subsequent change |
| **Evals** | Eval case added to the dataset | Eval case fails against pre-fix system, passes against post-fix system | The eval case catches a regression in a subsequent model or agent version |
| **Operations** | Monitor, alert, or runbook deployed | Monitor fires under the incident condition (fault injection or replay); runbook is exercised | The alert fires before user impact in a subsequent occurrence; the runbook produces the expected outcome |
| **Governance** | Policy, access control, or approval gate enacted | The restricted action is attempted and blocked; the approval gate is exercised | The governance change prevents a subsequent incident in the same category |

## Rejecting a follow-up item

A follow-up item may be rejected — intentionally not pursued. Rejection is a legitimate outcome when:

- The cost of the follow-up outweighs the risk it addresses.
- The follow-up would introduce more risk than it mitigates.
- The finding is accepted as a known, tolerated risk.
- A different follow-up addresses the same finding more effectively (record as "superseded," not "rejected").

A rejection is never silent. The rejection must be recorded with:
- **Rejection reason:** Why the follow-up is not being pursued.
- **Residual risk acceptance:** Explicit acknowledgment that the gap remains.
- **Rejection authority:** Who made the rejection decision.
- **Rejection date:** When the decision was made.

A rejected follow-up item is closed — it does not remain open indefinitely. The rejection is a conscious decision, not a forgotten item.

## Tickets alone are not sufficient

This is the foundational closure rule:

> Creating a ticket, task, or story is an action — not an outcome. Closure requires evidence that the intended change was implemented, verified, and had the intended effect. Tickets alone are not sufficient; a closure record must reference evidence of the implemented change.

This rule is enforced structurally: the closure record template has no field for "ticket ID" as a substitute for implementation, verification, or effect evidence. A ticket may be referenced as supplementary context, but it does not satisfy any of the three evidence requirements.
