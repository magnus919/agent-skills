# Experiment and rollout decisions

Read this when comparing candidates, adding a performance gate, or preparing a user-visible rollout.

1. Write a falsifiable hypothesis: bottleneck, mechanism, affected workload, predicted outcome and countermetrics. Name the minimum practical gain before seeing results.
2. Hold the workload and environment constant. Use one primary change per comparison when possible. If several changes interact, measure the combined outcome and avoid attributing the whole gain to one.
3. Capture baseline and candidate raw results. Compute absolute difference in the unit users experience and relative difference against baseline. Show run counts and variability; a small percentage on a tiny path can be immaterial.
4. Preserve correctness and inspect tradeoffs: errors, output equivalence, memory, CPU, network, startup, accessibility, maintainability, and behavior on slow devices or large inputs. Add tests for the actual failure mode where feasible.
5. Classify: **supported in lab**, **unsupported**, or **inconclusive**. A proxy-only change is not a user win. A noisy result remains inconclusive; do not tune the workload until it passes.
6. Review the change with a human owner. Set rollout size, observation window, success/abort thresholds, and rollback target. Follow project authority for external mutations. A feature flag helps reversibility but creates cleanup work; give it an owner and removal condition.
7. After rollout, compare matched field slices by build and platform and inspect error/correctness countermetrics. Accept as **field verified** only when the user outcome improves without unacceptable harm. If not, disable/revert or investigate and repeat.
8. Ratchet only a stable benchmark whose measured signal predicts the outcome and whose threshold exceeds ordinary noise. Preserve the baseline fixture and document how to refresh it intentionally.

Stop after a bounded non-converging pass (for example, three distinct measurements or hypotheses) and report the evidence gap and next owner decision. Avoid endless micro-optimizations without a user-relevant objective.
