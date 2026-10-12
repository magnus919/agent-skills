# Unsloth run record

## Intent and authority

- Task, surface (Core/Studio/Desktop), success metric and acceptance threshold:
- Authorized environment, compute/time budget, output path, publication scope:
- Previous environment/model and rollback or recovery path:

## Reproducibility

- Date, OS, Python, accelerator/backend, free VRAM/RAM/disk:
- Unsloth, unsloth_zoo, Torch/runtime, TRL, Transformers, PEFT, quantization versions:
- Environment lock/container digest, source notebook/script URL and commit:
- Base model/tokenizer/processor IDs and immutable revisions:
- Dataset provenance, permission, hashes, grouping and split IDs:
- Seed, template/hash, BOS/EOS/PAD, rendered example and label audit location:
- Quantization, dtype, target modules, rank/alpha, optimizer/LR/schedule:
- Context/token-length distribution, truncation policy, packing:
- Per-device batch, accumulation, world size, effective batch, max steps/epochs:
- For RL: reward revision, challenge tests, generation settings and reward budget:

## Evidence

| Check | Status (pass/fail/not run) | Artifact or observation |
|---|---|---|
| Backend operation and small training run | | |
| Structural data audit and group/semantic leakage review | | |
| Actual collator labels retain intended targets | | |
| Base versus candidate held-out task results | | |
| Critical regressions and resource budget | | |
| Fresh-process reload | | |
| Resume from full checkpoint (if required) | | |
| Target-runtime export parity | | |

- Measured peak memory, warmup policy, tokens/sec, total elapsed time:
- Failed attempts and links to subsequent attempts:
- Missing evidence and consequential limitations:

## Handoff

- Adapter, tokenizer/processor, base revision, merged/exported file hashes:
- Full checkpoint location and resume command (distinct from adapter reload):
- Serving runtime/version, decoding and stop settings:
- Publication destination/visibility and permission (if applicable):
- Decision: accept / iterate / stop; reason and next bounded action:
