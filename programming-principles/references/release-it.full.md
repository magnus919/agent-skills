# OBEY Release It! by Michael T. Nygard

## Purpose

This repository follows **Release It!** in the sense of Michael Nygard:
design and implement software that survives production reality - failures, overload, latency, partial outages, bad data, hostile traffic, and operational mistakes.

All code generation, edits, and reviews must optimize for:
- production readiness
- failure isolation
- graceful degradation
- back pressure and overload protection
- timeouts and retries with discipline
- observability
- survivability over ideal-path elegance

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

Assume production will be messy.

When uncertain, prefer the design that:
1. fails visibly instead of hanging silently
2. limits blast radius instead of maximizing coupling
3. sheds load instead of collapsing
4. preserves core service under stress
5. makes diagnosis possible

Do not design only for the happy path.

---

## Stability Mindset Rules

1. Every dependency can be slow, unavailable, or wrong.
2. Every queue can fill.
3. Every cache can miss or stampede.
4. Every timeout can cascade.
5. Every caller can retry badly.
6. Every “temporary” degraded state can become normal for hours.

The code must assume these conditions, not merely tolerate them by accident.

---

## Production Readiness and Release Risk Rules

1. Do not treat QA success or feature completion as proof of production readiness.
2. Design deployment, operations, security, observability, and rollback as part of the system.
3. Reduce release risk through small exposure steps, compatibility discipline, and reversible changes.
4. Make version, build, configuration, dependency, and runtime state visible enough to diagnose a live instance.
5. Validate critical configuration at startup and make configuration changes auditable and reversible.

---

## Dependency Protection Rules

### Timeouts Are Mandatory
1. Outbound calls must have explicit time limits.
2. Timeouts must be chosen intentionally, not left to library defaults.
3. Different dependencies may need different timeout budgets.
4. Infinite waits are forbidden.

### Retries Must Be Disciplined
1. Retry only where repeated attempts are safe for the caller and provider.
2. Bound retry count and total retry time.
3. Add jitter/backoff to avoid synchronized retry storms.
4. Do not retry validation errors or permanent failures.

### Circuit Breakers and Fast Failure
1. Protect unstable dependencies with fast-fail mechanisms when appropriate.
2. When a dependency is clearly unhealthy, stop flooding it.
3. Surface fallback or degraded mode explicitly.

### Bulkheads and Isolation
1. Separate resource pools for unrelated workloads where failure isolation matters.
2. One failing integration must not consume all threads, connections, or worker capacity.
3. Isolate slow or risky work from core request paths.

Anti-patterns (MUST NOT):
- nested retries at multiple layers
- no timeout around remote calls
- one shared pool for all outbound work
- treating all failures as transient

---

## Load and Capacity Rules

### Back Pressure
1. The system must have a strategy for overload.
2. Reject, defer, queue, or degrade intentionally.
3. Unbounded acceptance of work is forbidden.

### Queues
1. Queues are buffers, not infinite storage.
2. Monitor queue length, age, throughput, and failure rate.
3. Know what happens when producers outpace consumers.
4. Define dead-letter or poison-message handling explicitly.

### Demand Control
1. Protect scarce resources with limits.
2. Prefer early rejection over total collapse.
3. Reserve capacity for critical traffic when appropriate.

### Load Shedding
1. Define which work is optional under stress.
2. Shed low-value work first.
3. Preserve core functions whenever possible.

### Additional Stability Patterns
- USE Steady State design so routine operation does not require manual cleanup, unbounded growth, or periodic rescue.
- USE Fail Fast when continuing would hold scarce resources or hide an unrecoverable dependency problem.
- USE Let It Crash only when supervisors, isolation, and restart behavior make crashing safer than limping.
- USE Handshaking between instances, load balancers, and dependencies so traffic reaches only ready components.
- USE Decoupling Middleware when it reduces direct failure propagation; monitor the middleware as a dependency.
- USE Governors to cap expensive behavior before it harms the rest of the system.

