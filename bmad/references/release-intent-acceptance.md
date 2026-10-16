# Accept an integrated release against intent

Use when a batch of agent-built changes is ready to demonstrate as a user outcome.
Keep the implementation loop autonomous within its authority while placing human
or accountable domain decisions where ambiguity actually matters. A software
factory can use these checkpoints; a dark-factory design may automate some under
an established policy. Neither label determines fitness for every team or task.

## Establish the release boundary

Reuse the approved intent contract and existing PRD/architecture artifacts. Name
the bounded outcome, explicit non-goals, dependencies, remaining uncertainty,
acceptance owner and available review/recovery budget. Choose a batch that can be
meaningfully demonstrated and corrected within that budget. A universal ticket
count or mandatory full-application plan is not useful.

Define which decisions need a human and which are already delegated. In
[the release acceptance template](../templates/RELEASE-ACCEPTANCE.md), record for
each checkpoint: required evidence, owner, decision policy, allowed next action
and when changes invalidate it. Decomposition, staging integration and production
promotion can have different owners and policies. Existing authorization may
already cover a checkpoint; do not invent repetitive approvals. Complexity and
consequence are separate: a tiny access-control change still needs appropriate
security evidence. Promotion authority remains explicit.

## Demonstrate the combined outcome

1. Identify the integrated candidate/content hash, environment/configuration and
   contract version. Verify these match the evidence being reviewed.
2. Demonstrate the release's real user journeys and important cross-story seams.
   Review behavior and maintainability separately through spec-driven-development's
   factory review lanes; QA owns the checks and holdout exposure record.
3. Ask the acceptance owner to assess whether observed behavior serves the agreed
   intent. Green tests alone do not resolve an unstated product decision. Record
   any required human observation; do not invent a sign-off from silence.
4. Classify mismatches using the table below. Create or update authorized work with
   stable finding IDs, requirement links, an owner and acceptance checks. Batch
   related feedback when useful without hiding blockers or expanding scope.
5. Reconcile the contract, implement authorized corrections and rerun affected
   integrated checks. Repeat only within the repair budget. Hand the resulting
   evidence and decision to release-engineering for promotion/rollback mechanics.

## Route the mismatch before fixing it

| Observation | Classification | Next action |
|---|---|---|
| Contract requires persistent saved filters; reload loses them | Implementation defect | Repair under the current contract and verify persistence |
| Contract says "team visibility" but the owner meant selected teams | Ambiguous intent | Owner resolves scope/privacy meaning; version the contract before dependent implementation |
| Accepted release explicitly excludes exports; demo prompts a CSV request | New scope | Record a separate proposed increment; do not silently include it in current repairs |
| Requirement is met but three stories duplicate the same policy | Engineering defect | Review maintainability consequence and repair under an owned criterion |
| Only individual PR checks exist; integrated journey was not run | Missing evidence | Obtain candidate-bound integration evidence; do not claim acceptance |

An authorized contract correction supersedes affected approvals and test oracles.
Preserve the old decision and failure history; do not retroactively redefine a
failure as success. If scope or authority cannot be resolved, block dependent
promotion and continue only unaffected authorized work.

## Completion

Finish with accept / rework / investigate, current evidence, unresolved conditions,
and an explicit next-action owner. Acceptance of a demo does not grant deployment
authority, prove production health or replace release-engineering's rollout controls.
Stop at the repair/time limit or unresolved consequential intent; never run more
coding loops to compensate for a missing decision.

## Source and limits

Cole Medin describes [bounded release scope, 5:47](https://www.youtube.com/watch?v=GQatuTWSRqY&t=347s)
and [staging feedback, 17:40](https://www.youtube.com/watch?v=GQatuTWSRqY&t=1060s)
in his 16 October 2026 account. These are practitioner observations, not proof
that dark factories fail generally. The checkpoint and mismatch procedures are
our synthesis for the existing BMad intent/authority protocol.
