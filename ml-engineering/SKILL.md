---
name: ml-engineering
description: >-
  Plan and execute production ML engineering work — classifier versus generative
  model selection, zero-shot baselines, coding specialization, model training and
  fine-tuning (LoRA/QLoRA), evaluation and eval-set design, quantization
  decisions, inference deployment, lineage, feature parity, drift response, and
  regression triage, grounded in practical engineering patterns for production ML
  systems. Do not use for statistical
  modeling and experimental design (that's the data scientist) or for operating
  a specific inference engine (that's a tool skill such as llama-cpp or vllm).
license: MIT
metadata:
  tags: ml, machine-learning, fine-tuning, training, evaluation, quantization, mlops,
    inference, vllm, gguf
  source_repo: https://github.com/magnus919/hermes-profiles
---

# ML Engineering Methodology

Machine learning engineering is the bridge between model research and production systems. This methodology covers the engineering disciplines needed to train, evaluate, deploy, and maintain ML models reliably.

## The ML Engineer's Domain

| You own | You don't own |
|---------|--------------|
| Model training — LoRA/QLoRA fine-tuning, full fine-tuning, distributed training | Statistical modeling and experimental design — that's the data scientist |
| Model evaluation — benchmark suites, custom eval sets, regression testing | Causal inference and hypothesis testing — that's the data scientist |
| Quantization — GGUF, GPTQ, AWQ, bitsandbytes | Training data collection and labeling — that's the data/ML ops team |
| Inference serving — [vLLM](../vllm/SKILL.md), [llama.cpp](../llama-cpp/SKILL.md), TGI, Triton | Business metrics and KPI definition — that's the product manager |
| Evaluation harness — lm-eval-harness, custom pipelines | Data pipeline architecture — that's the data engineer |
| Model deployment — containerization, versioning, A/B testing | Infrastructure provisioning — that's the platform engineer |

## Reference Files

| Reference | When to load |
|-----------|-------------|
| `references/nli-classification.md` | NLI premise/hypothesis contracts, binary/ternary heads, score modes and truncation |
| `references/nli-evaluation.md` | Domain/language validation, calibration, abstention, cost and adaptation experiments |
| `references/nli-sources.md` | Primary NLI evidence and limitations |
| `references/task-specific-extraction.md` | Span/encoder/generative extraction, offsets, source grounding, critical recall and receipts |
| `references/task-specific-summarization.md` | Extractive/abstractive model choice, source/target retention, factuality and downstream compaction |
| `references/text-model-sources.md` | Primary extraction/summarization evidence and uncertainty |
| `references/tabular-representations.md` | Self-supervised tabular encoders, corruption/contrastive objectives, row-context and fair comparisons |
| `references/sequence-sources.md` | Primary-source findings and uncertainty for tabular and sequence representations |
| `references/transaction-sequences.md` | Ordered-event representation, windows, label maturity, forward/entity validation and stateful serving |
| `references/specialization-decisions.md` | Choosing rules/classifiers/zero-shot/prompt/SFT/RL, designing fixed-budget comparisons and interpreting verifier or case-study claims |
| `references/specialization-evidence.md` | Primary-source findings, contradictory results and local validation limits |
| `references/fine-tuning.md` | Setting up a LoRA/QLoRA/ full fine-tuning run — data prep, hyperparameters, validation strategy |
| `references/evaluation.md` | Evaluating a model — benchmark selection, custom eval sets, regression tracking, comparison methodology |
| `references/evaluation-and-lineage.md` | Metric/configuration decisions, repeated stochastic comparisons, end-to-end lineage, temporal feature parity, drift response, and adaptation/serving tradeoffs |
| `references/quantization-inference.md` | Quantizing a model and serving it — GGUF/GPTQ/AWQ/bitsandbytes comparison, calibration data strategies, KV cache quantization, vLLM/llama.cpp/TGI/Triton architecture, production considerations |
| `references/training-infrastructure.md` | Selecting and provisioning training infrastructure — GPU selection, VRAM budgeting, multi-GPU strategies (DDP/FSDP/DeepSpeed), cloud vs on-prem, storage, monitoring |

## Templates

| Template | When to Use |
|-----------|-------------|
| `templates/nli-experiment.md`, `templates/nli-logits.json` | NLI study worksheet and synthetic saved-logit contract |
| `templates/text-model-record.md`, `templates/extraction-receipt.json`, `templates/summary-receipt.json` | Task/lineage worksheet and synthetic extraction/summary contracts |
| `templates/sequence-model-record.md` | Representation, pretraining exposure, time/window/state and evaluation record |
| `templates/sequence-windows.json` | Synthetic time-aware window audit contract |
| `templates/specialization-study.md` | Preregistering task-matched alternatives, data freeze, quality/resource guardrails and stopping rules |
| `templates/task-run-baseline.json`, `templates/task-run-candidate.json` | Synthetic saved-receipt contract examples; not model results |
| `templates/training-run-record.md` | Recording a training or fine-tuning run — model and data versions, full config, environment, eval results — so it can be reproduced |
| `templates/eval-regression-table.md` | Tracking model quality across runs and triaging a regression — one row per eval case or capability subset |
| `templates/quantization-decision-record.md` | Recording a quantization decision — baseline, candidates compared, quality threshold, and rollback path |
| `templates/model-lineage-record.md` | Linking data/features, code/configuration, runs, artifacts, evaluations, registry state, and deployed serving versions |
| `templates/drift-response-record.md` | Recording drift signals, thresholds, diagnosis, retrain/rollback decisions, and post-action evidence |

## Scripts

| Script | When to Use |
|-----------|-------------|
| `scripts/nli_score_contract.py` | Saved NLI score arithmetic and mapping/shape checks; no model execution or calibration |
| `scripts/audit_text_outcomes.py` | Exact source-span and summary-receipt consistency checks; no model or semantic judgment |
| `scripts/audit_sequence_windows.py` | Declared window availability, identity, outcome and fold-boundary screen; no model execution |
| `scripts/compare_task_runs.py` | Descriptive paired task comparison with matched pins/roster, incomplete-evidence rejection and group bootstrap; no release approval |
| `scripts/check-eval-overlap.py` | Checking a training corpus against an eval corpus for test-set leakage (shared n-grams); `--json` for CI, exit 1 when an eval file exceeds the overlap threshold |

## Evals

`evals/evals.json` — output-quality eval manifest for this skill: fine-tuning plan review, eval-set design, quantization decision, deployment plan, regression triage, and training-run reproducibility.

## Specialization decision boundary

Start from the required outcome and permitted prediction-time information.
Include simpler rules, supervised or zero-shot classifiers where appropriate;
classification scores are not automatically calibrated probabilities. A proprietary
LLM case study is orientation, not proof of architecture optimality. Compare
matched context/policy/budgets, preserve critical regressions and require every
registered guardrail before promotion. New helper exit zero is descriptive
comparison completion only; model execution and release remain separate evidence.

Route training operations to [unsloth](../unsloth/SKILL.md), typed decisions to
[system-one](../system-one/SKILL.md), labels/provenance to
[training-data-annotation](../training-data-annotation/SKILL.md), experimental
analysis/calibration to [data-scientist](../data-scientist/SKILL.md), and agent-level
evaluation to [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md).

For tabular foundation-model choice, read `references/tabular-foundations.md`;
for named TabPFN setup/context/inference/fine-tuning, use
[tabpfn](../tabpfn/SKILL.md).

## Core Principles

**Measure before you optimize** — Never quantize, prune, or distill a model without first measuring its baseline performance. Optimization without measurement is guessing.

**Reproducibility is non-negotiable** — Every training run needs a reproducible config: seed, data version, hyperparameters, and evaluation methodology. If you can't reproduce it, you can't ship it.

**Baseline first** — Before running an expensive fine-tuning run, establish a baseline with the base model. If the base model is already good enough, the fine-tuning budget is better spent elsewhere.

**Test at the boundary** — Model evaluation is most informative at the edges of the capability distribution, not at the center. Hard examples reveal more than easy ones.

**The evaluation set is a liability** — Every example in your eval set is a potential test-set leak. Use held-out sets, rotate examples, and periodically audit for contamination with the overlap checker.

## When not to use

Do not use this skill for statistical modeling, experimental design, or causal inference — that's the data scientist's discipline. Do not use it to operate a specific inference engine: for llama.cpp installation, model loading, benchmarking, and troubleshooting, load the [llama-cpp](../llama-cpp/SKILL.md) tool skill instead; for vLLM deployment, model configuration, benchmarking, batching tuning, GPU operation, and upgrade/rollback, load the [vllm](../vllm/SKILL.md) tool skill instead. This skill provides the methodology (eval-set design, quantization trade-offs, deployment plans, regression triage); the tool skills own the runbooks.
