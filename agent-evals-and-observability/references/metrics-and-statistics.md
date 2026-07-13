# Metrics and Statistical Reasoning

Report a profile by task and slice: task outcome; grounding to supplied or retrieved evidence; tool selection, arguments, ordering, authorization, and side effects; safety; reliability and recovery; cost/resource use; and latency. Include failures, timeouts, abstentions, and missing data rather than conditioning only on completed runs.

Compare candidate and baseline on the same cases when feasible. Preserve paired outcomes, effect sizes, uncertainty intervals suited to the metric, and run-level conditions. For stochastic systems, repeat runs when stochastic variation can change the decision; report variability rather than treating one draw as stable.

Choose sample size through the decision risk, baseline rate, metric distribution, planned pairing, slice coverage, minimum detectable effect, and available resources. Do not use fixed sample quotas. Plan power or sensitivity before a consequential comparison. A non-significant result does not show equivalence.

Predeclare primary comparisons where practical. Investigate multiple comparisons, changing composition, missingness, base rates, selection effects, temporal/environment confounders, and aggregate reversals. Use correction or hierarchical interpretation appropriate to the question, and show slice results instead of relying on a blended average.

## Define Each Measure

A metric contract names the property; unit or label set; population and denominator; included failures, retries, and abstentions; aggregation and tail/slice views; preferred direction; data source; measurement error; baseline; decision threshold or comparison rule; owner; and failure behavior when data is missing. Token counts are not automatically cost, latency averages can hide tail harm, and user feedback is a selected noisy signal rather than ground truth.

Keep hard invariants categorical. Report ordinary indicators separately, for example:

- task outcome and completion evidence;
- grounded claims or evidence use, with the actual source context available to the grader;
- tool selection, arguments, authorization checks, ordering, and committed side effects;
- safety/privacy/policy outcomes and grader false-positive/false-negative behavior;
- reliability, retries, recovery, loops, timeouts, and escalation;
- latency distribution and time to useful outcome; and
- resource use and monetary cost from the billing/usage source that actually defines them.

## Choose Comparison Methods From The Data

For paired binary outcomes, preserve the discordant case pairs and use an interval/test suitable for paired proportions. For continuous or heavy-tailed outcomes, consider paired bootstrap, permutation, or a justified model and report distributional views. For ordinal or rubric scores, preserve the scale and rater structure instead of pretending equal numeric distance. If a release needs to establish practical equivalence or non-inferiority, predefine the acceptable margin and design for that question; failure to detect a difference is not equivalence.

Choose repetitions and sample size from estimated variance/base rate, minimum effect worth detecting, pairing, slice coverage, desired error risk, and decision consequence. Run sensitivity analysis when inputs are uncertain. If the design cannot resolve the decision, report insufficient evidence rather than converting a wide interval into a pass.
