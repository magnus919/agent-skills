# Eval Regression Table

Use this table to track model quality across runs and to make regression triage
auditable. One row per eval case or capability subset, one table per model change
being compared. Every number must name the eval set version that produced it.

## Change Under Evaluation

- Change / run IDs compared: `[fill: e.g. ft-support-lora-013 vs ft-support-lora-014]`
- Date: `[fill: YYYY-MM-DD]`
- Evaluator: `[fill: name or handle]`
- Eval set version: `[fill: eval set revision/hash — do not compare across versions]`
- Leakage check status: `[fill: overlap-check result between train and eval corpora]`

## Results

| Eval case / capability subset | Baseline score | New score | Delta | Noise estimate | Verdict | Notes |
|---|---|---|---|---|---|---|
| `[fill: case or subset name]` | `[fill: baseline value]` | `[fill: new value]` | `[fill: signed delta]` | `[fill: e.g. +/-0.02 from repeat runs]` | `[fill: regression / improvement / no change]` | `[fill: what changed and why]` |
| `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` | `[fill: ...]` |

## Analysis

- Aggregate verdict: `[fill: e.g. "overall +3%, but multi-turn subset regressed"]`
- Is the delta beyond noise? `[fill: yes/no and the evidence]`
- Per-example inspection of any regression: `[fill: link or notes for the regressed cases]`
- Root-cause hypothesis: `[fill: data mix drift, overfitting, trade-off, eval artifact, other]`
- Contamination check: `[fill: re-run the overlap checker if a subset dropped suspiciously]`

## Decision

- Decision: `[fill: ship / retrain / tune / roll back]`
- Rollback or follow-up action: `[fill: adapter version to revert to, retrain ticket, etc.]`
- Sign-off: `[fill: who approved and when]`