Anti-patterns (MUST NOT):
- unbounded queues
- accepting work with no plan to finish it
- letting best-effort tasks crowd out critical work

---

## Runtime State and Restart Safety Rules

1. Make runtime state visible through logs, metrics, health endpoints, administrative interfaces, and diagnostic data.
2. Validate external responses by status, content type, shape, and semantics before trusting them.
3. Make deployment and operational automation idempotent or restartable where practical.
4. Avoid partial deployment or migration steps without a rollback or roll-forward path.
5. Validate operational assumptions at system boundaries.

### Restartable Automation
Required when:
- deployments touch many machines
- scripts may be rerun after partial failure
- migrations run while old and new application versions coexist
- operational procedures must be repeatable under release pressure

Anti-patterns (MUST NOT):
- one-shot deployment scripts that cannot safely resume
- manual repair steps with no recorded state
- side effects before a durable release checkpoint with no recovery plan

---

## Resource Management Rules

1. Explicitly budget scarce resources:
   - threads
   - DB connections
   - sockets
   - file descriptors
   - memory
   - CPU-intensive worker slots
2. Release resources deterministically.
3. Do not hold locks or expensive connections across slow remote calls.
4. Use streaming or pagination for large payloads where appropriate.
5. Guard memory-heavy operations.

Anti-patterns (MUST NOT):
- one huge in-memory batch by default
- blocking worker threads on slow I/O when a better model exists
- connection pools sized by guess and then ignored

---

## Data Boundary Rules

1. Treat all external input as untrusted.
2. Validate syntax, shape, and business plausibility separately where needed.
3. Avoid letting malformed data poison caches, queues, or downstream systems.
4. Normalize and sanitize data once at the right boundary.
5. Keep parsing errors and domain rule violations distinct.

---

## Operational Visibility Rules

### Observability Is Part of the Design
1. Emit meaningful logs at boundaries and failure points.
2. Include identifiers needed for correlation and diagnosis.
3. Measure latency, throughput, error rate, saturation, queue depth, and retry behavior.
4. Expose health information that reflects real dependency state.

### Logging
1. Log structured context, not just prose.
2. Log failures with the dependency, operation, and outcome.
3. Do not log secrets.
4. Avoid log spam loops under retry storms.

### Metrics
At minimum, capture:
- request rate
- success/failure counts
- dependency latency
- timeout counts
- queue depth
- retry counts
- circuit-breaker state
- saturation signals

Anti-patterns (MUST NOT):
- only logging stack traces without context
- no metrics for slow dependencies
- health checks that always return green despite broken downstreams

---

## Incidents, Capacity, and Runtime Control

1. After incidents, identify the failure chain, missing defenses, detection gaps, and design changes.
2. For performance or capacity incidents, inspect demand, saturation, latency distribution, queue age, dependency behavior, and traffic concentration.
3. Provide administrative interfaces or operational controls only with authorization, auditability, safe defaults, and clear stop mechanisms.
4. Keep process code, scripts, and automation observable enough that operators can see what changed and why.
5. Treat control planes and delivery tooling as production systems when they can affect production.

---

## Deployment and Startup Rules

1. Startup must fail fast on missing critical configuration.
2. Health checks must reflect actual ability to serve.
3. Health checks must not mask deadlocks or stuck subsystems.
4. Avoid expensive or destructive startup work in request-serving processes when possible.
5. Migrations and one-time jobs must be deliberate, observable, and recoverable.

---

## Interconnect, Routing, Security, and Chaos Rules

1. Keep DNS, service discovery, routing, and load balancing health-aware and current.
2. Design interconnects to avoid concentrated demand, hidden single points of failure, and uncontrolled fan-out.
3. Treat hostile traffic, abusive users, and malformed requests as production load cases.
4. Include security in production readiness: secrets, permissions, administrative access, dependency trust, and input handling.
5. Use production tests, launch checks, capacity tests, and game days to validate operational assumptions.
6. Run chaos or disaster simulations only with a hypothesis, limited blast radius, observability, stop condition, and recovery path.
7. Feed findings from chaos and disaster work back into design, operations, and tests.

