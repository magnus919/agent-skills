# Experiment and rollout decisions

Read this when comparing candidates, adding a performance gate, or preparing a user-visible rollout.

1. Write a falsifiable hypothesis: bottleneck, mechanism, affected workload, predicted outcome and countermetrics. Name the minimum practical gain before seeing results.
2. Hold the workload and environment constant. Use one primary change per comparison when possible. If several changes interact, measure the combined outcome and avoid attributing the whole gain to one.
3. Capture baseline and candidate raw results. For noisy timings, repeat them in alternating or randomized blocks to limit drift, retain the individual observations, and report run counts, distributions, and spread. Compare the observed change with the predeclared minimum practical gain and ordinary run-to-run noise. Select an uncertainty method that fits the data and comparison; there is no universal repetition count, p-value, or confidence threshold. If noise overlaps the practical threshold, call the result inconclusive.
4. Count failed and timed-out attempts in the record. Report success/failure rates beside successful-run latency. Define timeout treatment before analysis and do not silently omit failures from an outcome denominator.
5. Preserve correctness and inspect tradeoffs: errors, output equivalence, memory, CPU, network, startup, accessibility, maintainability, and behavior on slow devices or large inputs. Add tests for the actual failure mode where feasible.
6. Classify: **supported in lab**, **unsupported**, or **inconclusive**. A proxy-only change is not a user win. A noisy result remains inconclusive; do not tune the workload until it passes.
7. Review the change with a human owner. Set rollout size, observation window, success/abort thresholds, and rollback target. Follow project authority for external mutations. A feature flag helps reversibility but creates cleanup work; give it an owner and removal condition.
8. After rollout, compare matched field slices by build, platform, workload or traffic, cohort, and time window. Keep assignment intact where available, inspect relevant slices and aggregate, and include failures and timeouts in success-rate denominators. Accept as **field verified** only when the user outcome improves without unacceptable harm. If not, disable/revert or investigate and repeat.
9. Before a strict ratchet, compare the unchanged benchmark with itself to learn its ordinary variability and false-alarm behavior. Gate only when a stable, documented fixture predicts the intended user-relevant outcome in its stated domain, includes plausible regressions and exceptions in calibration, and uses a threshold above ordinary noise and chosen with the practical gain in mind. If these conditions are not established, keep the metric diagnostic. Document intentional fixture and threshold refreshes.

Stop after a bounded non-converging pass (for example, three distinct measurements or hypotheses) and report the evidence gap and next owner decision. Avoid endless micro-optimizations without a user-relevant objective.

Do not interpret an A/A stability check as evidence of a treatment effect, proxy calibration on only favorable examples as a general guarantee, or matched-slice observational data as randomized causal evidence. State which evidence supports each decision.

For rationale on A/A checks, workload assignment, guardrails, and interleaved benchmark observations, see the primary sources in [measurement-and-benchmarks.md](measurement-and-benchmarks.md#sources).
