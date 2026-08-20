# Validation and Calibration

## Match validation to use

The evaluation boundary must reproduce deployment information flow. Choose the unit of
splitting before fitting or tuning the final model.

- **Random holdout:** only when observations are exchangeable enough and no entity or
  temporal leakage is possible.
- **Grouped split:** keep policyholders, firms, households, claims, or other dependent
  entities entirely on one side when reuse would inflate performance.
- **Blocked split:** use contiguous periods for temporal deployment or regime-sensitive data.
- **Rolling-origin evaluation:** train on the past, forecast a defined horizon, advance the
  origin, and summarize performance across origins.
- **Nested validation:** keep model selection and final performance estimation separate when
  tuning or comparing many candidates.
- **Embargo/gap:** reserve a gap when labels, features, or development information overlap
  across the boundary.

Scaling, feature selection, imputation, target encoding, resampling, calibration, and
hyperparameter selection are all fitted operations. Fit them within the training boundary.
Record data revisions and feature availability timestamps.

## Metrics by output

| Output | Useful evidence |
|---|---|
| Continuous mean | MAE/RMSE with scale, residual checks, interval coverage, segment stability |
| Count/rate | Deviance or proper count score, exposure-aware error, calibration, aggregate error |
| Probability | Log loss or another proper score, reliability/calibration curve, Brier score, discrimination |
| Quantile/tail | Pinball loss, coverage, exceedance behavior, tail sensitivity, aggregate impact |
| Forecast distribution | Horizon-specific proper score, interval coverage, bias, rolling stability |
| Time-to-event | Concordance only as a supplement, calibration by horizon, survival/Brier measures, censoring checks |
| Decision | Expected cost, threshold performance, capacity/capital impact, abstention and override behavior |

Do not choose a metric solely because it is familiar. AUC measures ranking, not whether a
0.20 prediction means approximately 20% in the relevant population. A low average error
can hide unacceptable tail or segment behavior.

## Calibration

Assess calibration on held-out data and by meaningful time, geography, portfolio, and risk
segments. Use reliability summaries, proper probabilistic scores, and uncertainty bands
where sample size permits. Recalibration is a fitted transformation and must obey the same
information boundary. Monitor calibration drift separately from ranking drift.

## Uncertainty

Report the source and type of each interval or distribution: sampling, parameter,
process, model-form, scenario, or data-quality uncertainty. Bootstrap only within a design
that respects clusters, time, censoring, and the estimand. Do not label a narrow standard
error as total decision uncertainty.

## Stress and sensitivity

Vary assumptions that could change the action: exposure, trend, tail threshold, link or
distribution, missing-data treatment, feature availability, regime, dependence, and
aggregation. Keep sensitivity scenarios separate from the primary estimate. A stress test
is not a claim that the stressed scenario is likely; it reveals decision fragility.

## Release evidence

A release packet should contain the frozen data definition, split manifest, code and
environment, candidate comparison, metrics with denominators, calibration, diagnostics,
sensitivity, known limitations, monitoring thresholds, owner, review date, and rollback or
retirement trigger. Green training metrics are not release evidence by themselves.
