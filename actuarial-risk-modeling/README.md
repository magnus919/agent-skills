# actuarial-risk-modeling

Expert statistical modeling for insurance, actuarial, and financial-risk decisions.

## Why Install This Skill

Many models fail before the algorithm is chosen. The data may represent repeated policy periods, claims may be zero-inflated and heavy-tailed, exposure may differ across records, or the validation split may quietly use information from the future. This skill helps an agent recognize those structures and choose an analysis that can survive scrutiny.

It is useful for insurance pricing and claims work, financial-risk analysis, forecasting, reserving, solvency questions, and other settings where uncertainty has operational consequences. It emphasizes transparent assumptions, appropriate validation, calibration, tail behavior, and clear communication rather than treating a high-scoring model as self-justifying.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Routing, workflow, boundaries, and completion gate |
| `references/` | Model selection, validation, applications, diagnostics, governance, and sources |
| `templates/` | Model brief, validation plan, report, and governance record |
| `scripts/risk_preflight.py` | Read-only CSV/JSONL profile with risk-modeling diagnostics |
| `scripts/temporal_split_audit.py` | Read-only chronological split and leakage audit |
| `scripts/test_*.py` | Deterministic tests for bundled scripts |
| `evals/evals.json` | Output-quality evaluation cases |

## Quick Start

```bash
python3 scripts/risk_preflight.py claims.csv --output preflight.json
python3 scripts/temporal_split_audit.py observations.csv --time-column observed_at --output splits.json
```

Both scripts are read-only and use only the Python standard library.

## Triggers

- Model insurance claims, frequency, severity, pure premium, or medical expenditure
- Select or diagnose a GLM, two-part, survival, panel, time-series, credibility, or tail model
- Validate a financial forecast, risk measure, reserve, or solvency estimate
- Design leakage-safe backtesting, calibration, stress testing, or model governance
- Explain statistical model output and uncertainty to an actuarial, risk, finance, or executive audience

## Requirements

- Python 3.9+ for the bundled scripts
- No external dependency for the preflight and temporal-audit scripts
- A qualified practitioner remains responsible for regulated or credentialed actuarial, investment, legal, accounting, and regulatory decisions
