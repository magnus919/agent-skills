# Tabular foundation-model selection

A tabular foundation model learns inductive structure from pretraining datasets
and adapts predictions to a labeled table through in-context learning or optional
weight adaptation. This is a different deployment artifact from a tree ensemble,
a generative text model returning a number, and a time-series model trained on
ordered events. The labeled context and its preparation are part of inference.

## What the evidence supports

Early TabPFN work studies synthetic priors and approximate posterior predictive
behavior on small tables. Newer TabPFN reports, TabICL/TabICLv2 and their author
implementations extend data shapes and efficiency under their own conditions.
Do not interpret prior predictive modeling as verified probabilistic calibration
for every shifted domain. Synthetic structural-causal priors do not identify a
causal effect in observed data. Read exact source scope in the family evidence
record and route operational TabPFN work to the `tabpfn` skill.

TabPFN and TabICL are distinct named systems. Their API resemblance does not
establish compatible checkpoints, preprocessing, class support, licenses,
fit/predict cost boundaries or local-device placement. Benchmarks claiming
superiority over boosted trees motivate comparison, not automatic deployment.
Keep a simple/tree incumbent with comparable permitted features and tuning time.

## Study design

1. Specify classification/regression, future prediction population, harm/budget,
   feature availability, delayed label maturity and dependency groups. Select
   IID, grouped, temporal or combined folds to match deployment rather than
   maximize a leaderboard score.
2. Pin checkpoint, package, inference-context selection, transforms, class map,
   ensembles, calibration and optional adaptation. Labeled holdout rows cannot
   enter the training context; repeat context construction inside each fold.
3. Evaluate linear/tree/ICL candidates on the same rows, feature information,
   hyperparameter/ensemble wall-time budgets and decision thresholds. Fit all
   learned preprocessing using the fold's training data only.
4. For classification measure proper probability scores and reliability plus
   precision/recall at fixed operational error/review budgets; report rare classes,
   abstention, prevalence changes and unknown-label handling. For regression
   report bias, tail/subgroup error and interval coverage if claimed.
5. Record whole-task resource/cost: initialization, context fit, first/warm batch,
   subsampling/ensembles, peak VRAM/RAM, model cache and concurrent replication.
   A ceiling of rows/columns is not a joint resource guarantee.
6. Reserve development/calibration/final roles. Explicit weight fine-tuning is
   a separate candidate from context-only inference; tune on development data
   and preserve checkpoint/optimizer lineage. Do not call ordinary fit training
   weights without checking the actual operation.
7. Fresh reload must preserve both weights and labeled context/schema/calibration.
   Gate on actual task behavior and every registered operational constraint;
   original/model-report metrics are not release approval.

## Licensing and privacy are selection inputs

Repository code and downloaded weights may have different terms, including
non-commercial/non-production restrictions by checkpoint generation. Hosted APIs
may upload table data or use different preprocessing and ensemble behavior. A
locally installed package may still authenticate, fetch weights or emit telemetry.
Record actual authorization/egress/serialization evidence; don't equate open code,
local path or syntactically valid model record with an approved private deployment.

## Failure hypotheses and alternatives

- Wrong class order or context/schema mismatch can explain bad probabilities
  before adaptation is warranted.
- Memory/latency may be dominated by context/ensemble/concurrency rather than
  checkpoint file size. A sampled smaller context changes task quality too.
- Near-duplicate groups, labels observed after the training cutoff and future
  aggregates can explain impressive retrospective metrics.
- Text-heavy/high-cardinality tables may need checkpoint-specific representations;
  denying a comparator equivalent information confounds model choice.
- Forecasting by temporal featurization is a route to test, not proof a tabular
  model handles arbitrary sequences. Use rolling origins and leakage-aware lags.

Finish with a matched comparison and explicit applicability decision, or a
prepared experiment with missing execution evidence. Unavailable weights/hardware
are not reasons to claim fit or to silently substitute a hosted provider.
