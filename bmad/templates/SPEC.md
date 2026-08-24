---
status: draft
slug: example-change
owner: human
created: YYYY-MM-DD
---

# Example Change

## Why

What outcome are we trying to create, and why does it matter? Name the user or system
that benefits and the cost of not doing it.

## Capabilities

- Capability one — observable behavior the system must have.
- Capability two — with the actor and the trigger for each.

## Constraints

- Technical boundary (stack, integration, compatibility).
- Operational boundary (deployment, support, runbooks).
- Security or privacy boundary (data, access, retention).
- Time, cost, or organizational boundary.

## Non-goals

- Explicitly excluded behavior — say what this change will NOT do.
- Deferred items — name where they are tracked so they do not leak back in.

## Success signal

- Observable acceptance criterion (binary: PASS or FAIL is possible).
- Test or evaluation that demonstrates success.
- Manual observation that confirms the result in the real environment.

## Architecture decisions

- Decision or link to an ADR for each consequential choice.
- Boundaries future agents must preserve.

## Implementation slices

1. Story one — bounded, independently finishable unit.
2. Story two — with its own acceptance criteria.

## Verification

- Tests:
- Manual observations:
- Independent review: (who/what — separate evaluator where risk warrants it)

## Residual risks and deferred work

- Risk:
- Deferred item:

## Status history

- `draft` — created.
- `ready-for-dev` — passed readiness; implementation may start.
- `in-progress` — implementation underway.
- `in-review` — review or triage underway.
- `done` — completed successfully.
- `blocked` — cannot continue safely; routing signal for orchestrator or human.
