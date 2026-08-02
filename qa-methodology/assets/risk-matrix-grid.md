# Risk Matrix Grid (5×5 Probability × Impact)

> Use this grid during risk assessment workshops to score and zone risks. This grid is consistent with [risk-based-testing.md](../references/risk-based-testing.md) and the `risk-prioritize.py` script.

## Scoring Formula

```
Risk Score = Probability (1–5) × Impact (1–5)
```

## 5×5 Grid

| P \ I | 1 — Negligible | 2 — Minor | 3 — Moderate | 4 — Major | 5 — Catastrophic |
|-------|:--------------:|:---------:|:------------:|:---------:|:----------------:|
| **5 — Almost Certain** | 5 (P3) | 10 (P2) | 15 (P1) | 20 (P0) | 25 (P0) |
| **4 — Likely** | 4 (P3) | 8 (P2) | 12 (P1) | 16 (P0) | 20 (P0) |
| **3 — Possible** | 3 (P3) | 6 (P2) | 9 (P2) | 12 (P1) | 15 (P1) |
| **2 — Unlikely** | 2 (P3) | 4 (P3) | 6 (P2) | 8 (P2) | 10 (P2) |
| **1 — Rare** | 1 (P3) | 2 (P3) | 3 (P3) | 4 (P3) | 5 (P3) |

## Zone Thresholds

| Zone | Score Range | Priority Tier | Action |
|------|-------------|:-------------:|--------|
| **Critical** | 20–25 | P0 | Test exhaustively; every path, every edge case |
| **High** | 12–19 | P1 | Test all happy paths + known failure modes |
| **Medium** | 6–11 | P2 | Test happy paths + common failure modes |
| **Low** | 1–5 | P3 | Smoke test only; defer detailed testing |

## Probability Anchors

| Rating | Label | Anchor |
|:------:|-------|--------|
| 5 | Almost Certain | Will fail in production within a quarter (or has already) |
| 4 | Likely | Expected to fail within a year |
| 3 | Possible | Could fail; uncertain |
| 2 | Unlikely | Unlikely given current controls |
| 1 | Rare | Extremely unlikely; well-understood code |

## Impact Anchors

| Rating | Label | Anchor |
|:------:|-------|--------|
| 5 | Catastrophic | Data loss, security breach, revenue stoppage |
| 4 | Major | Major feature outage, SLA breach |
| 3 | Moderate | Degraded experience, workaround exists |
| 2 | Minor | Cosmetic, minor inconvenience |
| 1 | Negligible | No user-visible impact |

## Workshop Scoring Sheet

Record scores during the workshop, then transfer to [templates/risk-register.md](../templates/risk-register.md).

| # | Risk (short label) | P (1–5) | I (1–5) | Score | Zone | Tier |
|---|---------------------|:-------:|:-------:|:-----:|------|:----:|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |

## Calibration Rule

If probability votes span more than 2 points:
1. The facilitator asks the highest and lowest voter to state their evidence.
2. Re-vote once.
3. Record dissent in the register.

## Test Allocation by Tier

| Tier | Hours per Risk Item (default) | Strategy |
|:----:|------------------------------:|----------|
| P0 | 8–16 | Exhaustive design + automation |
| P1 | 4–8 | Happy paths + failure modes |
| P2 | 2–4 | Happy paths + common failures |
| P3 | 0.5–1 | Smoke only |

Adjustment: multiply by 1.5× for legacy/unfamiliar code, 0.7× for well-automated areas.
