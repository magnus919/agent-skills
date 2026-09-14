# Constrained optimization

Make optimization decisions that remain valid when constraints, tradeoffs, and solver limits matter.

## Why Install This Skill

Optimization results are easy to misread: a lower score may violate a hard limit, a timeout may be mistaken for infeasibility, and an average from one random run may not survive repetition. This skill gives an agent a disciplined way to state the problem before choosing a method.

It produces reviewable formulation and solution-audit records. The workflow separates feasible candidates from infeasible ones, preserves exact-solver bounds and gaps, and makes multiobjective and stochastic tradeoffs explicit.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Decision workflow, boundaries, and routing |
| `references/` | Formulation, solver evidence, Pareto, robustness guidance, and primary-source index |
| `templates/` | Formulation and solution-audit records |
| `evals/` | Quality cases for common optimization failures |

## Quick Start

Start with `SKILL.md`, then fill `templates/formulation-record.md` before selecting a solver. Use `templates/solution-audit.md` to independently verify the returned candidate.

## Triggers

- Formulating a constrained optimization problem
- Comparing exact methods, heuristics, or stochastic search
- Reviewing feasibility, optimality gaps, or timeout claims
- Choosing among Pareto tradeoffs or objective priorities

## Requirements

No solver, API key, or runtime is required. Named solver operation and statistical modeling remain with their respective skills.
