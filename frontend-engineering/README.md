# Frontend Engineering

Frontend engineering methodology — component architecture, state management, API integration, responsive layout, client-side performance, and frontend testing patterns. Framework agnostic, focused on web frontend implementation.

## Why Install This Skill

Your agent applies proven component architecture, state management, and performance patterns instead of reinventing frontend structure each time. Fillable templates capture component/state design and performance budgets as reviewable records, and the bundled bundle-budget checker enforces performance budgets in CI.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core methodology, trigger conditions, reference index |
| `references/` | Deep-dive reference files loaded on demand |
| `templates/` | Fillable records: component/state design record, performance budget |
| `scripts/` | `bundle-budget-checker.py` — checks bundle size reports against total and per-chunk budgets |
| `evals/` | Output-quality eval manifest for the skill's methodology cases |

## Triggers

Building UI components, choosing state management approaches, integrating APIs, optimizing Core Web Vitals, or setting up responsive layouts.

## Requirements

Platform-agnostic. Framework-agnostic patterns applicable to React, Vue, Svelte, or vanilla JS. The bundled script needs only Python 3 (standard library).

## Quick Start

Check a bundle size report against total and per-chunk budgets before merging a change:

```bash
python3 frontend-engineering/scripts/bundle-budget-checker.py dist/bundle-report.json --total 500KB --chunk 120KB
```

The report maps chunk names to sizes (or a `{"chunks": [...]}` list from your bundler's analyzer). The script prints each chunk, the budget, and OK/OVER status, and exits 1 when any budget is exceeded — so it can gate CI. Add `--json` for machine-readable output.

Load SKILL.md for the methodology overview and reference table, then load specific references as needed for the task at hand.
