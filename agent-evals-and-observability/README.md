# Agent Evals and Observability

Build evidence for AI-agent changes without confusing a dashboard with proof of quality.

## Why Install This Skill

Agent behavior can look good in a demo yet fail through an unsafe tool call, a bad recovery path, stale data, or a silent production regression. This skill helps your agent turn those risks into task and trajectory contracts, datasets, appropriate graders, and release evidence.

It also keeps observability useful without turning it into a privacy liability. Your agent can design minimized traces and metrics, analyze a regression fairly, and make a release decision that keeps hard safety and privacy invariants separate from ordinary quality indicators.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | Framework-neutral workflow and routing |
| `references/` | Evaluation, statistics, trajectory, privacy, OTel, and source guidance |
| `templates/` | Fillable plans, manifests, grader specs, reviews, reports, and gates |

## Quick Start

Ask: `Create an eval plan and release gate for this agent change.`

Expected result: a risk-based plan that names the task contract, evidence, privacy limits, uncertainty, rollback path, and decision owner.

## Triggers

- Agent evaluation, LLM evals, evaluation dataset, grader, or model judge
- Agent observability, traces, telemetry, trajectory review, or production monitoring
- Regression analysis, prompt/model/tool release gate, or incident-to-eval learning
- Privacy-aware logging, redaction, retention, or trace sampling for an agent

## Requirements

No package, vendor account, or API key is required. Use the agent framework and telemetry backend already selected by the project. OpenTelemetry GenAI is optional interoperability guidance only.
