# Measurement and benchmark design

Read this when the baseline is missing, the metric is ambiguous, or a lab benchmark needs to stand in for a user outcome.

## Measure the boundary users feel

- Define the journey's start (user action or request arrival) and completion (result usable, not merely received). Record cold/warm state, cache state, device, network, data size, concurrency, and build.
- Use real-user or production data for prioritization and final validation. Segment by journey and material platform/workload differences; report sample count and a distribution (often p50/p75/p95) rather than averages alone. Include failures/timeouts rather than silently dropping slow attempts.
- Use traces to partition the critical path, metrics to see distribution and rate, profiles to identify expensive code, and logs for event context. If a span boundary crosses clocks or a sample excludes client/render time, state that limitation.
- Instrument the missing start/end or segment before tuning. Keep event names stable, label versions, estimate telemetry overhead and cardinality, avoid sensitive payloads, and ensure the measurement itself does not change the journey materially.

## Build a faithful laboratory proxy

Choose a representative workload from observed slow cases, including adverse data sizes and a normal case. Freeze fixture identity and record build, hardware, OS/runtime, dependencies, flags, concurrency, warmup, and command. Check that benchmark output cannot be optimized away and that setup/teardown is included or excluded intentionally. For asynchronous systems, decide whether wall time, CPU time, queue delay, or throughput answers the question.

Before enforcing a strict CI ratchet, run the unchanged benchmark against itself (an A/A or equivalent stability check) across the ordinary CI environment and workload variation. Record its false alarms, spread, failures, and timeouts. Set any threshold beyond routine noise and chosen with the predeclared practical gain in mind; if those ranges overlap, keep the signal diagnostic until measurement or environment stability improves. An A/A check tests the measurement and gate, not whether a change helps users.

For noisy comparisons, repeat baseline and candidate in alternating or randomized blocks under the same fixture and environment. Preserve each run and report distributions and spread, then compare the observed change with both routine noise and the predeclared practical threshold. Choose an uncertainty method that fits the measurement and design; more runs do not fix a biased or unrepresentative fixture. There is no universal run count, p-value, or confidence-interval cutoff. A deterministic count can be checked exactly only if its environment and measurement are genuinely stable.

Count every attempted run, including errors, crashes, and timeouts. Report completion and failure rates beside latency. Define timeout handling before comparing: a timeout is a failed attempt and may be reported at its known bound for a latency summary only when that rule is explicit; never silently drop it or treat it as a fast successful result. Keep successful-run latency distinct from end-to-end success probability.

Calibrate a proxy for a named workload domain, not for “performance” in general. Compare proxy movement with user-relevant wall time and, when available, field outcomes across representative improvements, plausible regressions, and boundary cases. Check whether it misses harmful changes, including correctness and resource countermetrics, and document exceptions. Two concordant examples are not enough to establish a general relationship. If prediction is weak or exceptions matter, retain the proxy as diagnostic evidence or narrow its claimed domain. A CI gate needs a stable fixture, a demonstrated relationship in its intended domain, a threshold above ordinary noise and aligned with practical impact, and an explicit review process for refreshing the fixture or threshold.

For field verification, compare like with like: use build and platform plus relevant workload or traffic characteristics, rollout cohort, and time window. Preserve assignment/cohort when available; show material slices as well as the aggregate so changes in population mix do not masquerade as a treatment effect. State missing telemetry and exclusions, and keep failed or timed-out journeys in the outcome denominator where the metric is a success rate.

Never claim statistical certainty from a single measurement or infer field impact from a synthetic-only win.

## Sources

- [Anthropic: How we made claude.ai 3x faster](https://claude.dev/blog/how-we-made-claude-ai-faster/) — journey definitions, calibrated lab proxies, CI ratchets, field follow-up.
- [web.dev: Core Web Vitals workflows](https://web.dev/articles/vitals-tools) — field measures user experience; lab tools help diagnose under fixed conditions.
- [OpenTelemetry: instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/) and [signals](https://opentelemetry.io/docs/concepts/signals/) — metrics, traces, logs, profiles, and their distinct roles.
- [Go diagnostics](https://go.dev/doc/diagnostics) — profile selection and the risk that diagnostics perturb each other.
- [Google Benchmark: reducing variance](https://github.com/google/benchmark/blob/main/docs/reducing_variance.md) — sources of host variance; [user guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md) — repetitions, warmup, and interleaving.
- [Google Benchmark: random interleaving](https://github.com/google/benchmark/blob/main/docs/random_interleaving.md) — repeated interleaved observations and their tradeoffs.
- [Kohavi et al., Controlled Experiments on the Web](https://www.exp-platform.com/Documents/GuideControlledExperiments.pdf) — A/A testing, power and variability, assignment, and segment analysis.
- [Kohavi et al., Controlled Experiments at Scale](https://www.exp-platform.com/Documents/2013%20controlledExperimentsAtScale.pdf) — guardrails, data quality, and risks from many metrics and slices.
