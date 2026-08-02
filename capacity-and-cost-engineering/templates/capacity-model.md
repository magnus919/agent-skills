# Capacity Model

Fill this template to produce a capacity model connecting demand to infrastructure requirements over a projection horizon.

## Demand assumptions

- **Current demand:** _[fill: e.g., 500 requests/second, 10,000 concurrent users, 2 TB/day ingested]_
- **Demand unit:** _[fill: requests/sec, concurrent users, GB ingested, messages/sec — be specific]_
- **Growth rate:** _[fill: e.g., 15% month-over-month, or flat with seasonal spike]_
- **Known peak events:** _[fill: product launch, Black Friday, seasonal — date/range, expected multiplier over baseline]_
- **Projection horizon:** _[fill: e.g., 6 months, 12 months]_
- **Confidence in demand forecast:** _[fill: high/medium/low with rationale — what is this based on? historical data, product roadmap, market estimate?]_

## Capacity-unit mapping

| Demand unit | Capacity unit | Mapping ratio | Rationale |
|-------------|---------------|---------------|-----------|
| _[fill: e.g., 1 request/sec]_ | _[fill: e.g., 0.25 vCPU, 256 MB memory]_ | _[fill: e.g., measured at 70% utilization]_ | _[fill: from load test 2026-01-15]_ |
| _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ |

## Utilization targets

| Resource | Target utilization | Rationale | Evidence |
|----------|-------------------|-----------|----------|
| CPU | _[fill: e.g., 70%]_ | _[fill: e.g., spiky traffic needs headroom for P99 latency]_ | _[fill: load test at 80% showed P99 degradation]_ |
| Memory | _[fill: e.g., 80%]_ | _[fill: e.g., GC overhead acceptable up to 80%]_ | _[fill: soak test 24h at 85% — no OOM, stable]_ |
| Storage | _[fill: e.g., 75%]_ | _[fill: e.g., provisioned IOPS degrade above 80%]_ | _[fill: vendor docs + observed IOPS curve]_ |
| Network | _[fill: e.g., 60%]_ | _[fill: e.g., burst capacity for peak events]_ | _[fill: ...]_ |

## Scaling triggers

| Resource | Trigger threshold | Action | Lead time |
|----------|------------------|--------|-----------|
| _[fill: CPU]_ | _[fill: sustained > 60% for 5 min]_ | _[fill: scale out by 2 instances]_ | _[fill: 3 min]_ |
| _[fill: Storage]_ | _[fill: projected to hit 75% in 30 days]_ | _[fill: provision additional 500 GB]_ | _[fill: 7 days for procurement]_ |

## Capacity projection

| Period | Projected demand | Required capacity | Scaling action | Estimated cost |
|--------|-----------------|-------------------|----------------|----------------|
| _[fill: Month 1]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: none]_ | _[fill: $X]_ |
| _[fill: Month 2]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: scale out 2 instances]_ | _[fill: $Y]_ |
| _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ |

## Assumptions

- [ ] _[fill: assumption about demand pattern, growth stability, peak shape]_
- [ ] _[fill: assumption about unit cost stability, no price changes]_
- [ ] _[fill: assumption about no architecture changes that alter capacity/demand ratio]_
- [ ] _[fill: any other unverified assumption]_

Every assumption without evidence must be labeled as such.

## Evidence sources

| Source | What it provides | Boundary exercised |
|--------|-----------------|--------------------|
| _[fill: load test 2026-01-15]_ | _[fill: capacity/demand ratio at 70% CPU]_ | _[fill: end-to-end]_ |
| _[fill: production metrics Jan-Mar 2026]_ | _[fill: observed growth rate]_ | _[fill: production]_ |
| _[fill: ...]_ | _[fill: ...]_ | _[fill: component / integration / end-to-end / production]_ |

## Ownership

- **Model owner:** _[fill: name or team]_
- **Capacity provisioning owner:** _[fill: name or team — may differ from model owner]_
- **Review cadence:** _[fill: e.g., monthly, or on demand change >20%]_

## Tradeoffs

- _[fill: e.g., lower utilization target → higher cost but lower latency risk]_
- _[fill: e.g., faster scaling trigger → more responsive but more frequent provisioning events]_
- _[fill: any tradeoff between cost, performance, reliability, or operational complexity]_
