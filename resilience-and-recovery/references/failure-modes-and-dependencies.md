# Failure Modes and Dependencies

## Purpose

Map how a system can fail and what happens when it does. This reference provides the method for identifying failure modes, analyzing dependency behavior under failure, and designing degradation paths with tier-based feature shedding.

## Failure-mode identification

### Categories

| Category | Examples | Detection method |
|---|---|---|
| Component failure | Service crash, OOM kill, deadlock | Health checks, process supervision |
| Dependency failure | Upstream API timeout, database unavailable | Circuit breakers, health indicators |
| Resource exhaustion | Disk full, connection pool saturated, CPU starvation | Resource monitoring, capacity alerts |
| Region/zone failure | Cloud AZ outage, datacenter power loss | Multi-region health checks, DNS failover |
| Data corruption | Bit rot, bad deployment, logical error | Checksums, integrity scans, replica comparison |
| Operator error | Wrong command, wrong target, wrong config | Change reviews, guardrails, dry-run modes |
| Security event | Ransomware, credential leak, unauthorized access | Intrusion detection, anomaly monitoring |
| Cascading failure | Retry storms, thundering herd, dependency chain collapse | Backpressure, circuit breakers, bulkheads |

### Method

1. **List every component** in the system boundary.
2. **List every dependency** (upstream and downstream), including external SaaS, internal services, databases, caches, message queues, and third-party APIs.
3. **For each component and dependency**, ask: what happens when it fails? What happens when it is slow? What happens when it returns incorrect data?
4. **Classify each failure** by impact: full outage, degraded but acceptable, degraded and unacceptable, or no impact.
5. **Record assumptions** — especially timeout values, retry behavior, and fallback paths — and verify them in exercises.

## Dependency behavior under failure

Every dependency is a failure mode. For each dependency, define:

| Property | Question |
|---|---|
| **Timeout** | How long does the system wait before treating the dependency as failed? |
| **Retry behavior** | Does the system retry? With what backoff? How many times? Is there a retry budget? |
| **Circuit breaker** | Does the system stop calling a failing dependency after a threshold? What is the threshold? How does it reset? |
| **Fallback** | What does the system do when the dependency is unavailable — cached response, default value, degraded path, or error? |
| **Consumer contract** | What does the system promise ITS consumers when this dependency fails? |

### Dependency-loss scenarios

| Scenario | System behavior | Consumer impact |
|---|---|---|
| Dependency unavailable (hard failure) | Circuit breaker opens; fallback activated | Degraded but operational (if fallback exists); error if not |
| Dependency slow (latency degradation) | Timeout triggers after threshold; retries exhaust budget | Slow responses; potential timeout cascades |
| Dependency returns incorrect data | Detection via response validation; circuit breaker may not help (dependency is "up") | Data corruption risk; requires semantic validation |

## Degradation paths

### Tier-based feature shedding

When a dependency or component fails, shed features by tier:

1. **Tier 3 — Nice-to-have (shed immediately):** Non-critical embellishments — recommendations, social features, cosmetic UI elements, analytics forwarding. These are shed without user-visible impact beyond their absence.
2. **Tier 2 — Enhancing (shed if necessary):** Features that improve experience but are not essential to the core function — advanced search filters, rich formatting, personalization. Shed after Tier 3 if further headroom is needed.
3. **Tier 1 — Core (preserve at all costs):** The system's reason to exist — placing an order, submitting a form, viewing critical data. Must remain available in degraded mode.

### Degradation design checklist

- [ ] Which features are shed first, second, and last?
- [ ] What does the user see when a feature is shed — a graceful message, a fallback UI, or nothing?
- [ ] How does the system recover when the dependency returns — automatically or manually?
- [ ] Is there a maximum degraded-operation window after which a full outage is preferable?
- [ ] Has the degradation path been exercised in a game day?

### Degradation vs. outage decision

Not every failure justifies degraded operation. Ask:

- Is degraded operation safer than a clean failure? (e.g., financial systems may prefer to stop than to operate with uncertain data)
- Will degraded operation cause downstream data corruption or inconsistency?
- Can the system detect when degradation is no longer acceptable and fail closed?
