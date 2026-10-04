# Agent Consumer Interface Review

## Task and Boundary

- Task outcome and observable completion evidence:
- Intended agent/automation and client/runtime/version:
- Human roles in review, exception handling, and authorization:
- Services, authoritative facts, and side effects involved:
- User, tenant, object, action, and credential authority:
- Evidence source: production trace, representative fixture, mock, or proposal:

## Consumer Path

| Step / operation | How the consumer discovers it | Required inputs and where obtained | Output used by next step | Owner / authority | Failure and recovery |
|---|---|---|---|---|---|
| 1. | | | | | |
| 2. | | | | | |

## Contract Review

- [ ] Names and descriptions distinguish purpose, scope, prerequisites, and side effects.
- [ ] Discovery fits the actual catalog and deployed client; any search/deferred layer has evidence of need.
- [ ] Every cross-operation identifier has a stated namespace, scope, and supported mapping.
- [ ] Errors distinguish different recovery paths and state retry safety without exposing sensitive details.
- [ ] Large results have defaults, bounds, ordering, truncation/continuation semantics, and completeness signals.
- [ ] Large artifacts have a usable authorized retrieval path with media type and lifecycle/size behavior.
- [ ] Outputs contain the documented inputs required by follow-up operations or an explicit translation step.
- [ ] Authorization context, side effects, idempotency, partial outcomes, and accepted-versus-complete states are explicit.
- [ ] Human review or approval gates are stated for consequential actions; the API contract does not assume the model is authority.

## Evidence and Findings

- Representative successful task trace and outcome:
- Invalid/missing prerequisite trace:
- Denied-authority trace:
- Bounded-result and continuation trace:
- Artifact retrieval trace:
- Retry/partial/ambiguous-completion trace:
- Failures, severity, owner, and required decision:
- Remaining unknowns and evidence needed:
- Verdict: pass / conditional / blocked / not exercised
