# Self-supervised tabular representations

Read for neural tabular classification/regression and pretraining on unlabeled
rows. Distinguish dataset-specific representation learning from TabPFN/TabICL
in-context inference, and feature-token attention from ordered event attention.
The model family does not decide the task's information requirements.

## Architecture and objective map

| Candidate | Represented structure | Adaptation signal | Main comparison concern |
|---|---|---|---|
| Linear/GBDT/MLP/ResNet | Engineered row features | Supervised labels | Strong tuned baseline and train-only preprocessing |
| TabTransformer | Contextual categorical-feature embeddings | Supervised plus optional unlabeled pretraining | Numeric/categorical fusion, missing/noisy feature protocol |
| FT-Transformer | Feature tokens within a row | Supervised task | Matched tuning/training protocol; no universal winner |
| SAINT | Feature and inter-row attention | Supervised and contrastive pretraining | Batch/cohort composition and inductive/transductive boundary |
| TabNet | Stepwise feature selection | Supervised plus optional reconstruction | Selection masks not causal explanation; comparable baseline |
| VIME-style method | Masked/corrupted feature recovery and consistency | Unlabeled reconstruction then labels | Corruption reflects deployment and split isolation |

The founding papers report gains in their benchmark settings. The FT-Transformer
study explicitly finds no universally superior solution. Booking.com's fraud
study demonstrates a self-supervised tabular-transformer route in its own
production regime; its rows/feature tokens are not automatically a temporal
transaction-sequence architecture. Keep numerical gains author-reported until
reproduced on a matching dataset and protocol.

## Pretraining data is still experimental exposure

Unlabeled examples can leak future distribution, entity identity, target-derived
features or final-test characteristics. Declare inductive versus transductive
usage before training. By default pretrain only on the permitted training period/
entities, then hold the final cohort out of representation learning, augmentation
selection, feature pruning and classifier tuning. A lack of target labels does
not make future data harmless. Track raw source availability, not only row event time.

Build categorical vocabularies, scaling/imputation and learned encodings inside
each training fold. Unknown categories and missing values need explicit semantics;
new category IDs are not arbitrary numeric magnitudes. Review target encodings,
post-outcome status flags, aggregates and joins. A self-supervised task can recover
features that are themselves illicit at deployment.

## Corruption and augmentation design

Masking/reconstruction or contrastive views should retain task-relevant semantics.
Record features allowed to change, missingness patterns, replacement distribution,
probability/severity, random seeds and positive/negative pair identity. Do not
pair different customers as “the same example” merely because rows are adjacent.
Augmentations that invert an outcome-driving amount/timing/category may destroy
labels; evaluate that harm separately. More pretraining objective improvement
is not evidence the downstream classifier improved.

For row-attention architectures, batching other examples changes the input context.
Verify whether final-test rows inform each other or the training representation,
which labels are visible, and whether changing batch order/composition changes
predictions. That can be a legitimate declared transductive design, but must not
be compared to an inductive baseline as if information access were identical.

## Controlled experiment

Compare supervised-only and pretrained versions of the same architecture, plus
strong linear/tree/ResNet baselines. Freeze features, splits and selection/tuning
budgets; separately account for unlabeled exposure, pretraining cost and inference
batch/cohort settings. Include label-scarcity learning curves, subgroup imbalance,
missing/noisy/categorical shift and temporal generalization. Fine-tune encoder and
head policies explicitly; frozen-head versus full updates are different candidates.

Report proper probability metrics/calibration and operational precision/recall at
fixed harm/review budgets. Preserve preprocessing/category schema, model/head,
pretraining and supervised configuration, data/time hashes, batch semantics and
calibration object. Independent reload/task checks precede promotion. Feature
attention/selection can aid inspection but is not proof of causal contribution.
Route explanation/calibration methodology to `data-scientist`.

The author TS2Vec/VIME/FT repositories are implementation discovery routes, not
validated package recipes. Old Torch/scientific dependency pins need isolated
compatibility checks; never upgrade a shared host to make a paper demo run.
