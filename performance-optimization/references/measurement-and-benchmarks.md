# Measurement and benchmark design

Read this when the baseline is missing, the metric is ambiguous, or a lab benchmark needs to stand in for a user outcome.

## Measure the boundary users feel

- Define the journey's start (user action or request arrival) and completion (result usable, not merely received). Record cold/warm state, cache state, device, network, data size, concurrency, and build.
- Use real-user or production data for prioritization and final validation. Segment by journey and material platform/workload differences; report sample count and a distribution (often p50/p75/p95) rather than averages alone. Include failures/timeouts rather than silently dropping slow attempts.
- Use traces to partition the critical path, metrics to see distribution and rate, profiles to identify expensive code, and logs for event context. If a span boundary crosses clocks or a sample excludes client/render time, state that limitation.
- Instrument the missing start/end or segment before tuning. Keep event names stable, label versions, estimate telemetry overhead and cardinality, avoid sensitive payloads, and ensure the measurement itself does not change the journey materially.

## Build a faithful laboratory proxy

Choose a representative workload from observed slow cases, including adverse data sizes and a normal case. Freeze fixture identity and record build, hardware, OS/runtime, dependencies, flags, concurrency, warmup, and command. Check that benchmark output cannot be optimized away and that setup/teardown is included or excluded intentionally. For asynchronous systems, decide whether wall time, CPU time, queue delay, or throughput answers the question.

Before using a structural count (instructions, allocations, React commits, DOM mutations, style recalculations) as a CI ratchet, show on at least two representative changes or cases that the count moves with user-relevant wall time, and confirm it does not hide a countermetric regression. If the relationship fails, use it only as diagnostic evidence or discard it.

Repeat noisy timings; interleave or randomize candidate and baseline if environment drift is material. Keep raw measurements, medians or percentiles, and run-to-run spread. A deterministic count can be checked exactly only if its environment and measurement are genuinely stable. Never claim statistical certainty from a single measurement or infer field impact from a synthetic-only win.

## Sources

- [Anthropic: How we made claude.ai 3x faster](https://claude.dev/blog/how-we-made-claude-ai-faster/) — journey definitions, calibrated lab proxies, CI ratchets, field follow-up.
- [web.dev: Core Web Vitals workflows](https://web.dev/articles/vitals-tools) — field measures user experience; lab tools help diagnose under fixed conditions.
- [OpenTelemetry: instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/) and [signals](https://opentelemetry.io/docs/concepts/signals/) — metrics, traces, logs, profiles, and their distinct roles.
- [Go diagnostics](https://go.dev/doc/diagnostics) — profile selection and the risk that diagnostics perturb each other.
- [Google Benchmark: reducing variance](https://github.com/google/benchmark/blob/main/docs/reducing_variance.md) — sources of host variance; [user guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md) — repetitions, warmup, and interleaving.
