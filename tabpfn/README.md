# TabPFN

Use tabular foundation models with reproducible data, checkpoint and evaluation decisions.

## Why Install This Skill

TabPFN can predict from labeled table context without training a new model for
every dataset. Choosing the right checkpoint, preserving that context and evaluating
forward holdouts are essential to making its predictions useful.

This skill gives your agent detailed setup, version and license guidance, data
and calibration checks, fine-tuning boundaries and recovery instructions. An
offline helper catches declared temporal leakage, split overlap and policy-limit
violations before you spend model time. Actual model execution remains explicitly
unverified until tested on your selected environment.

## What You Get

| Contents | Benefit |
|---|---|
| `references/` | Model decisions, local operations, evaluation, adaptation and sources |
| `scripts/tabpfn_check.py` | Read-only package inventory and task-manifest audit |
| `scripts/test_tabpfn_check.py` | Leakage, capacity, malformed-input and privacy challenges |
| `templates/` | Run worksheet and synthetic manifest example |
| `evals/` | Output-quality cases and assertion challenges |

## Quick Start

From this directory:

```bash
python3 scripts/tabpfn_check.py doctor
python3 scripts/tabpfn_check.py audit templates/task-manifest.json
```

The first prints package versions or null. The example audit reports counts and
no findings; it does not load a model or approve a license. Exit 1 means a finding
or invalid manifest; exit 2 means incorrect CLI arguments.

## Triggers

- Choose, install or troubleshoot a TabPFN checkpoint.
- Prepare labeled context, forward holdouts and calibration for TabPFN.
- Plan explicit weight fine-tuning or verify saved inference artifacts.

## Requirements

Offline helper: Python 3.10+, standard library. Model execution: version-matched
TabPFN/Torch/data dependencies, suitable hardware and approved weight terms.
Downloads/hosted clients require separate network and data-transfer scope.
