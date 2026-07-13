# Contract Review

## Scope

- Artifact, version, deployment boundary, and reviewers:
- Consumer jobs and domain/authority assumptions reviewed:

## Review Checklist

- [ ] Interface style fits interaction direction, authority, and failure model.
- [ ] For HTTP, method, status, representation, content negotiation, cache, conditional, and asynchronous-completion semantics are explicit.
- [ ] OpenAPI/AsyncAPI/GraphQL/RPC artifacts pin the selected version or dialect; references, security, examples, negative examples, and generated-client behavior are validated where applicable.
- [ ] Schema semantics cover requiredness, null/absence, defaults, enums/unions, time, and units.
- [ ] Collection ordering, filters, pagination mutation behavior, and limits are explicit where relevant.
- [ ] Mutations define preconditions, idempotency/retry boundaries, concurrency, and partial completion.
- [ ] Errors are machine-actionable, safe, and distinguish transport from application meaning.
- [ ] Authentication, credential transport, scopes/permissions, and server-side subject/action/object/tenant authorization are documented; security depth is routed appropriately.
- [ ] Event/webhook/stream delivery, ordering, duplicate, gap, replay, and signature boundaries are explicit where relevant.
- [ ] Consumer-specific compatibility evidence covers strict and generated clients.
- [ ] Deprecation/migration has ownership, telemetry, communication, criteria, and rollback where relevant.
- [ ] Provider, consumer, negative, compatibility, and deployed-boundary tests have evidence or an explicit gap.

## Verdict

- Pass, conditional, blocked, or not applicable:
- Evidence and reproducible locations:
- Gaps, owner, and required decision:
