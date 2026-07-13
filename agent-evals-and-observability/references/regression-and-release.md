# Regression, Triage, and Release Gates

For each change, identify the baseline, frozen dataset, configuration differences, primary decision metrics, uncertainty method, slices, and hard invariants. Compare paired runs where possible. A regression investigation begins with reproduction, trace and fixture review, configuration and environment differences, then a narrow root-cause hypothesis. Do not tune against the same incident case without recording contamination.

Turn confirmed incidents and near misses into candidates for new cases only after privacy, rights, redaction, and retention review. Classify whether the failure was task contract, trajectory, tool/environment, grader, data, deployment, or observability failure.

Risk-tier gates should have an authority, evidence owner, and one of: approve, approve with recorded conditions, hold for insufficient evidence, or block. Define hard invariants separately from statistical indicators. Examples of hard invariants include unauthorized action, unapproved sensitive-data disclosure, or an unreconciled harmful side effect. They cannot be offset by quality, cost, or latency results. Every gate records rollback/containment, monitoring during rollout, and the next review trigger.

## Compare Without Moving The Goalposts

Freeze candidate and baseline identifiers, dataset version, grader versions, fixtures, environment, sampling/randomization plan, primary comparisons, slices, and exclusions before the decision run. Use the same cases and comparable external conditions where feasible. Record provider/model drift, cache state, concurrency, tool/data versions, and instrumentation changes that could explain a delta.

Report case-level paired outcomes, slice deltas, uncertainty/effect size, hard-invariant results, failures/timeouts/missing data, cost/resource and latency distributions, grader disagreement, and observed confounders. Separate exploratory findings from preregistered release evidence. Do not tune on the held-out decision set and then report the same run as independent confirmation.

## Build The Gate

A release matrix should state for each dimension:

| Dimension | Evidence | Decision rule | Hard or statistical | Owner | Failure/insufficient-data action |
|---|---|---|---|---|---|
| Task/trajectory outcome | Cases, state checks, trace review | Risk- and slice-specific | Statistical or categorical | | |
| Safety/privacy/authorization/side effects | Adversarial cases and environment evidence | Explicit invariant | Hard | | |
| Reliability/recovery | Failure injection and deployed evidence | Workload-specific | Statistical plus hard cases | | |
| Cost/resource/latency | Metered distributions | Budget/SLO-specific | Statistical | | |
| Operability | Correlation, alerts, rollback rehearsal | Evidence checklist | Categorical | | |

The owner chooses a verdict from the documented outcomes, not from an unweighted average. Conditional approval names the condition, monitor, expiration/review trigger, and authority to halt. Rollout evidence must be linked to the exact released configuration, and rollback must account for state and side effects rather than only code version.
