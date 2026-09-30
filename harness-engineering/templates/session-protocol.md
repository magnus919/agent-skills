# Initializer and worker session protocol

## Initializer exit contract

- Outcome/acceptance owner and unresolved decisions:
- Actual startup, dependency readiness, and verification paths:
- Authoritative task/state store (avoid duplicates):
- Bounded tasks, dependencies, owners, evidence:
- Authority, budget, escalation and rollback:
- Fresh-session answers with source references:

## Worker startup

- Workspace, identity, revision, dirty changes:
- Applicable policies and accepted contract:
- Active task/lease and incomplete effects to reconcile:
- Readiness observations and selected context:
- Bounded action and stop conditions:

## Worker exit

- Verified, failed, and unobserved behavior separately:
- Candidate identity and check evidence:
- Partial effects/checkpoints/resources and owners:
- Blockers, next action, and recovery:
- Handoff publication and acknowledgement:

A failed check does not require deleting useful work. Preserve it with an explicit
incomplete status and a recoverable next step.
