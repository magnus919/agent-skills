# Performance Testing

## Types

| Type | Question Answered | Duration | Frequency |
|------|-------------------|----------|-----------|
| Load test | Does it handle expected traffic? | 5–15 min | Nightly / pre-release |
| Stress test | Where does it break? | Ramp until failure | On-demand / architectural changes |
| Soak test | Does it degrade over time (leaks)? | 4–24 hours | Weekly |
| Spike test | Does it survive sudden bursts? | Seconds to minutes | Pre-launch / event prep |
| Benchmark | What's the raw throughput/latency? | 30s–2 min | On PR (smoke) |

## Tool Landscape

| Tool | Language | Strengths | Weaknesses | Best For |
|------|----------|-----------|------------|----------|
| **k6** | JavaScript (Go runtime) | CI-native, thresholds as code, low resource overhead, Grafana ecosystem | No GUI scripting; HTTP/gRPC/WebSocket/browser (experimental) | CI-integrated load testing, developer-owned perf |
| **Locust** | Python | Distributed by design, real-user behavior modeling, event-driven | Higher memory per VU than k6; Python GIL limits single-node throughput | Complex user flows, distributed load generation |
| **Gatling** | Scala/Java/Kotlin | Highest throughput per node, detailed HTML reports, protocol breadth | Steep learning curve; commercial features paywalled | High-throughput enterprise, protocol-heavy (JMS, JDBC) |
| **JMeter** | Java (GUI + CLI) | Widest protocol support, plugin ecosystem, 20+ years of community | Heavy resource usage, brittle test plans, XML config | Legacy protocol support, non-developer QA teams |

### Selection Decision

| Signal | Choose |
|--------|--------|
| CI/CD integration is the primary driver | k6 |
| Team is Python-centric, needs distributed load | Locust |
| Need maximum VUs per machine, detailed reporting | Gatling |
| Must test JMS, JDBC, FTP, or other non-HTTP protocols | JMeter |
| Browser-level rendering performance matters | k6 (browser module) or Lighthouse CI |

## SLO-Based Threshold Design

Performance thresholds must derive from product requirements, not arbitrary round numbers.

### Deriving Thresholds from SLOs

1. **Start with the product SLO.** Example: "95% of API requests complete in < 300ms" → p95 < 300ms.
2. **Set the test threshold at the SLO.** The load test asserts `p(95)<300`.
3. **Add a warning threshold below the SLO** for early signal: `p(95)<250` (advisory, does not fail CI).
4. **Set error-rate threshold from availability SLO.** If availability SLO is 99.9%, error threshold is `rate<0.001`.

### Baseline-Then-Regress Pattern

Never evaluate a single run in isolation. Establish a baseline first:

```
1. Run the load test on a known-good commit (e.g., main HEAD).
2. Store p50, p95, p99, throughput, error rate as the baseline.
3. On subsequent runs, compare against the 7-day rolling baseline.
4. Alert if p95 regresses > 20% vs baseline.
5. Fail CI (blocking gate) if p95 exceeds the absolute SLO.
```

| Comparison | Action |
|-----------|--------|
| p95 within 10% of baseline | Pass — no action |
| p95 regressed 10–20% | Advisory warning — investigate if trend continues |
| p95 regressed > 20% vs baseline | Alert — likely regression; investigate before merge |
| p95 exceeds absolute SLO | Block merge — SLO breach |

### Worked Example (k6 thresholds)

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // ramp up
    { duration: '1m', target: 20 },    // steady state
    { duration: '10s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<800'],  // from product SLO
    http_req_failed: ['rate<0.001'],                  // from availability SLO
  },
};

export default function () {
  const res = http.get('https://staging.example.com/api/items');
  check(res, {
    'status 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(1);
}
```

## Key Metrics

| Metric | Definition | Target Guidance |
|--------|-----------|-----------------|
| p50 latency | Median response time | User-perceived "normal" |
| p95 latency | 95th percentile | SLO boundary for most APIs |
| p99 latency | 99th percentile | Tail latency — catches GC pauses, cold starts |
| Throughput | Requests/sec sustained | Compare against capacity plan |
| Error rate | 5xx / total | < 0.1% under load |
| Saturation | CPU/memory/connections at peak | < 80% = headroom |

## CI Cadence

| Trigger | Test Type | Duration | Gate |
|---------|-----------|----------|------|
| PR (hot-path changes only) | Smoke benchmark (10 VUs, 30s) | < 2 min | Advisory — catches 10× regressions |
| Nightly (staging) | Full load test (expected traffic profile) | 10–15 min | Blocking for release branch |
| Weekly | Soak test (constant load, 4–8h) | 4–8 hours | Alert on degradation trend |
| Pre-release | Stress test + spike | 30 min | Blocking — must not regress vs last release |

**Not on every PR.** Full load tests on every PR waste CI resources and produce noisy results. Smoke benchmarks on PRs catch gross regressions; nightly runs catch subtle ones.

## Interpreting Results

| Symptom | Likely Cause | Next Step |
|---------|-------------|-----------|
| Latency climbs linearly with VUs | Single-threaded bottleneck or lock contention | Profile CPU, check for global locks |
| Latency flat then sudden cliff | Resource exhaustion (connections, memory, FDs) | Check pool sizes, `ulimit`, OOM killer |
| Throughput plateaus early | Downstream dependency is the bottleneck | Test the dependency in isolation |
| Errors only at high concurrency | Race condition or timeout misconfiguration | Check connection pool, retry storms |
| Memory grows during soak | Leak — unclosed connections, unbounded cache | Heap dump at intervals, diff allocations |

## Gate Governance

Performance thresholds feed into quality gate decisions — they are not standalone pass/fail numbers. A perf regression that exceeds the SLO is a **blocking gate** (prevents merge/deploy); a regression within the warning band is an **advisory gate** (flags for review). For the full gate design framework (blocking vs advisory, pipeline stages, anti-patterns), see [quality-gates-and-metrics.md](./quality-gates-and-metrics.md).

## Gotchas

- **Thresholds without baselines are meaningless.** A p95 of 280ms tells you nothing without knowing whether last week's was 120ms. Always baseline first.
- **Testing against shared staging environments** produces noisy results from other teams' load. Use dedicated perf environments or time-boxed windows.
- **Ignoring tail latency.** p50 can look healthy while p99 is 10× the SLO. Always assert on percentiles, not averages.
- **Running the full suite on every PR** wastes CI minutes and teaches teams to ignore perf results. Tier by trigger.

## Related

- Gate governance (blocking vs advisory, pipeline placement): [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)
- Test data for load tests (volume seeding): [test-data-management.md](./test-data-management.md)

*Sources: k6 documentation (grafana.com/k6), Locust docs (locust.io), Gatling docs (gatling.io), JMeter docs (jmeter.apache.org), Google SRE Workbook (O'Reilly, 2018), DORA State of DevOps Reports.*
