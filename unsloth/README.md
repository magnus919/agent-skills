# Unsloth

Train, run, and export local models with fewer environment and data mistakes.

## Why Install This Skill

Unsloth makes local model training more accessible, but choosing the wrong
backend, chat template, or export format can waste a training run. This skill
helps your agent choose between Core, Studio, and Desktop and take a model from
installation through a measured experiment to a reloadable artifact.

It includes practical guidance for LoRA/QLoRA, GRPO, vision and audio workflows,
multi-GPU training, and deployment handoffs. Offline checks catch malformed text
datasets and exact train/validation overlap before GPU time is spent. A GPU-validated Qwen3 smoke workflow implements label audits, training,
checkpoint resume, fresh reload and GPU F16 GGUF comparison. Research-backed guides also cover decision models, local coding agents, MCP,
media generation and quantization selection. Their runtime paths remain explicitly
unverified until tested on the selected model and backend.

For coding specialization, it adds source-group leakage checks, verifier
challenge receipts, reward-design guidance and experiment templates. These help
you distinguish a useful code model from a run with improving loss or reward.
They also guide when a simpler classifier is sufficient and when training is justified.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | End-to-end workflow and decision boundaries |
| `references/` | Focused training, decision, agent/tool, media and quantization guides |
| `scripts/specialization_audit.py` | Read-only source/split and verifier-receipt checks; no code execution |
| `scripts/decision_audit.py` | Hard-label decision schema and three-split leakage checks |
| `scripts/unsloth_preflight.py` | Read-only environment inventory and JSONL audit |
| `scripts/sft_smoke.py`, `sft_audit.py` | Bounded training and actual label/token audits |
| `scripts/verify_export.py`, `gpu_completion.cpp` | Fresh merged-model and GPU GGUF parity |
| `scripts/test_*.py` | Offline audit, guard and subprocess-limit tests |
| `assets/` | Pinned stack/model configuration and synthetic train/holdout data |
| `templates/specialization-plan.md`, `reward-contract.md` | Coding/RL experiment, verifier and delivery contracts |
| `templates/run-record.md` | Reproducible experiment and delivery worksheet |
| `evals/` | Representative behavior scenarios and review challenges |

## Quick Start

From this directory:

```bash
python3 scripts/unsloth_preflight.py doctor --json
python3 scripts/unsloth_preflight.py dataset train.jsonl --eval-file valid.jsonl --json
```

The first command lists package versions or `null` for missing packages. The
second reports row counts, invalid rows, duplicates, and exact overlap; exit 1
means a finding needs attention. Neither command installs software or trains.

For GPU training, follow [the validated recipe](references/validated-sft.md).
The offline helpers alone do not prove training compatibility.

Try asking: “Use Unsloth to plan a QLoRA fine-tune on my 24 GB GPU, check my
conversation data, and export the result for llama.cpp.”

## Triggers

- Install or troubleshoot Unsloth Core, Studio, or Desktop.
- Fine-tune with LoRA/QLoRA, preference training, GRPO or decision heads.
- Connect local coding agents/tools or plan Desktop media generation.
- Select Dynamic GGUF/NVFP4 artifacts with measured quality checks.
- Diagnose masking, memory, checkpoint, or export problems.
- Prepare vision/audio training or verify multi-GPU feasibility.

## Requirements

The helpers use Python 3.10+ and the standard library. Actual training needs the
appropriate Unsloth/backend stack and supported hardware; requirements vary by
product and model. Downloads need network access. A Hugging Face token is needed
only for gated/private access or publishing; keep it out of scripts and logs.
