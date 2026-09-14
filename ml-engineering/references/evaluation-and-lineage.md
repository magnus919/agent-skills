# Evaluation, lineage, and production response

Use this reference for model-quality decisions that must remain comparable after training, adaptation, deployment, or data change.

## Configuration and metric choice

Start with the deployment decision, not a convenient metric. State the task, harm of errors, decision threshold, acceptable tradeoffs, and the smallest representative evaluation set. Select metrics that expose those risks (for example, per-class precision/recall for imbalanced classification, calibration when probabilities drive action, and latency/throughput when serving capacity is part of the decision). Record the metric definition, aggregation, weighting, and pass threshold.

For stochastic training or generation, repeat the same comparison with controlled seeds or a declared sampling protocol. Report the distribution or uncertainty across repeats and inspect per-capability/per-example deltas. An aggregate change within observed run-to-run variation is inconclusive; a statistically significant result still does not authorize a release if a critical capability regresses.

## End-to-end lineage

A promotable model needs links across the whole chain:

`source snapshot → dataset revision → feature definitions and cutoff → split/eval revision → code and configuration → run/artifacts → evaluation report → registered model → serving image/configuration → deployed endpoint`

Store immutable identifiers or hashes for each link, plus the owner, timestamp, environment, and transformation boundary. A model file or experiment URL alone is insufficient. If a link is missing, label the result non-reproducible and block promotion until the gap is accepted by the responsible owner.

## Temporal feature parity

For every feature, define its event time, availability time, source revision, transformation, and permitted lookback window. Training and batch evaluation must use only data available at the prediction timestamp. Online serving must run the same semantic transformation or consume a versioned feature definition. Compare offline and online distributions on a replay or shadow sample; investigate differences as training-serving skew before interpreting quality changes.

## Drift and response

Monitor system signals (errors, latency, throughput, resource saturation), input/feature distributions, prediction distributions, and outcome quality when labels arrive. Define thresholds, minimum sample/window, owner, and action before deployment. A drift alert is a signal to investigate, not proof that retraining is correct: check schema/source changes, seasonality, segment mix, label delay, and metric integrity first.

The response options are bounded: continue with a documented observation, repair the data/feature path, recalibrate or retrain, route to human review, roll back to the last known-good model, or retire the service. Choose using the critical-capability threshold, lineage completeness, cost/latency budget, and rollback readiness. Validate the candidate on the frozen regression set and a recent production slice before ramping traffic.

## Training, adaptation, and serving tradeoffs

Treat prompting, adapter fine-tuning, full fine-tuning, retrieval augmentation, quantization, and a serving-engine change as different hypotheses. Compare them against the same baseline and task eval, while recording data freshness, quality delta by capability, latency/throughput, memory, cost, operational complexity, and rollback path. Keep the smallest intervention that clears the target; do not spend training budget to solve a data, retrieval, or serving bottleneck without evidence.

This is methodology. Commands and lifecycle details for a named model server, orchestrator, registry, feature store, or monitoring product belong to that tool’s skill.
