# Training Data Annotation

Design human labeling programs that produce useful, defensible machine-learning data.

## Why Install This Skill

Poor labels waste model-training budgets and hide failures behind a misleading
agreement number. This skill helps an agent define the task, select informative
items, protect representative held-out data, and document who labeled what and
under which rules.

It also treats annotators as part of the measurement system. Your agent can plan
calibration, fair disagreement handling, workload controls, provenance, and a
cost-quality stopping decision that downstream ML and data teams can actually use.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | End-to-end annotation methodology and routing |
| `references/` | Task design, acquisition, annotator quality, provenance, and source guidance |
| `templates/` | Annotation plan, guide, and quality report records |
| `evals/evals.json` | Six output-quality cases for difficult annotation decisions |

## Quick Start

Ask: `Design an annotation plan for this training dataset, including calibration and stopping.`

## Triggers

- Training, validation, or evaluation data labeling
- Annotation guidelines, label taxonomy, or adjudication
- Active learning, uncertainty sampling, diversity sampling, or held-out audits
- Annotator qualification, agreement, workload, pay, or calibration
- Dataset provenance, consent, licensing, retention, or deletion for labels

## Requirements

No package or API key. Statistical analysis, data pipelines, model training, and interface implementation use their routed specialist skills.
