---
checkpoint: final
date: YYYY-MM-DD
---

# Review Checkpoint

The final human checkpoint. Organize the review around intent and risk first, then
provide file and line references. Do not ask a human to review an unexplained file
list.

## Original intent (one sentence)

What we set out to accomplish, from the intent contract or spec.

## Implemented behavior

What the system now does, stated in observable terms.

## Files and systems affected

- Files changed.
- Systems or services touched.
- External effects (deployments, data, credentials) — if any.

## Highest-risk decisions

- The decisions with the largest blast radius, and why they were made.
- Alternatives considered (briefly) and why they were rejected.

## Review binding

- Candidate commit/content hash (include dirty content):
- Acceptance contract ID/version/hash and reviewed tasks/criteria:
- Verifier, issued-at time, and independence limitations:
- Validity: current / superseded / withdrawn; replacement record:

Relevant candidate, contract, dependency/configuration, fixture, or environment
changes supersede affected approval/evidence. Reconcile identity before acceptance
or delivery; rerun affected checks and issue a current verdict. Record why reused
unaffected evidence remains applicable.

## Verification performed

- Executed checks/observations: command or procedure, candidate/contract, environment/fixtures, timestamp, actual result, and evidence reference/hash. Mark unrun checks explicitly.
- Manual observations.
- Independent review performed (who/what) or explicitly skipped and why.

## Review findings and disposition

| Stable finding ID / location | Severity | Disposition | Orchestrator decision / rationale | Follow-up task or duplicate-of | Owner / dependencies / gate boundary | Closure evidence |
|---|---|---|---|---|---|---|
| F-001 | <severity> | proposed / accepted / deferred / declined / duplicate / resolved | <authority and record> | <receiving task if warranted; canonical finding for duplicates> | <owner; affected tasks; latest safe gate> | <fix candidate and verifying report, or triage rationale/canonical link> |

Keep IDs across rounds. The orchestrator owns acceptance, deferral, rejection,
and deduplication; recommendations do not create backlog authority. Do not open
a task for every suggestion. Accepted follow-up work needs receiving ownership
and acceptance checks linked back to this finding. Deferral or task creation is
not defect closure. Close an accepted finding only with verified closure evidence
on the fix candidate, and link that result back to this record. Declined or
duplicate dispositions complete triage with rationale/linkage, not a repair claim.

## Residual risks and deferred work

- Risk:
- Deferred item (and where it is tracked):

## Decision

- [ ] **Accept** — result is fit for purpose.
- [ ] **Rework** — specific findings must be addressed.
- [ ] **Investigate** — evidence is insufficient; more work needed before a call.
