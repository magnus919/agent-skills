# Default Alive / Default Dead Calculator

Evaluate whether a startup is on a trajectory to profitability before running out of cash. Paul Graham's Y Combinator framework as a deterministic CLI tool.

## Why Install This Skill

When your agent loads this skill, it can **run the single most important startup financial diagnostic**. That means:

- **Compute default alive/dead status** — will revenue reach profitability before cash runs out?
- **Calculate burn multiple** — net burn vs net new ARR (the key efficiency metric)
- **Month-by-month projection** — see the runway month by month
- **Identify levers** — what changes would flip DEAD to ALIVE
- **Actionable verdict** — ALIVE / DEAD / MARGINAL with next-step guidance

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Framework explanation, quick heuristic, full script usage |
| `scripts/default-alive.py` | Deterministic CLI calculator — Python 3.9+ with zero external dependencies |

## Quick Start

```bash
python3 scripts/default-alive.py --revenue 10000 --burn 50000 --cash 500000 --growth 0.05
```

## Triggers

Load this when founders ask about runway, burn rate, default alive status, whether they need to raise money, or financial sustainability analysis.

## Requirements

Python 3.9+ with standard library only (no external dependencies).
