# Diagnostics and Communication

## Minimum diagnostic pass

For every fitted model, inspect:

1. outcome and predictor distributions, including zeros, bounds, skew, and tail mass;
2. missingness and selection patterns, not only missingness percentages;
3. residuals or observed-versus-expected behavior on the correct link and response scales;
4. variance, overdispersion, heteroscedasticity, serial correlation, and cluster dependence;
5. leverage, influence, sparse cells, separation, collinearity, and unstable coefficients;
6. calibration, ranking, threshold behavior, and segment or time stability;
7. sensitivity to transformations, distribution/link, exclusions, tail treatment, and windows.

A diagnostic is evidence about a failure mode, not a ritual pass/fail stamp. Explain what the
finding changes: estimator validity, prediction quality, uncertainty, decision impact, or
only presentation.

## Interpretation discipline

Use the scale the decision-maker actually needs. Translate coefficients only after stating
link, reference category, exposure, units, and conditioning. Do not describe an association
as an effect without an identification strategy. Do not treat a significant coefficient as
important without magnitude and decision context. Report intervals with their type and
coverage assumptions.

## Report structure

Use `templates/model-report.md`:

- answer the decision first;
- define population, grain, target, horizon, and data boundary;
- describe method and why it fits;
- report estimates, forecasts, calibration, and uncertainty with denominators and units;
- show diagnostics, robustness, and unresolved gaps;
- separate observed facts, model inferences, assumptions, and non-conclusions;
- state permitted use, monitoring, and review triggers;
- make reproduction possible.

## Effective graphics

Choose a display for the question: distributions for skew and tails, observed-versus-fitted
plots for calibration, residual plots for structure, coefficient or effect plots for
comparisons, forecast bands for time, and development heatmaps for claims. Label units,
reference populations, interval definitions, and data cutoffs. Avoid decorative precision,
truncated axes that alter the comparison, unlabeled error bars, and a single aggregate that
conceals a failing segment.

## Executive translation

A concise report can still retain material caveats. Convert caveats into consequences:
“the probability ranking is strong, but probabilities are under-calibrated in the newest
segment, so expected-cost use should wait for recalibration.” This is more useful than
omitting the caveat or burying it in a technical appendix.
