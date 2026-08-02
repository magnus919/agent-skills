# Load / Soak Test Plan

Fill this template to design a load or soak test that produces valid capacity evidence. A capacity claim without load/soak evidence is incomplete.

## Test identification

- **Test objective:** _[fill: what capacity decision does this test support? e.g., "validate that the service can handle projected peak + 20% headroom at P99 latency < 200ms"]_
- **Test type:** _[fill: load test (target throughput, short duration) / soak test (sustained load, extended duration) / both]_
- **Test owner:** _[fill: name or team]_

## Target throughput

- **Target throughput:** _[fill: e.g., 1000 requests/second]_
- **Rationale:** _[fill: e.g., projected peak demand 850 req/s + 20% headroom]_
- **Ramp-up profile:** _[fill: how quickly does load ramp to target? e.g., linear over 5 minutes, step function]_
- **Steady-state duration (load test):** _[fill: e.g., 30 minutes after ramp-up]_
- **Soak duration (if applicable):** _[fill: e.g., 24 hours]_

## Test environment

- **Environment:** _[fill: production-like staging, dedicated test environment, or production (state which)]_
- **Environment parity:** _[fill: how does this environment differ from production? instance sizes, data volumes, network topology — every difference is an assumption]_
- **Justification:** _[fill: why is this environment sufficient evidence? if it is not production-like, what is the risk of extrapolation?]_

## Success criteria

| Criterion | Target | Measurement method |
|-----------|--------|--------------------|
| P50 latency | _[fill: e.g., < 50ms]_ | _[fill: client-side histogram, server-side metric]_ |
| P99 latency | _[fill: e.g., < 200ms]_ | _[fill: client-side histogram]_ |
| Error rate | _[fill: e.g., < 0.1% non-5xx]_ | _[fill: response status aggregation]_ |
| CPU utilization | _[fill: e.g., < 70% sustained]_ | _[fill: OS metrics / container metrics]_ |
| Memory utilization | _[fill: e.g., stable — no upward trend over soak]_ | _[fill: OS metrics; max threshold e.g., 80%]_ |
| _[fill: other]_ | _[fill: ...]_ | _[fill: ...]_ |

## Data collection

| Metric | Source | Granularity | Retention |
|--------|--------|-------------|-----------|
| Latency percentiles | _[fill: load generator]_ | _[fill: 1-second buckets]_ | _[fill: duration of test + 30 days]_ |
| Resource utilization | _[fill: infrastructure metrics]_ | _[fill: 10-second intervals]_ | _[fill: duration of test + 30 days]_ |
| Error logs | _[fill: application logs]_ | _[fill: per-event]_ | _[fill: duration of test + 30 days]_ |
| _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ | _[fill: ...]_ |

## Soak-specific checks

For soak tests, additionally monitor and record:

- [ ] Memory trend (flat, slowly rising, or leaking — with rate estimate)
- [ ] File descriptor count (stable or growing)
- [ ] Connection pool utilization (stable or growing)
- [ ] Disk usage growth (log rotation, temp files, WAL growth)
- [ ] GC pause time and frequency (stable or degrading)
- [ ] Any metric with a statistically significant trend over the soak period

## Test boundary

- **Boundary exercised:** _[fill: component / integration / end-to-end / production]_
- **What this test does NOT cover:** _[fill: e.g., does not test cross-region failover, does not exercise all API endpoints, does not include cold-start scenarios]_

## Evidence record

After the test, complete this section:

- **Test date:** _[fill: YYYY-MM-DD]_
- **Actual throughput achieved:** _[fill: ...]_
- **P50 latency (observed):** _[fill: ...]_
- **P99 latency (observed):** _[fill: ...]_
- **Error rate (observed):** _[fill: ...]_
- **Peak CPU utilization:** _[fill: ...]_
- **Peak memory utilization:** _[fill: ...]_
- **Soak findings (if applicable):** _[fill: memory trend, FD trend, connection pool trend, any anomalies]_
- **Verdict:** _[fill: PASS — all success criteria met / FAIL — criteria not met (list which) / PASS WITH GAPS — anomalies found (list which)]_
- **Follow-up actions:** _[fill: any findings requiring investigation or re-test]_

## Assumptions

- [ ] _[fill: test environment is sufficiently representative of production]_
- [ ] _[fill: load profile (request mix, payload sizes, user behavior) is representative of real traffic]_
- [ ] _[fill: no external dependencies have different behavior in test vs production]_
- [ ] _[fill: any other unverified assumption]_

## Ownership

- **Test designer:** _[fill: name or team]_
- **Test executor:** _[fill: name or team — may differ from designer]_
- **Evidence reviewer:** _[fill: name or role who reviews and accepts the evidence]_
