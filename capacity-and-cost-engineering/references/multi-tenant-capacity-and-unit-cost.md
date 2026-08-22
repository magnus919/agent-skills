# Multi-Tenant Capacity and Unit Cost

Use this reference when a shared service serves multiple tenants whose demand,
promises, or resource footprints differ. The purpose is to produce capacity and
cost evidence, not to choose the SaaS domain model or security controls.

## Start with distributions

Represent demand as tenant profiles rather than one aggregate average. For each
profile, record the demand units, request or job mix, payload or object size,
concurrency, burst shape, background work, storage growth, and tier or placement
promise. Use observed tenant cohorts where possible and label synthetic profiles
as assumptions. Preserve the distribution's shape: a small number of very large
tenants can dominate a pooled system even when the mean tenant looks modest.

Useful views include:

- per-tenant time series for rate, concurrency, queue depth, storage, and work;
- a distribution across tenants for each resource, with the statistic chosen for
  the decision rather than a default percentile;
- joint views that show whether high demand, large objects, and burstiness occur
  in the same tenants;
- a scenario for new, growing, dormant, migrating, and unusually hot tenants;
- confidence and provenance for every profile, including sampling bias and
  omitted tenants.

Do not substitute a global average, a single representative tenant, or an
arbitrary percentile for the distribution. If a percentile or cap is selected,
explain the user promise, failure consequence, and evidence that make it useful.

## Find skew and hot tenants

Map the demand profile onto the resource boundary that can saturate: CPU,
memory, connections, partitions, IOPS, queue workers, cache capacity, search
shards, network, or an external quota. Partition skew is a separate question from
request skew. A tenant may be moderate overall but overload one partition, key
range, shard, worker pool, or availability zone.

For each hot-tenant or skew scenario, record:

1. the detection signal and the identity granularity available to operators;
2. the resource and neighboring tenants exposed to contention;
3. the admission, queueing, scheduling, placement, throttling, or isolation
   response;
4. the impact on the hot tenant and on protected tenants;
5. the recovery and rebalancing path, including backlog and data-integrity
   checks; and
6. the evidence boundary, workload mix, duration, and unresolved gaps.

Route isolation mechanisms, authorization, and noisy-neighbor threat analysis to
`secure-software-engineering`. Route the end-to-end tenancy, lifecycle, and
placement architecture to `multi-tenant-saas-architecture`.

## Compare pooled and siloed headroom

For a pooled deployment, model shared baseline, aggregate demand distribution,
correlation between tenants, admission behavior, and the headroom needed to
protect the promised service during a hot-tenant or dependency scenario. Pooling
can benefit from imperfectly correlated demand, but its usable headroom is
bounded by the resource with the worst contention or skew, not by a fleet average.

For a siloed or dedicated deployment, model the per-tenant baseline, reserved
headroom, failure-domain requirement, idle capacity, and operational overhead.
Do not assume that a silo is cheaper or more reliable. Compare the scenarios that
matter: ordinary load, tenant growth, burst, tenant failure, placement movement,
and loss of a resource or failure domain. Hybrid placement should show which
resources are pooled and which are dedicated, with separate evidence for each.

Headroom is a decision variable. State what it protects, the time horizon and
provisioning lead time, the observed saturation behavior, and the cost of unused
capacity. Never present one utilization or headroom percentage as a general rule.

## Translate tier promises into capacity controls

For every tier promise, connect the customer-visible statement to a measurable
capacity behavior: sustained demand, burst allowance, concurrency, storage or
job limit, latency treatment, priority, isolation, or recovery treatment. Record
whether the promise is a contract, a product default, or an operational goal.

Quotas and rate limits are controls, not proof of capacity. Define the scope,
steady behavior, burst behavior, response to excess, fairness objective, and
backpressure or degradation path. Admission should preserve the critical path
and make rejection or delay explicit rather than allowing unbounded queues and
retry amplification.

Fairness is contextual. Choose the fairness policy from the promise and resource:
weighted shares, reserved capacity, tier priority, work conservation, isolation,
or another explicit rule. Measure both protected-tenant outcomes and the
consequence for the tenant being constrained. Do not use a universal fairness
ratio, quota, utilization target, or rejection threshold. A threshold is valid
only when its rationale, owner, workload, and review trigger are recorded.

## Produce tenant-variable unit cost

Separate the cost model into at least:

- **platform baseline:** costs that remain for the service or pool when tenant
  demand is absent or minimal;
- **tenant-variable cost:** incremental compute, storage, transfer, operations,
  or other resource cost attributable to a tenant profile; and
- **allocation of shared cost:** the chosen method for assigning pooled cost,
  such as measured consumption, reserved entitlement, capacity reservation, or a
  transparent blended allocation.

Report direct or marginal cost separately from fully allocated cost. Use the same
period, scope, and demand denominator. For tenant `t`, a useful model is:

```text
tenant cost(t) = allocated baseline(t) + measured variable cost(t)
tenant unit cost(t) = tenant cost(t) / tenant demand units(t)
```

The allocation method must explain how idle pooled capacity, shared control-plane
work, replication, support, backups, and failure-domain redundancy are treated.
Keep fixed commitments separate from costs that change with demand. Segment units
by materially different work types rather than averaging cheap metadata work with
expensive jobs. Route revenue, pricing, margin, and commercial packaging to
`financial-modeling`; route cost tags, billing exports, and resource policy
implementation to `platform-engineering`.

## Evidence standard

Before approving a tenant capacity or unit-cost claim, require representative
per-tenant load and soak evidence. The test should exercise the relevant tenant
distribution concurrently, include hot and skewed profiles, use production-like
data and placement, and observe tenant-level and shared-resource outcomes. Record
latency, errors, queueing, throttling, admission decisions, resource saturation,
partition balance, backlog recovery, and cost inputs.

Component benchmarks can explain a mapping, but they do not establish end-to-end
fairness or pooled headroom. A fleet aggregate can show total spend, but it does
not establish tenant-variable cost. If representative evidence is unavailable,
the output is a model with an explicit gap and a required test, not a validated
capacity claim.

## Completion check

Stop when the model names the tenant distribution, hot/skew scenario, pooled or
siloed headroom choice, tier promise, quota/admission behavior, fairness policy,
baseline and variable cost allocation, representative per-tenant load/soak
evidence, owners, and unresolved assumptions. Escalate a promise that cannot be
supported without silently weakening reliability, privacy, security, or user
outcomes.
