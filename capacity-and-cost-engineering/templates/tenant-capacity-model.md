# Tenant Capacity and Unit-Cost Model

Fill this template when tenant demand or tier promises change the capacity and
cost decision. Use measured distributions where available; mark assumptions and
synthetic profiles clearly.

## Service and promise

- **Service/resource boundary:** _[fill: API, worker pool, database partition, storage, etc.]_
- **Decision:** _[fill: sizing, placement, quota, tier promise, or cost allocation decision]_
- **Tenant tiers or profiles in scope:** _[fill: names and why they are representative]_
- **Customer promises:** _[fill: contractual promises, product defaults, and operational goals separately]_
- **SLO/performance dependency:** _[fill: owner and relevant target; route SLO definition to SRE]_

## Tenant demand profiles

| Profile or cohort | Tenant count/weight | Demand and mix | Burst/concurrency | Storage/background work | Evidence/confidence |
|---|---:|---|---|---|---|
| _[fill: ordinary pooled tenant]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |
| _[fill: hot or bursty tenant]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |
| _[fill: dedicated/silo tenant]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |

- **Distribution view:** _[fill: per-tenant time series, selected statistic(s), correlation/skew analysis]_
- **Sampling limits:** _[fill: omitted tenants, seasonality, new-tenant uncertainty, synthetic data]_

## Skew and hot-tenant analysis

- **Resource/partition boundary:** _[fill: shard, key range, worker, zone, cache, queue, or other]_
- **Detection signal:** _[fill: tenant-level and shared-resource signal]_
- **Contention path:** _[fill: which tenants or tiers are affected and how]_
- **Response:** _[fill: admission, queue, scheduling, throttling, placement, or isolation behavior]_
- **Recovery/rebalance:** _[fill: backlog, movement, reconciliation, and verification]_
- **Security handoff:** _[fill: isolation and authorization evidence owned by secure-software-engineering]_

## Pooled, siloed, or hybrid comparison

| Scenario | Pooled baseline/headroom | Siloed baseline/headroom | Hybrid choice | Evidence and tradeoff |
|---|---|---|---|---|
| Ordinary load | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |
| Hot tenant or burst | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |
| Failure-domain loss | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |
| Tenant growth/movement | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |

- **Headroom rationale:** _[fill: what it protects, lead time, observed saturation, and cost of idle capacity; no universal percentage]_

## Quota, admission, and fairness

- **Quota scope and units:** _[fill: tenant/tier/resource and steady/burst units]_
- **Admission rule:** _[fill: accept, queue, prioritize, throttle, or reject and why]_
- **Excess response:** _[fill: status/backpressure/degradation and customer communication]_
- **Fairness policy:** _[fill: explicit policy for this promise/resource, not a universal ratio]_
- **Fairness evidence:** _[fill: protected-tenant outcomes, constrained-tenant outcome, workload mix, duration, owner]_
- **Review trigger:** _[fill: what observed change causes recalibration]_
- **Implementation handoff:** _[fill: platform owner; this record does not configure infrastructure]_

## Tenant-variable unit cost

- **Period and scope:** _[fill: same period for cost and demand]_
- **Platform baseline cost:** _[fill: idle/minimum pool, control plane, shared redundancy]_
- **Variable cost pool:** _[fill: compute, storage, transfer, jobs, support, or other measured costs]_
- **Shared-cost allocation:** _[fill: measured use, reserved entitlement, capacity reservation, blended, or other rationale]_
- **Tenant demand unit:** _[fill: request/job/GB/concurrency unit and measurement source]_

```text
tenant cost = allocated baseline + measured variable cost
tenant unit cost = tenant cost / tenant demand units
```

| Tenant/profile | Allocated baseline | Variable cost | Total cost | Demand units | Unit cost | Confidence/gap |
|---|---:|---:|---:|---:|---:|---|
| _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ | _[fill]_ |

- **Financial handoff:** _[fill: pricing, margin, or commercial decision routed to financial-modeling]_

## Representative load/soak evidence

- **Test plan:** _[fill: link to `templates/load-soak-test-plan.md`]_
- **Profiles exercised concurrently:** _[fill: ordinary, hot, skewed, tier, placement]_
- **Environment parity:** _[fill: data volume, topology, partitions, dependencies]_
- **Observed tenant outcomes:** _[fill: latency, errors, throttles, admission, backlog]_
- **Observed shared outcomes:** _[fill: saturation, partition balance, recovery, cost inputs]_
- **Soak findings:** _[fill: leaks, queue growth, fairness drift, or other trends]_
- **Verdict:** _[fill: validated / model with gap / failed; list criteria]_

## Assumptions, ownership, and decision

- **Assumptions and gaps:** _[fill]_
- **Capacity/model owner:** _[fill]_
- **Demand measurement owner:** _[fill: route instrumentation to product-analytics-and-measurement]_
- **SLO/reliability owner:** _[fill: route SLO and error budget to site-reliability-engineering]_
- **Decision owner and review date:** _[fill]_
- **Chosen option and rationale:** _[fill]_
