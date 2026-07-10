# Convergence Detection

The council uses algorithmic convergence detection to decide when to stop debating — not a fixed number of rounds.

## Metrics

After each cross-examination round, four metrics are computed:

| Metric | Calculation | Meaning |
|--------|------------|---------|
| **Mean confidence** | Average of all agents' `updated_confidence` values | Overall conviction level |
| **Dispersion** | Standard deviation of confidence values | Agreement spread — how far apart agents are |
| **New arguments** | `remaining_disagreements` + `new_evidence_needed` not seen in prior rounds | Whether the debate is still surfacing new material |
| **Concessions** | Count of items in `concessions` across all agents | Whether positions are shifting |

## Decision Logic

```python
if round >= max_rounds:
    stop_reason = "max_rounds"
elif dispersion < threshold and confidence_delta < 0.03:
    stop_reason = "converged"
elif new_arguments == 0 and concessions == 0 and rounds > 1:
    stop_reason = "diminishing_returns"
elif dispersion > threshold * 1.5 and concessions == 0 and new_arguments == 0:
    stop_reason = "genuine_disagreement"
else:
    stop_reason = "continue"  # run another round
```

## Default Thresholds

| Mode | Default threshold | Max rounds |
|------|------------------|------------|
| quick | 0.15 | 2 |
| medium | 0.10 | 4 |
| deep | 0.08 | 4 |

## Diagnostic Interpretation

| Pattern | Meaning |
|---------|---------|
| Mean confidence DROPPED, dispersion WIDENED | Council surfaced genuine doubt — healthy debate |
| Mean confidence ROSE, dispersion NARROWED | Genuine convergence — agents convinced each other |
| Mean confidence STABLE, dispersion NARROWED | False consensus — agents agreed before debating (possible shared blind spots) |
| Mean confidence ROSE, dispersion WIDENED | Polarization — agents became more entrenched in their positions |
