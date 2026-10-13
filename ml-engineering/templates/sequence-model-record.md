# Tabular/sequence representation study

User decision/output, harm and authority:
Candidates: aggregate+linear/tree; row encoder; event/sequence encoder; contextual LLM:
Comparable permitted information and tuning/pretraining/serving budgets:

## Input and labels

Entity/event IDs, schema and source revisions:
Event time versus actual availability; prediction origin/current target:
Lookback, irregular time/ties, late/missing/out-of-order events:
Label definition, horizon, maturity, intervention/censoring:
Feature joins/aggregates reviewed for post-outcome information:

## Representation and objective

Architecture; feature versus event tokens; padding/attention/pooling:
Unlabeled pretraining period/entities and inductive/transductive policy:
Augmentations/masks/pair identities and semantic checks:
Encoder/head frozen or adapted; loss/imbalance handling; seeds:
Batch/cohort attention semantics; state reset/isolation:

## Evaluation

Forward/new-entity split; target IDs; gap/purge policy in actual time units:
Train-only preprocessing; development/calibration/sealed-test roles:
Baseline and supervised-only/pretrained ablations:
Proper probability scores and fixed-budget harm metrics; segment regressions:
Independent-group and seed uncertainty; missing/failed tasks retained:
Whole-task assembly/encoder/policy latency and resource peaks:

## Delivery

Source/model/head/code/environment/config hashes:
Saved state/category schema/calibration; fresh reload and entity-reset tests:
Stage status: metadata screen / encoder runtime / task eval / online replay / rollout:
Rollback artifact, state compatibility and owner:
Prepared stages are not executed; declared metadata is not original-source proof.
