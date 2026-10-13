# Data, calibration and matched evaluation

## Prediction-time evidence

Define what each row represents and when its features and labels became available.
For delayed fraud outcomes, event timestamp and label maturity are different facts.
Train only on labels available at the training cutoff; future features cannot be
made legitimate by random splitting. Group related users/cases/documents before
splitting. The bundled audit uses strict disjoint groups plus forward holdouts;
a deployment requiring repeated entities needs a separately designed temporal
protocol rather than falsely rewriting IDs to clear the screen.

The manifest records typed feature arrays and target values, group IDs, prediction,
feature-availability and label-availability timestamps. The time fields are declared
metadata, not verified source lineage. All timestamps must be timezone-aware.
Capacity policy is supplied for the exact selected checkpoint/backend; defaults
cannot certify hardware or current vendor limits. Exact feature overlap is a
review signal, not proof all repeated valid observations are fraudulent leakage.
Clean hashes cannot exclude near-duplicate or pretraining contamination.

## Context and preprocessing

Maintain one feature schema/order/dtype contract across train and prediction.
Fit learned transforms on training only. Some newer TabPFN interfaces handle
categorical strings/missing data and text internally; that is version-specific,
not permission to concatenate unrelated text or discard schemas. For tree/linear
baselines, use their appropriate train-only transformations so a comparison does
not penalize them for an unsuitable preprocessing path. Inspect category coverage,
empty columns, high cardinality, nonfinite numeric values and unseen target classes.

The labeled train context participates in each prediction. Holdout labels must
not enter context, checkpoint selection, ensemble choices or calibration. Separate
model-selection development data from calibration and final tests when both are
needed; the three-split helper is not a replacement for all experimental split roles.
Do not compute imputation/scaling/encoding from an entire table before CV. Repeat
context/model construction per fold with the permitted training subset.

## Quality contract

Classification: record class order, prediction labels, log loss/Brier and reliability
slices, precision/recall at fixed review/error budgets, rare-class and abstention
coverage. AUROC can hide class imbalance. Fit calibration/thresholds only on their
reserved development/calibration split; native probabilities are not universally
calibrated. For sampled prevalence, correct interpretation of predictive precision
before applying production thresholds.

Regression: MAE/RMSE by subgroup/range, bias, outlier behavior and interval coverage
where supported. A point predictor or advertised uncertainty is not a verified
prediction interval. Evaluate extrapolation/shift, missingness and temporal drift.
Feature importance does not identify a causal effect.

Match data/features/tuning/ensemble/context budgets and measurement boundary
across baseline/candidate. Record cold start, fit/context setup, complete prediction
latency at requested batch/concurrency, peak RAM/VRAM and repeated-seed variation.
Include mislabeled, rare, shifted, malformed, OOM/timeout and unavailable-label
cases. Do not omit failures from the denominator or treat them as task truth.
Route statistical uncertainty to data-scientist and deployment model-lineage/drift
requirements to ML Engineering.
