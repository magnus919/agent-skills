# Error-Handling Taxonomy

Fill this taxonomy when designing or reviewing error handling for a service.
It makes the service's error behavior explicit, consistent, and reviewable in
one place. Every error path in the code should trace back to a row here.

## Error Classification

| Class | Meaning | Examples | Client-visible? | Recovery strategy |
|---|---|---|---|---|
| Client error | The request is wrong and will not succeed if retried unchanged | `[fill: invalid field, missing resource, conflict]` | Yes — structured 4xx | Fix the request; no retry |
| Transient failure | A dependency or resource was temporarily unavailable | `[fill: timeout, 503, connection reset]` | Sometimes — retryable signal | Retry with backoff and jitter |
| Permanent server failure | The service itself hit an unexpected state | `[fill: coding bug, corrupt state]` | Generic 5xx only | Alert; no automatic retry |

## Error Response Contract

- Response shape: `[fill: JSON/gRPC error structure — code, message, details, correlation id]`
- Stable error codes: `[fill: the enumerated codes clients can match on]`
- Status-code mapping table:

| Condition | HTTP status | Error code | Notes |
|---|---|---|---|
| Validation failed | `[fill: e.g. 400]` | `[fill: e.g. validation_error]` | `[fill: which fields and why]` |
| Resource not found | `[fill: e.g. 404]` | `[fill: code]` | `[fill: when this applies]` |
| State conflict / stale write | `[fill: e.g. 409]` | `[fill: code]` | `[fill: concurrency or idempotency context]` |
| Too many requests | `[fill: e.g. 429]` | `[fill: code]` | `[fill: rate-limit and retry-after header]` |
| Unexpected error | `[fill: e.g. 500]` | `[fill: code]` | `[fill: what is logged vs returned]` |

## Exception Handling Rules

- Where exceptions are caught: `[fill: boundary layers that map exceptions to responses]`
- What is logged at each layer: `[fill: context fields, stack traces only server-side]`
- What is never exposed to clients: `[fill: stack traces, SQL, internal paths, dependency details]`
- Correlation: `[fill: how request/trace IDs are attached to logs and error responses]`

## Retry and Idempotency

| Operation | Idempotency key? | Retry policy | Ambiguity handling |
|---|---|---|---|
| `[fill: operation]` | `[fill: yes/no and where the key comes from]` | `[fill: attempts, backoff, jitter, which statuses are retried]` | `[fill: how a timeout-before-response is resolved, e.g. GET to verify state]` |

## Background Jobs and Queues

- Retry policy per queue: `[fill: max attempts, backoff schedule, retryable error classes]`
- Dead-letter behavior: `[fill: where failed jobs land and who drains them]`
- Poison-message handling: `[fill: how a message that always fails is quarantined]`

## Testing the Error Paths

- Test cases to add: `[fill: one test per mapping row above — request, expected code, expected body]`
- Failure injection: `[fill: how transient failures are simulated in tests (e.g. a stub that returns 503)]`
- Verification: `[fill: how the error contract is asserted (contract tests, schema checks)]`