---

## API and Contract Rules

1. Make failure modes explicit in API contracts where they matter.
2. Return clear retryable vs non-retryable outcomes.
3. Prefer coarse-grained, resilient interactions over fragile chattiness.
4. Use versioning and compatibility discipline for long-lived contracts.
5. Document retry, timeout, version, and compatibility expectations clearly.

---

## Cache Rules

1. Cache is an optimization, not a source of truth unless explicitly designed that way.
2. Plan for cache miss storms, stale data, and cache outages.
3. Avoid dogpiles with request coalescing or appropriate expiry strategies.
4. Define what happens when the cache is unavailable.

Anti-patterns (MUST NOT):
- assuming cache hit rate is always high
- rebuilding the whole cache synchronously on miss
- hiding correctness assumptions inside cache behavior

---

## Scheduled and Background Work Rules

1. Spread scheduled work so demand does not concentrate at the same instant.
2. Do not set all periodic jobs to run on the same obvious clock boundary.
3. Failure and retry policy must be explicit.
4. Retried work must use increasing backoff where synchronized retry pulses would create load.
5. Long-running work needs bounded waits, progress visibility, timeout, and cancellation strategy.

---

## Review Rules

When reviewing code, actively look for:
- outbound calls with no timeout
- retries without backoff, limits, or a clear failure policy
- no backoff or jitter
- unbounded queues or buffers
- shared resource pools with no isolation
- no overload strategy
- no failure visibility
- health checks that say nothing meaningful
- scheduled jobs concentrating load at the same instant
- caches treated as always available

---

## Forbidden Patterns

### Happy-Path Design
- code that assumes dependencies are fast and correct
- no timeout, no retry discipline, no degradation path

### Retry Storms
- retries at every layer
- retries with no increasing backoff or limits
- synchronized retries without jitter

### Collapse by Queue
- unbounded queue growth
- taking work forever even while falling behind
- no poison-message handling

### Silent Failure
- swallowed exceptions
- generic “something went wrong” without context
- missing correlation information

### Blast-Radius Amplification
- one dependency outage consuming all worker threads or DB connections
- shared pools for all risk classes with no isolation

---

## Code Generation Rules

When generating code, default to:
1. explicit timeout for every remote dependency
2. explicit retry policy only where safe
3. restartable deployment and operational automation where practical
4. bounded resources and queues
5. clear failure paths
6. useful diagnostic hooks
7. graceful degradation or fast failure where appropriate

Avoid by default:
- infinite waits
- implicit library retries
- unbounded buffering
- best-effort logging with no metrics
- fragile startup sequences
- one-shot release automation with no restart path

---

## Testing Rules

1. Test timeout behavior.
2. Test retry, backoff, and failure boundaries.
3. Test degraded dependency scenarios.
4. Test overload and queue saturation behavior where practical.
5. Test restartable deployment or operational automation where practical.
6. Test startup and health-check failure modes.

---

## Review Checklist

Before finalizing any change, verify:
- Does every remote call have an explicit timeout?
- Are retries bounded and safe?
- Are deployment and operational scripts restartable or idempotent where practical?
- Is there an overload strategy?
- Are queues and resource pools bounded?
- Is failure isolated from unrelated work?
- Are there enough diagnostics to investigate issues?
- Are health signals meaningful?
- Are scheduled and background workloads bounded and paced safely?
- Did we preserve the core service under likely failure scenarios?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, prefer the design that:
1. survives partial failure
2. limits blast radius
3. fails fast or degrades gracefully
4. exposes enough information to operate
5. prevents overload from becoming collapse

Production reality outranks happy-path elegance.
