# Training Run Record

Fill this record for every training or fine-tuning run, and commit it next to the
training code. A run that cannot be reproduced is not evidence. If a field is not
applicable, write `n/a` — do not leave it blank.

## Run Identity

- Run ID: `[fill: unique id, e.g. ft-support-lora-014]`
- Date: `[fill: YYYY-MM-DD]`
- Engineer: `[fill: name or handle]`
- Linked issue / ticket: `[fill: issue number or URL]`

## Model & Data

- Base model: `[fill: model id and commit/hash, e.g. meta-llama/Llama-3.1-8B-Instruct @ 5c2c...]`
- Adapter/output model path: `[fill: artifact path and hash after training]`
- Training dataset version: `[fill: dataset revision/hash, not just the folder name]`
- Dataset size: `[fill: example count]`
- Train / validation split: `[fill: how the split was made and whether leakage was audited]`
- Leakage check: `[fill: result of the eval-set overlap check between train and eval corpora]`

## Configuration

| Setting | Value |
|---|---|
| Method (LoRA / QLoRA / full / other) | `[fill: method]` |
| Seed | `[fill: integer]` |
| Optimizer | `[fill: e.g. AdamW, adamw-torch]` |
| Learning rate | `[fill: value and schedule (cosine/linear/constant)]` |
| Warmup steps | `[fill: count or fraction]` |
| Batch size (per device) | `[fill: value]` |
| Gradient accumulation steps | `[fill: value]` |
| Epochs | `[fill: value or early-stop criterion]` |
| Precision / mixed precision | `[fill: e.g. bf16, fp16, fp32]` |
| LoRA rank / alpha / target modules | `[fill: values, or n/a]` |
| Max sequence length | `[fill: tokens]` |
| Other notable flags | `[fill: anything else that changes training behavior]` |

## Environment

- Framework versions (transformers, peft, torch, trl, ...): `[fill: exact versions]`
- Training hardware: `[fill: GPU model(s), count, VRAM per GPU]`
- CUDA / driver version: `[fill: version]`
- Container / OS image: `[fill: image tag or OS + versions]`

## Evaluation

- Eval set version: `[fill: eval set revision/hash]`
- Eval harness and scoring code: `[fill: script/repo and commit]`
- Baseline score (base model on same eval set): `[fill: metric and value]`
- Final score: `[fill: metric and value, per capability if applicable]`
- Eval notes: `[fill: anything unusual about how the numbers were produced]`

## Artifacts

- Weights / adapter location: `[fill: path or registry reference]`
- Logs / training run URL: `[fill: wandb/mlflow URL or log path]`
- Config file: `[fill: path to the exact config used]`

## Reproduction Check

- [ ] A fresh checkout plus this record reproduces the reported numbers
- [ ] If not reproducible, the gap is documented here: `[fill: what is missing]`

## Decisions & Follow-Ups

- Why this configuration: `[fill: the reasoning behind the key choices]`
- Known issues / next steps: `[fill: anything to try next, or leave blank]`
