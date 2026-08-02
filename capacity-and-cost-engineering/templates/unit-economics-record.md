# Unit Economics Record

Fill this template to calculate and record the unit cost of serving demand at the infrastructure level.

## Unit definition

- **Unit:** _[fill: e.g., cost per API request, cost per active user/month, cost per GB stored/month, cost per provisioned TPS]_
- **Why this unit:** _[fill: what decision does this unit cost inform? e.g., pricing, budget planning, SLO cost sensitivity]_

## Cost numerator

- **Total cost of capacity (period):** _[fill: e.g., $12,000/month for compute, storage, network, and data transfer]_
- **Allocation method:** _[fill: direct resource cost, attributed shared cost, or fully loaded (including overhead). State which and why.]_
- **Cost scope:** _[fill: single service / team / platform — what is included and what is excluded]_
- **Cost source:** _[fill: cloud bill, internal cost dashboard, finance report — with date]_

## Demand denominator

- **Total demand units served (same period):** _[fill: e.g., 50,000,000 requests/month, 10,000 active users]_
- **Measurement source:** _[fill: production metrics, CDN logs, API gateway — with date and measurement method]_
- **Confidence:** _[fill: high/medium/low — is this measured or estimated?]_

## Unit cost calculation

```
unit cost = total cost of capacity / total demand units served
         = [fill: $X] / [fill: Y units]
         = [fill: $Z per unit]
```

- **Unit cost:** _[fill: $Z per unit]_
- **Period:** _[fill: month/quarter/year — must match numerator and denominator]_

## Cost-per-SLO comparison

| SLO target | Required capacity (relative to baseline) | Estimated unit cost | Cost multiplier vs baseline |
|------------|----------------------------------------|---------------------|-----------------------------|
| _[fill: 99.9%]_ | _[fill: 1.0x — baseline]_ | _[fill: $Z/unit]_ | _[fill: 1.0x]_ |
| _[fill: 99.95%]_ | _[fill: 1.3x — redundancy, faster failover]_ | _[fill: $Z*1.3/unit]_ | _[fill: 1.3x]_ |
| _[fill: 99.99%]_ | _[fill: 2.5x — multi-region, active-active]_ | _[fill: $Z*2.5/unit]_ | _[fill: 2.5x]_ |

## Unit cost trend

| Period | Unit cost | Change | Explanation |
|--------|-----------|--------|-------------|
| _[fill: current]_ | _[fill: $Z]_ | — | — |
| _[fill: projected next quarter]_ | _[fill: $Z']_ | _[fill: +/-X%]_ | _[fill: scale, reserved capacity, price change]_ |
| _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ |

## Assumptions

- [ ] _[fill: cost allocation method is accurate — state assumption or evidence]_
- [ ] _[fill: demand measurement captures all relevant units — state assumption or evidence]_
- [ ] _[fill: unit cost is stable over the projection period — or state change driver]_
- [ ] _[fill: any other unverified assumption]_

## Evidence sources

| Source | What it provides | Boundary exercised |
|--------|-----------------|--------------------|
| _[fill: cloud bill / cost dashboard]_ | _[fill: cost numerator]_ | _[fill: production]_ |
| _[fill: production metrics]_ | _[fill: demand denominator]_ | _[fill: production]_ |
| _[fill: load test at SLO targets]_ | _[fill: capacity multipliers at each SLO level]_ | _[fill: end-to-end]_ |

## Ownership

- **Unit cost owner:** _[fill: name or team accountable for this calculation]_
- **Cost data owner:** _[fill: name or team that provides cost numerator]_
- **Demand data owner:** _[fill: name or team that provides demand denominator]_

## Tradeoffs

- _[fill: e.g., higher SLO → higher unit cost; is the reliability improvement worth the cost per unit?]_
- _[fill: e.g., fully loaded cost includes overhead that obscures infrastructure-level decisions]_
- _[fill: e.g., averaging across all services hides services with outlier unit costs]_
