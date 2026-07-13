# Operations, Failures, And Boundaries

## Mutations And Retries

Separate HTTP method semantics from application behavior. HTTP idempotence describes
the intended effect, not identical responses or the absence of audit/log effects.
For each operation, state preconditions, side effects, retryable outcomes, and the
client's stop conditions.

`Idempotency-Key` is an **expired Internet-Draft** (`draft-ietf-httpapi-idempotency-key-header-07`), not an RFC. If using it, define key scope, request equivalence or fingerprint,
concurrent duplicate handling, retention, result replay or lookup, key reuse conflict,
and the retry boundary. Do not impose a UUID format, retention period, echoed header,
or byte-identical replay unless the interface contract requires it.

Retry only failures and operations marked safe by the contract. Respect `Retry-After`
where applicable, use bounded backoff and jitter appropriate to the workload, and do
not retry permanent errors. Idempotency does not resolve competing updates: use a
version field, conditional request such as `If-Match`, domain conflict rule, or an
explicit serialization model. Explain the consequences of last-write-wins if chosen.

For batches and long-running operations, define acceptance versus completion, operation identity/state, result retrieval, cancellation semantics, per-item and partial outcomes, compensation, and what is observable after an interrupted request.

## Errors And Limits

Use RFC 9457 Problem Details (`application/problem+json`) where it fits the HTTP API.
`instance` identifies a problem occurrence; it is not automatically a correlation ID
or log URL. Define stable type/code, safe human detail, status, retryability,
field-level pointer semantics, and a separately documented correlation mechanism.
Do not expose stack traces, secrets, or object-existence detail that enables enumeration.

Use [../templates/error-taxonomy.md](../templates/error-taxonomy.md) to distinguish a
transport status from an application code. Not every interface needs Problem Details
or the same 400/422 boundary.

Rate/resource limits are part of the operational contract: state scope, cost model, units, quota versus rate behavior, reset/retry semantics, and observability. The IETF RateLimit fields work is an Internet-Draft in progress; do not call old `RateLimit-Limit`/`RateLimit-Remaining`/`RateLimit-Reset` headers an RFC standard. Identify any headers as vendor-defined unless the deployed contract says otherwise.

## Authority Boundary

Every protected operation needs server-side authorization over subject, action, object, tenant, and relevant context. Authentication does not authorize access. Document the authentication scheme and credential transport, token/credential audience and lifecycle assumptions, required scopes or permissions, and denied behavior without revealing sensitive distinctions. Scope names describe delegated capability but do not replace object-level or state-dependent checks; do not invent a universal `read:`/`write:` naming convention.

Document output minimization, field-level disclosure, mass-assignment protection, and whether `401`, `403`, or a concealed not-found response is appropriate to the threat model and consumer contract. Load [secure-software-engineering](../../secure-software-engineering/SKILL.md) for threat modeling, credential and secret lifecycle, tenant isolation, mass assignment, URL/file handling, output minimization, or abuse controls.
