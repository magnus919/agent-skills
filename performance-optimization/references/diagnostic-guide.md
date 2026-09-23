# Symptom-to-signal diagnostic guide

Start with a user-visible symptom and use the signal that can distinguish its likely causes. A metric says **where or how often**; a trace shows **which part of one journey**; a profile shows **what code consumed CPU or memory**. No single signal explains all three.

| Symptom | First signal | Next diagnostic | Common interpretation |
|---|---|---|---|
| Slow interaction or request | Journey latency distribution, segmented by version and workload | Trace the slow slice; compare client, queue, service, dependency, and render spans | One segment dominates; missing spans mean the boundary is not yet observable |
| High CPU with normal request volume | CPU utilization and CPU time per completed operation | CPU profile on a representative slow interval | A hot function, repeated work, or contention; verify it is on the critical path |
| Long tail with acceptable median | p95/p99 latency, timeout and error rates | Compare slow traces with normal traces; inspect queue depth and dependency timing | Queues, retries, locks, GC, or a small adverse workload may dominate |
| High memory or rising memory over time | Heap/RSS trend and allocation rate, by workload/build | Heap/allocation profile and lifecycle trace | Retained objects, allocation churn, unbounded buffering, or cache growth |
| Low throughput before saturation | Completed work per second plus latency and error rate | Queue/wait profile, concurrency trace, CPU and I/O measures | Serialization, blocking, a dependency ceiling, or insufficient useful parallelism |
| Browser page feels slow despite fast server spans | Field interaction/render metric and client timing | Browser trace/profile, long tasks, layout/paint evidence | Client-side work, network transfer, hydration, or rendering is outside server timing |
| A benchmark improved but users did not | Matched field outcome by build/platform/workload | Check journey boundary, representativeness, and countermetrics | The proxy may not predict the user outcome, or exposure/data changed |

## Triage sequence

1. Name the journey, start/end boundary, affected population, and primary outcome. Preserve failures and timeouts in the distribution.
2. Segment the symptom by build, platform, and workload size. If the signal is absent, instrument the smallest missing boundary and label proxies.
3. Follow a representative slow trace to the expensive segment. Compare it with a normal trace so common work is not mistaken for the cause.
4. Profile that segment using the diagnostic that fits the symptom: CPU for active computation, heap/allocation for memory, blocking/lock or queue evidence for waits. Do not infer CPU work from wall time alone.
5. Reproduce the suspected mechanism locally or in a controlled environment. Change one reversible thing, check output/correctness, and compare repeated measurements on the same workload.
6. Treat a lab improvement as a hypothesis until matched field data confirms the user outcome. Use [measurement-and-benchmarks.md](measurement-and-benchmarks.md) and [experiment-and-rollout.md](experiment-and-rollout.md) for design and decision rules.

For OpenTelemetry signal boundaries, see [signals](https://opentelemetry.io/docs/concepts/signals/) and [profiling](https://opentelemetry.io/docs/concepts/signals/profiles/). For Go-specific profile selection and diagnostic interactions, see [Go diagnostics](https://go.dev/doc/diagnostics). Browser field and lab measures answer different questions; see [web.dev's Web Vitals tools](https://web.dev/articles/vitals-tools).

Route operation of a named observability product to [telemetry](../../telemetry/SKILL.md) or [grafana](../../grafana/SKILL.md); route frontend rendering work to [frontend-engineering](../../frontend-engineering/SKILL.md), backend query/service work to [backend-engineering](../../backend-engineering/SKILL.md), and SLO or incident policy to [site-reliability-engineering](../../site-reliability-engineering/SKILL.md). These links are catalog skills, not substitutes for the diagnostic sequence above.
