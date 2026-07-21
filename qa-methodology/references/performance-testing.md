# Performance Testing

## Types

| Type | Question Answered | Tool Examples |
|------|-------------------|---------------|
| Load test | Does it handle expected traffic? | k6, Locust, Gatling |
| Stress test | Where does it break? | k6 (ramping VUs), wrk |
| Soak test | Does it degrade over time? | k6 (constant load, 4–24h) |
| Spike test | Does it survive sudden bursts? | k6 (spike scenario) |
| Benchmark | What's the raw throughput/latency? | wrk, hey, ab, pytest-benchmark |

## When to Performance Test

- Before launch (baseline)
- After architectural changes (new DB, new cache layer, new service boundary)
- After dependency upgrades (ORM version, driver changes)
- When latency SLO is at risk (p99 trending up over 2+ sprints)

**Not** on every PR — that's what unit/integration tests are for.

## k6 Pattern (Load Test)

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
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
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

## Interpreting Results

| Symptom | Likely Cause | Next Step |
|---------|-------------|-----------|
| Latency climbs linearly with VUs | Single-threaded bottleneck or lock contention | Profile CPU, check for global locks |
| Latency flat then sudden cliff | Resource exhaustion (connections, memory, file descriptors) | Check pool sizes, `ulimit`, OOM killer |
| Throughput plateaus early | Downstream dependency is the bottleneck | Test the dependency in isolation |
| Errors only at high concurrency | Race condition or timeout misconfiguration | Check connection pool, retry storms |
| Memory grows during soak | Leak — unclosed connections, unbounded cache | Heap dump at intervals, diff allocations |

## CI Integration

- Run a **smoke benchmark** (10 VUs, 30s) on PRs that touch hot paths — fast, catches 10× regressions
- Run **full load test** nightly against staging
- Alert if p95 regresses > 20% vs 7-day baseline
- Store results in time-series (k6 Cloud, Grafana, or CSV + script) for trend detection
