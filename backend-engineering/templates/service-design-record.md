# Service Design Record

Fill this record when designing or restructuring a backend service, before
implementation begins. Keep it in the repository next to the service code so
reviewers and future maintainers can see the decisions that shaped the
architecture.

## Context

- Service name: `[fill: service name]`
- Owner team: `[fill: owning team]`
- Problem being solved: `[fill: what user or system problem does this service address]`
- Consumers: `[fill: which services, clients, or teams call this service]`
- Non-functional requirements: `[fill: latency target, throughput, availability, data-retention needs]`

## Service Structure

- Boundary style chosen (layered / hexagonal / clean): `[fill: which structure applies and why]`
- Layers or modules and their responsibility: `[fill: list each layer or module with one line of responsibility]`
- Dependency direction rule: `[fill: e.g. "transport may depend on service, service on persistence interfaces, never the reverse"]`
- Framework and language: `[fill: stack, and what framework-owned vs framework-agnostic code exists]`

## API Surface

| Endpoint / operation | Method | Purpose | Request validation | Success response | Failure response |
|---|---|---|---|---|---|
| `[fill: path or RPC name]` | `[fill: HTTP verb or gRPC method]` | `[fill: purpose]` | `[fill: schema/validation approach]` | `[fill: status + body]` | `[fill: error codes mapped to this operation]` |

## Data Access

- Storage: `[fill: database or store, and why this one]`
- Access pattern: `[fill: repository interface, ORM, raw SQL; batch queries and eager-loading strategy]`
- Transaction boundaries: `[fill: which operations need a transaction and its isolation level]`
- Pagination strategy: `[fill: cursor or offset, ordering key]`

## Error Handling

- Error classification: `[fill: how client vs transient vs permanent errors are distinguished]`
- Error response format: `[fill: shape of the error body, stable error codes, correlation IDs]`
- Retry policy for external dependencies: `[fill: backoff, jitter, max attempts, idempotency keys]`
- Failure fallback: `[fill: what happens when retries are exhausted]`

## Integrations

| External system | Interaction | Failure handling | Idempotency | Backpressure |
|---|---|---|---|---|
| `[fill: system]` | `[fill: sync call, webhook, queue]` | `[fill: retry/circuit breaker policy]` | `[fill: how duplicates are prevented]` | `[fill: queue limit, rate limit, load shedding]` |

## Event Flow

- Domain facts emitted: `[fill: meaningful completed business facts, not property changes]`
- Unit-of-work rule: `[fill: what state and outbox records commit atomically]`
- Outbox relay: `[fill: event identity, publish retry, crash-after-publish handling]`
- Incoming message deduplication: `[fill: consumer identity + event identity, inbox lease/state]`
- Handler idempotency: `[fill: repeated side effects and external-effect strategy]`
- Retry, quarantine, and replay: `[fill: classifications, limits, operator evidence, and stop rules]`

## Coexistence And Authority

- Old and new paths: `[fill: adapters, selector, strangler route, or dual path]`
- Authority by operation/data field: `[fill: exactly one authoritative writer or explain the exception]`
- Comparison evidence: `[fill: shadow/parallel comparison, tolerance, and mismatch action]`
- Handoff condition: `[fill: measurable evidence and owner who can transfer authority]`
- Removal condition: `[fill: callers, queues, old writes, flags, credentials, and recovery evidence]`

## Observability

- Structured logging fields: `[fill: request id, trace id, service, environment]`
- Metrics: `[fill: RED or USE metrics exposed and where]`
- Traces: `[fill: span coverage at service boundaries]`
- Alerts: `[fill: the alert rules tied to this service]`

## Testing Plan

- Unit tests: `[fill: business-logic cases and the fakes used for boundaries]`
- Integration tests: `[fill: API contract tests and how the stack is provisioned]`
- Contract tests: `[fill: consumer contract tests and their provider]`
- Query regression guard: `[fill: query-count assertions or N+1 checks]`

## Alternatives Considered

- Alternative 1: `[fill: option considered]` — rejected because `[fill: reason]`
- Alternative 2: `[fill: option considered]` — rejected because `[fill: reason]`

## Open Questions

- `[fill: any unresolved decision that needs input before implementation]`
