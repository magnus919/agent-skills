# Transaction and event-sequence modeling

Read when the task depends on event order, intervals, bursts or changing behavior,
not merely one row's features. First compare time-aware aggregates with a simple
classifier; then sequence encoders and contextual LLM review under equal permitted
information. The need for history does not establish the need for language generation.

## Define the event and decision contracts

An event has an entity, immutable ID, event time, availability time and permitted
features. The target transaction and prediction origin are separate from history.
Exclude the current target from its history and exclude outcome labels/post-decision
status. Define permitted lookback and update latency, simultaneous-event tie order,
late/out-of-order arrivals, missing events, repeated IDs and cross-entity joins.
Retrospective storage contains information the online system may not have had.

Choose the output: next-event/amount forecast, sequence-level fraud classification,
anomaly score, representation or horizon-specific uncertainty. They require
different targets and evaluation. A forecasting architecture's quantile objective
is not automatically a calibrated fraud classifier.

## Candidate representations

- Rolling aggregates + linear/trees: counts, recency, amount changes and rates,
  with explicit event/availability cutoffs. Test whether these explain the gain.
- Recurrent/temporal convolution/causal transformer: event tokens and interval
  encoding, bounded lookback, masks and pooled or target-specific classifier head.
- Contrastive representation such as TS2Vec: encoder learned from permitted
  augmented contexts, then a classifier/probe; timestamp and sequence-level
  representations have different pooling/cost/semantics.
- Forecasting models such as TFT: static, known-future and historically observed
  covariates plus horizon-specific outputs. Future calendar covariates can be
  known; future observed transaction outcomes cannot be made “known future.”
- Contextual language model: serialized sequence and guidance. Budget parsing,
  context truncation and generation; benchmark against history-aware alternatives.

Document irregular time, amount/categorical embeddings, padding, maximum events,
attention direction, pooling, loss and label/head semantics. Bidirectional encoders
may be valid over a history entirely before the prediction origin; “bidirectional”
alone is not leakage. Conversely a causal attention flag does not fix leaked
features or future preprocessing. Record state/cache reset across entities and
sessions, including serving restarts.

## Splits and windows

Define whether deployment predicts later events for existing entities or new
entities. Forward splits can legitimately share old historical events across
windows; shared history is not automatically label leakage. Entity holdout uses
disjoint entities, optionally with temporal constraints. Avoid randomly splitting
near-identical target windows and counting them as independent evidence.

Build each window from available events at its prediction origin. Split target
IDs first, then construct allowed history with no held-out target outcomes. Fit
normalization/representation only on authorized training data. Purge/embargo
neighboring windows when shared target intervals or label horizons induce leakage;
choose the gap from task horizon/availability, not a convenient fixed integer.
`TimeSeriesSplit` addresses ordered folds but its documented comparable-duration
assumption requires equally spaced samples. Irregular transaction streams need
explicit time boundaries and entity logic, not a row-index gap called days.

## Offline metadata audit

From the skill root:

```bash
python3 scripts/audit_sequence_windows.py templates/sequence-windows.json
```

The synthetic manifest declares `forward` or `entity_holdout`, training/evaluation
cutoffs, and train/development/test windows. Each window has unique ID/target ID,
entity, prediction/label-availability timestamps and ordered events with event/
availability timestamps and explicit `contains_outcome: false` after review.
The audit allows consistent shared past history in forward mode; it checks future
context, immature labels, self-in-history, duplicates, entity boundaries, changed
event identity and forward fold overlap. Entity-holdout mode adds disjoint-entity
checks. Both modes require nontraining origins after the training cutoff.

Exit 0 clears declared metadata only; 1 means findings/invalid input; 2 is invalid
CLI arguments. The 16MiB input limit bounds scanning. Outputs contain counts and
window indices, not private IDs or event content. It does not inspect actual
feature values, source timestamp truth, outcomes hidden in aggregates, attention
masks, correct class probabilities, purge gaps, device placement or model behavior.
Do not change identifiers/timestamps to conceal failed checks. Use
`templates/sequence-model-record.md` for source and runtime evidence.

## Independent task and online validation

Score fixed decision origins under the same input availability. Report false
blocks, recall/value coverage at a fixed review budget, calibration, per-entity/
time/rare-pattern outcomes, missing-history behavior and uncertainty clustered
at the independent unit. Delayed labels need a maturity window; interventions
can censor which outcomes become observable. Anomaly reconstruction error is not
a verified fraud label or probability.

Compare window lengths/representations as separate controlled ablations. Log
history assembly, encoder/head, policy decision and end-to-end cold/warm latency
separately; token throughput alone misses data joins. Replay online feature assembly
at historical origins and use shadow/canary observation before policy rollout.
Version encoder/head/state schema, category map, transforms, label horizon,
calibration, thresholds and serving environment. Fresh reload must recover the
same bounded history/state behavior; never carry one entity's hidden state into
another. Rollback includes state/schema as well as model weights.
