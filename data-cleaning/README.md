# data-cleaning

A practical, evidence-first workflow for turning messy data into trustworthy, reviewable datasets.

## Why Install This Skill

Messy data is not solved by a handful of `dropna()` calls. This skill helps an agent discover what is wrong, decide what may safely change, preserve what was observed, and demonstrate that the result still matches the intended grain and meaning.

It works across CSV, JSON, text, DataFrames, SQL extracts, and pipeline boundaries. It combines a repeatable methodology with tool-selection guidance, reusable plans and reports, and a dependency-free profiling script that produces machine-readable evidence before mutation.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Core workflow and completion gate |
| `references/` | Methodology, operations, validation, tools, sources |
| `templates/` | Cleaning plan, decision log, schema contract, quality report |
| `scripts/profile_dataset.py` | Read-only CSV/TSV/JSONL profiler |
| `scripts/test_profile_dataset.py` | Deterministic script tests |
| `evals/evals.json` | Output-quality evaluation cases |

## Quick Start

```bash
python3 scripts/profile_dataset.py input.csv --output profile.json
python3 scripts/profile_dataset.py input.csv --max-rows 10000
```

The profiler does not edit the input. Use its report to fill `templates/cleaning-plan.md`, then validate the transformed output against `templates/schema-contract.yml` or a project-specific contract.

## Triggers

- Clean or standardize CSV, JSON, text, spreadsheet exports, or DataFrames
- Diagnose missing values, duplicates, malformed types, dates, encodings, or categories
- Design a reusable cleaning pipeline or data-quality contract
- Choose among pandas, Polars, pyjanitor, Pandera, Great Expectations, OpenRefine, Frictionless, dbt tests, or Spark-scale tools
- Review whether cleaning is reproducible, safe, or leakage-free

## Requirements

- Python 3.9+ for the bundled script
- No external dependency for first-pass profiling
- Optional ecosystem tools require their own installations
