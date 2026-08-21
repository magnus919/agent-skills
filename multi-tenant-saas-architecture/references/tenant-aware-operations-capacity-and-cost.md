# Tenant-Aware Operations, Capacity, and Cost

An operational design is incomplete if it only describes the fleet average. Record tenant distribution, tier promises, resource ownership, and what happens when one tenant is unusually large, busy, expensive, or failing.

## Required scenarios

- **Hot tenant:** detect skew, protect other tenants, choose throttle, queue, placement, or isolation behavior, and define customer communication.
- **Noisy neighbor:** prove fairness at the resource boundary, not just at the API gateway; include caches, queues, storage, and background work.
- **Tenant restore:** identify whether restore is tenant-scoped, partition-scoped, or service-wide; preserve ordering and reconcile derived data before reopening traffic.
- **Tenant deletion/export:** enumerate primary, replicas, caches, indexes, logs, backups, and derived data; verify completion and legal holds with `privacy-engineering`.
- **Placement change:** define the trigger, compatibility window, movement evidence, and recovery path with `migration-engineering`.
- **Cost anomaly:** attribute shared baseline and tenant-variable cost separately; route quantitative modeling to `capacity-and-cost-engineering` and commercial decisions to `financial-modeling`.

## Evidence handoffs

The architecture brief names the metric, owner, and decision trigger. It does not invent universal thresholds. `capacity-and-cost-engineering` owns demand distributions, load/soak evidence, unit cost, quota controls, and SLO-cost tradeoffs. `platform-engineering` owns the implementation of autoscaling, scheduling, telemetry substrate, and resource policies. `site-reliability-engineering` owns SLOs, error budgets, incident command, and live operations.

For every tenant-aware metric, distinguish tenant identity from sensitive payload, define aggregation and access, and check whether the telemetry creates a privacy obligation.
