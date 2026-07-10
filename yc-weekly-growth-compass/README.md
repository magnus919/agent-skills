# Weekly Growth Compass — YC's Startup = Growth Framework

Paul Graham's "Startup = Growth" framework as an operational weekly practice. Computes growth rates, benchmarks against YC tiers, and frames every decision through the growth compass.

## Why Install This Skill

When your agent loads this skill, it can **make growth the compass for every startup decision**. That means:

- **Compute weekly growth rates** — single period or time-series data
- **Benchmark against YC tiers** — 1% concerning, 5-7% good, 10%+ exceptional
- **Project compound growth** — see where you'll be in a year at current trajectory
- **Frame decisions** — "does this serve your target growth rate?" for every initiative
- **Estimate doubling time** — how long to 2x, 10x, 100x at current growth

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Framework explanation, YC benchmarks, full script usage |
| `scripts/growth-compass.py` | Deterministic CLI calculator — Python 3.9+ with zero external dependencies |

## Quick Start

```bash
python3 scripts/growth-compass.py --current 1000 --prior 950
python3 scripts/growth-compass.py --series "1000,1050,1100,1150,1200"
```

## Triggers

Load this when founders ask about growth rate, weekly growth, startup traction, metrics, or whether they're moving fast enough.

## Requirements

Python 3.9+ with standard library only (no external dependencies).
