# NFR Encoding for AI Specs

Non-functional requirements (NFRs) are the hardest spec dimension for AI code generation. AI agents naturally optimize for functional correctness; NFRs are often the last thing they consider. This guide covers how to encode NFRs in machine-readable formats so AI agents treat them as first-class constraints.

## The Problem

AI agents, given a behavioral spec, will produce working code that:
- Works correctly for 1 user but fails at 1000
- Handles the happy path but logs nothing
- Is functionally correct but has a SQL injection vulnerability
- Uses the correct algorithm but is 100x slower than required

These are NFR failures. The agent didn't know the constraints because they weren't specified in a machine-actionable way.

## General Pattern

Every NFR must include three things:

1. **Dimension** — what is being measured (latency, availability, concurrency, etc.)
2. **Threshold** — the specific, measurable boundary
3. **Verification method** — how compliance is checked

| Dimension | Threshold Format | Example |
|-----------|-----------------|---------|
| Latency | `X units at Y percentile under Z load` | `200ms at P95 under 1000 concurrent users` |
| Throughput | `X operations per Y time unit` | `5000 requests/second sustained` |
| Availability | `X% over Y time period` | `99.9% uptime measured monthly` |
| Concurrency | `X simultaneous users/connections` | `5000 simultaneous WebSocket connections` |
| Storage | `X units per Y` | `1TB data, 30-day retention` |
| Recovery | `X time to recover from Y failure` | `<5 min RTO for AZ failure` |
| Accuracy | `X% correct under Y conditions` | `99.5% classification accuracy on test set` |

## Encoding NFRs in SPEC.md

Within the SPEC.md template, NFRs are specified as a table:

```markdown
## Non-Functional Requirements

| ID | Requirement | Threshold | Verification Method |
|----|-------------|-----------|-------------------|
| NFR-001 | API response time | <200ms at P95 under 1000 concurrent requests | k6 load test with p95 assertion |
| NFR-002 | Uptime | 99.9% availability | Prometheus alerting + SLO tracking |
| NFR-003 | Auth security | OWASP ASVS Level 2 | Semgrep SAST + dependency audit |
| NFR-004 | Write audit log | All writes to user data produce audit event | Audit log must exist and be immutable |
| NFR-005 | Max memory per request | <256MB heap | Memory profiling in staging |
```

The key insight: **each NFR must produce a PASS/FAIL verdict**, just like behavioral ACs. If you can't write a test for it, it's not an NFR — it's a hope.

## NFR by Category

### Performance

| Dimension | How to Specify | Common Pitfall |
|-----------|---------------|----------------|
| Latency | Xms at Y percentile | Forgetting load conditions — "fast" is meaningless without concurrency |
| Throughput | X operations/period | Mixing peak vs sustained — specify both |
| Resource usage | X CPU, X memory, X storage | Not specifying units or measurement method |

**Example:** "The search endpoint must respond within 500ms at P99 under 2000 req/s sustained load, measured by k6 on the staging environment. The API gateway must queue or reject requests exceeding this threshold, not crash."

### Security

Security NFRs are unique: specifying them in the spec is itself a security best practice (shift-left security).

| Concern | How to Specify |
|---------|---------------|
| Authentication | AuthN method (OAuth2, SAML, API keys), token format, expiry, scopes |
| Authorization | AuthZ model (RBAC, ABAC), permission model, admin boundaries |
| Input validation | Validation rules per field, injection prevention |
| Secrets | Encryption at rest, in transit; secrets management approach |

**Example:** "All API endpoints must validate JWTs from the OAuth2 provider before processing. Scopes are checked per RBAC matrix in docs/rbac.md. Input validation uses a whitelist approach — reject known-bad patterns at the API gateway level."

### Observability

| Concern | How to Specify |
|---------|---------------|
| Logging | What events produce logs, log format (structured JSON), retention |
| Metrics | What metrics are exposed (RED metrics for services: Rate, Errors, Duration) |
| Tracing | Distributed tracing headers, span context propagation |

**Example:** "Every API request produces a structured JSON log entry with: timestamp, request_id, method, path, status_code, duration_ms, user_id. The /metrics endpoint exposes Prometheus-formatted counters for request count, error count, and P50/P95/P99 latency."

### Reliability

| Concern | How to Specify |
|---------|---------------|
| Fault tolerance | What failures the system survives without data loss |
| Retry strategy | Backoff algorithm, max retries, circuit breaker thresholds |
| Graceful degradation | What features degrade and how |

**Example:** "The checkout service must survive any single downstream dependency failure without losing orders. Payments may queue for retry, but user session and cart data must persist. Circuit breakers open after 5 failures in 30 seconds."

## Encoding NFRs for Autonomous Agents

For fully autonomous AI agents, NFRs need additional structure:

```markdown
### NFR Constraints for Implementation Agent

The following constraints MUST be reflected in code architecture and dependencies, not just tested after implementation:

1. **Database:** Use PostgreSQL 16. Read replicas for reporting queries. Connection pooling via PgBouncer.
2. **Caching:** Redis for session cache (TTL: 30 min). No caching of user financial data.
3. **Async:** Background jobs via RabbitMQ. No long-running processes in request handlers.
4. **Observability:** OpenTelemetry instrumentation in every service. Export traces to Tempo.

Implementation choices that violate these constraints without explicit spec amendment will be rejected at Gate 3.
```

This gives the agent architectural guardrails before it makes technology choices that are expensive to undo.
