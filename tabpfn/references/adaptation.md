# Weight adaptation and bounded recovery

## Ordinary fit versus fine-tuning

Ordinary `TabPFNClassifier.fit`/`Regressor.fit` prepares labeled inference context.
The official fine-tuning guide separately exposes `FinetunedTabPFNClassifier` and
`FinetunedTabPFNRegressor` with gradient-based adaptation. Do not describe context
fitting as optimizing transformer weights or assume an Unsloth LoRA script can
train these models. Confirm exact class imports, parameters, checkpoint support
and dependency versions in the selected release.

Before adaptation compare context-only inference with a simple/tree baseline and
reserve a development set for epochs/learning rate/checkpoint selection. Freeze
context subsampling, ensemble settings and transforms; otherwise the comparison
changes multiple variables. Preserve label/group/availability cutoffs and final
holdout. Use a short finite-loss/load-save-reload trial before a full budget.
Record optimizer/scheduler/RNG/checkpoint state, memory and wall time; a new
fine-tune from a weight file is not a stateful continuation. Keep original and
adapted artifacts and preserve failing runs.

## Capacity and schema triage

- OOM: measure context size, features, ensembles, concurrent requests and cache;
  reduce one registered dimension or choose another supported checkpoint. Record
  rare-class/context changes. Do not bypass size guards as proof of compatibility.
- CPU slow: distinguish actual device placement from CUDA installation. Do not
  claim current CPU guard thresholds imply a latency guarantee.
- Column/category mismatch: reconstruct the saved schema and train-only transforms;
  inspect model's supported dtype/text path, not arbitrary one-hot rewriting.
- Unseen target class: restore task/class mapping or register a new model task;
  softmax over known classes cannot recognize every unknown class automatically.
- Divergent probabilities after reload: compare checkpoint/context/class order,
  package versions, ensemble/subsample randomness and calibration before retraining.
- Authentication/download failure: separate license/account access from API/package
  compatibility. No auto-acceptance, fallback provider or global credential changes.

Three diagnostic passes without new evidence produce a minimal versioned
reproducer and specific missing prerequisite. Preserve private data locally; use
a harmless representative fixture for public reports. Successful load, low loss
or cleared audit is not a task-quality result.
