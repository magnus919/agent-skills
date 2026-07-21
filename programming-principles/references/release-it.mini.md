# OBEY Release It! by Michael T. Nygard

## When to use

Use for services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures, overload, latency, bad data, hostile traffic, and operational mistakes.

## Primary bias to correct

A passing happy path is not production readiness. Design the failure semantics, demand limits, isolation, recovery path, and diagnosis surface before production defines them for you.

## Decision rules

- Assume every dependency, queue, cache, timeout, caller retry, and degraded state can fail in slow, partial, or prolonged ways.
- Prefer designs that fail visibly, limit blast radius, shed load, preserve core service, and make diagnosis possible.
- Treat deployment, operations, security, observability, rollback, and configuration validation as part of the system.
- Put explicit, intentional time limits on outbound calls and waits. No infinite waits.
- Retry only when safe for caller and provider. Bound count and total time. Use backoff or jitter.
- Isolate dependency failures with circuit breakers, fast failure, bulkheads, separate resource pools.
- Design overload behavior explicitly with back pressure, finite queues, demand limits, and load shedding.
- Budget scarce resources explicitly. Release them deterministically. Stream or paginate large payloads.
- Treat external input and responses as untrusted. Validate syntax, shape, business plausibility, semantics.
- Build observability into boundaries: structured context, correlation IDs, latency, throughput, error, saturation, queue depth, breaker state, dependency health.
- Make startup, health checks, migrations, and operational controls fail safely, auditable, stoppable, recoverable.

## Trigger rules

- When adding an outbound call, define timeout, retry eligibility, fallback, validation, and caller-survival behavior.
- When adding a queue, buffer, pool, cache, or background job, define capacity, full behavior, cleanup, and saturation monitoring.
- When a change touches deployment, config, startup, or migrations, make it idempotent and give it rollback.
- When designing API contracts, make failure modes explicit, distinguish retryable from non-retryable.

## Final checklist

- Explicit timeouts and no infinite waits?
- Retries safe, bounded, backed off?
- Failure isolated with breakers, bulkheads, load shedding?
- External input validated before trusted?
- Startups and migrations restartable and observable?
