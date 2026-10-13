# Specialization implementation record

Status: prepared / executed / rejected / inconclusive. Prepared is not validated.

## Target and authority

- User outcome and output contract:
- Why rules, a classifier, zero-shot labels, prompt changes or retrieval are insufficient:
- Authorized host, accelerator, isolated run directory and mutable paths:
- GPU-sharing owner/reservation and current allowed jobs:
- Rollback: stop only run-owned processes; retain accepted environment/artifact:
- Downloads, external providers, publishing and service exposure separately scoped:

## Data and task truth

- Source manifest/file hashes; immutable source revisions; rights decisions:
- Task and repository/family/source-group identities:
- Splits created before variants/chunking: train / development / calibration / sealed test:
- Prediction-time cutoff, label maturity and any intervention censoring:
- Teacher/generation prompts, model revisions, tool schemas and independent review:
- Exact/semantic duplicates, fork relationships and public benchmark exposure:
- Reference solutions and verifier suite/code/image hashes:
- Malformed, empty, wrong, adversarial, timeout and infrastructure challenges:

## Model, tokenizer and training contract

- Base weights/revision/hash; tokenizer/processor/template revision/hash:
- Surface/backend and official model-specific recipe commit:
- Resolved package versions, CUDA runtime/driver and same-process import probe:
- Objective: SFT / preference / RLVR / continued pretraining:
- LoRA targets/rank/alpha/dropout; base quantization; precision:
- Optimizer/paging/offload policy; scheduler; seed; step/epoch budget:
- Context/completion lengths, generation groups, global batch and accumulation:
- Rendered real examples; target-retention percentiles and rejection counts:
- Actual collator label masks, decoded supervised spans and packing-boundary checks:
- Tool/multimodal processor requirements; unsupported shape handling:

## Resource and stopping contract

- Whole-device and process peak VRAM ceiling, free-space reserve, host RAM:
- Maximum GPU hours, rollout tokens, verifier workers and output/checkpoint bytes:
- Representative-length pilot plus rollout/verifier bottleneck measurements:
- Stop at contention, nonfinite values, audit failure or registered regression:
- Exact checkpoint state; fresh reload and stateful-resume acceptance:

## Matched task evaluation

- Incumbent/base, simple alternative, prompt/retrieval control and candidate:
- Same permitted information; differences in policy/harness disclosed:
- Frozen tasks, decoding, token/tool/attempt/time budgets and status taxonomy:
- Primary metric/minimum gain; critical regression ceilings:
- General instruction, multi-turn and out-of-domain regression slices:
- Repeated seed protocol and independent-group uncertainty method:
- Task outcomes, raw output/patch references, verifier logs and failed tasks retained:

## Delivery and evidence

| Stage | Status (not run/pass/fail/inconclusive) | Artifact and hash | Actual evidence |
|---|---|---|---|
| Provenance/split screen | | | |
| Tokenizer/actual label audit | | | |
| Representative pilot | | | |
| Bounded training | | | |
| Fresh reload | | | |
| Stateful resume | | | |
| Held-out task comparison | | | |
| Merge/export | | | |
| Target-runtime and lossy-quality comparison | | | |
| Release decision and every guardrail | | | |

A helper exit zero, synthetic receipt or schema-valid eval manifest cannot fill
an executed-stage cell. Name unavailable evidence and the owner/prerequisite.
