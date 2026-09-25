# Fine-tuning GLiNER2 for Decide-style classification

Checked 2026-09-25 against Fastino's [training tutorial](https://github.com/fastino-ai/GLiNER2/blob/main/tutorial/9-training.md), [LoRA adapter tutorial](https://github.com/fastino-ai/GLiNER2/blob/main/tutorial/10-lora_adapters.md), and [Decide checkpoint](https://huggingface.co/fastino/GLiNER2.5-Decide). This is an upstream-supported **GLiNER2 classification training path**, not a verified claim that every trainer option works when initialized from the specialized Decide checkpoint.

## Pick the starting checkpoint deliberately

Fastino's training examples initialize `AutoExtractor` from `fastino/gliner2-base-v1` or `fastino/gliner2.5-base-v1`. The Decide model card documents inference, but does not provide a complete fine-tune-from-Decide recipe. For a first reproducible experiment, use the documented `gliner2.5-base-v1` training path. To continue training `fastino/GLiNER2.5-Decide`, first run a tiny load, forward, backward, save, reload, and classification smoke test with pinned `gliner2` and checkpoint revisions. Compare both starting points on the same held-out labels before selecting one. Do not assume the Decide checkpoint's specialized behavior survives base-model fine-tuning.

## Represent the decision as classification

Use a single-label `Classification` for a mutually exclusive route and `multi_label=True` only when multiple labels may be true. Include an explicit `other` or review label when the options are not exhaustive. Keep task names, label meanings, option ordering, and input formatting stable across training and serving. GLiNER2 classification labels are not Jev/Laya Choice distributions, Score values, or Noul probabilities.

```python
from gliner2.training.data import InputExample, Classification

row = InputExample(
    text="The second subscription charge should be refunded.",
    classifications=[Classification(
        task="support_route",
        labels=["billing", "technical", "other"],
        true_label="billing",
    )],
)
```

The [upstream tutorial](https://github.com/fastino-ai/GLiNER2/blob/main/tutorial/9-training.md#classification) also documents JSONL input, `TrainingDataset.validate`, deterministic splits, and training a classification head alongside extraction tasks. Use independently labeled, provenance-tracked examples. Deduplicate near-identical states across train, validation, and test. Keep the frozen decision battery and any final head-to-head benchmark cases outside the training and tuning sets. Do not use Jev outputs as training or distillation labels without a separate agreement review.

## Local tools and first experiment

The supported stack is `gliner2` plus its `gliner2.training` modules: `ExtractorTrainer`, `TrainingConfig`, `InputExample`, and `Classification`. Pin package/source and model revisions. Fastino documents full fine-tuning with separate `encoder_lr` and `task_lr`, evaluation checkpoints and early stopping, as well as mixed precision, gradient accumulation, and gradient checkpointing for memory pressure. Its LoRA mode uses `use_lora=True`, `lora_r`, `lora_alpha`, `lora_target_modules`, and `save_adapter_only`; inspect the saved artifact and reload it under the same pinned runtime before deployment. The tutorial's prose alternates between adapter-only and merged-weight descriptions, so do not infer an artifact format from the flag name alone.

Start with a small, representative train/validation split, then compare full fine-tuning and encoder-targeted LoRA only if the first run shows a useful signal. Fix the seed and split; log task mix, hyperparameters, effective batch size, trainable parameters, GPU memory, training time, checkpoint hash, and package version. Validate single-label and multi-label outputs separately. Tune `cls_threshold` only on validation data where multi-label selection is used.

Evaluate the saved and reloaded candidate against the unchanged baseline on held-out in-domain, out-of-domain, ambiguous, missing-evidence, and label-shift cases. Report per-label confusion, macro and rare-label measures, abstain/review coverage, and p50/p95 latency on the same hardware and request shape. Promote a candidate only when its downstream deterministic decision contract improves without unacceptable regressions; preserve the previous checkpoint for rollback.

Fastino also describes a hosted training API in the same tutorial. Treat that as a separate data-transfer and cost decision; verify that the desired starting checkpoint is listed as trainable before uploading any data.
