# ML Engineering

Machine learning engineering methodology — model training, fine-tuning (LoRA/QLoRA), evaluation, quantization, deployment, and MLOps pipeline design. Grounded in practical engineering patterns for production ML systems.

## Why Install This Skill

Your agent makes informed decisions about fine-tuning approaches, quantization trade-offs, GPU selection, and serving architecture with real VRAM budgets and benchmarks. Fillable templates turn training runs, eval comparisons, and quantization decisions into reviewable records, and the bundled eval-overlap checker catches train/eval contamination before it invalidates a benchmark.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core methodology, trigger conditions, reference index |
| `references/` | Deep-dive reference files loaded on demand |
| `templates/` | Fillable records: training-run record, eval regression table, quantization decision record |
| `scripts/` | `check-eval-overlap.py` — detects test-set leakage between train and eval corpora |
| `evals/` | Output-quality eval manifest for the skill's methodology cases |

## Triggers

Setting up fine-tuning runs, quantizing models, selecting training infrastructure, deploying inference servers, evaluating model quality, or triaging a model regression.

## Requirements

Assumes familiarity with PyTorch/HuggingFace ecosystem. References cover vLLM, llama.cpp, TGI, DeepSpeed, and accelerate. The bundled script needs only Python 3 (standard library).

## Quick Start

Check an eval corpus for leakage against your training data before trusting any eval score:

```bash
python3 ml-engineering/scripts/check-eval-overlap.py --train data/train/ --eval data/eval/
```

Each eval file is reported with its overlap fraction against the training corpus; an eval file that shares more than 10% of its text with training is flagged `LEAK` and the script exits 1, so it can gate a CI pipeline. Add `--json` for machine-readable output, `--token-ngram 5` to compare token sequences instead of character shingles, and `--max-overlap-fraction 0.05` to tighten the threshold.

Load SKILL.md for the methodology overview and reference table, then load specific references or templates as needed for the task at hand.
