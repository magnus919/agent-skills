# Capacity and Cost Engineering

Connect demand, performance, reliability, and spend into defensible capacity and cost decisions.

## Why Install This Skill

Every service that serves users has a capacity limit and a cost. When your agent can model capacity, calculate unit cost, define budget controls, and require load-test evidence for capacity claims, it stops treating infrastructure as "someone else's problem" and starts making decisions that respect real-world constraints. This skill fills the gap between the financial team's P&L models (which don't know what a request costs in compute) and the platform team's infrastructure-as-code (which doesn't know why a specific SLO target was chosen or what it costs).

After installing this skill, your agent can: project capacity from growth forecasts with utilization targets and scaling triggers; calculate what one request or one user costs to serve at the infrastructure level; define budget thresholds with operational consequences (alert, throttle, deny); design load and soak tests as mandatory capacity evidence — not optional nice-to-haves; and resolve SLO-cost tradeoffs with explicit evidence, ownership, and accountability. When a product manager asks "what would it cost to serve 2x the users?", your agent has a structured answer instead of a guess.

## What You Get

| Directory | What it provides |
|-----------|-----------------|
| `SKILL.md` | Core methodology: connected dimensions (demand/performance/reliability/spend), working method with five steps, four named scenarios (growth, peak, degraded, cost-constrained), routing table to adjacent skills, and guardrails against generic cloud-cost tips and universal utilization targets |
| `README.md` | This human-facing overview |
| `references/discovery-brief.md` | Ownership boundary analysis comparing seven adjacent skills (financial-modeling, platform-engineering, site-reliability-engineering, product-analytics-and-measurement, production-readiness, product-roadmapping-and-portfolio, resilience-and-recovery) with explicit routing decisions |
| `templates/capacity-model.md` | Fillable capacity model: demand assumptions, capacity-unit mapping, utilization targets with rationale, scaling triggers, evidence sources, ownership, and tradeoffs |
| `templates/unit-economics-record.md` | Fillable unit-economics record: unit definition, cost numerator with allocation method, demand denominator, unit-cost calculation formula, cost-per-SLO comparison, and structured assumptions/evidence/ownership/tradeoffs fields |
| `templates/load-soak-test-plan.md` | Fillable load/soak test plan: objective, target throughput, duration, environment requirements, success criteria (latency percentiles, error rate, utilization), data collection, and evidence record |
| `templates/budget-quota-decision.md` | Fillable budget/quota decision: budget owner, period, thresholds (alert/soft/hard), quota/rate-limit configuration, enforcement mechanism, operational behavior at each threshold, cost attribution, and approval |
| `templates/slo-cost-tradeoff-record.md` | Fillable SLO-cost tradeoff record: SLO under discussion, current and projected cost, alternative SLO comparison, degradation path, error budget impact, accountable owner, and approval |
| `evals/evals.json` | Five output-quality evaluation cases covering growth forecast, peak event, SLO-cost conflict, quota decision, and misleading unit-cost calculation |

## Quick Start

No setup required. The skill is pure methodology — no scripts, no API keys, no runtime dependencies.

To use: ask your agent to model capacity for a service, calculate unit cost, define budget controls, plan a load test, or resolve an SLO-cost tradeoff. The skill loads when the task matches its trigger conditions and provides step-by-step guidance plus fillable templates for each artifact.

## Triggers

Load this skill when the task involves:
- Projecting capacity from a growth forecast
- Sizing capacity for a peak event (launch, seasonal, Black Friday)
- Calculating unit cost at the infrastructure level
- Defining budget thresholds, spending alerts, or hard caps
- Designing quota or rate-limit enforcement
- Planning or reviewing a load or soak test as capacity evidence
- Resolving an SLO-cost tradeoff or cost-constrained reliability decision
- Reviewing a cost anomaly or attributing cost to services/teams

## Requirements

- No runtime dependencies, API keys, or system tools.
- No specific Python version, package, or service required.
- The skill references templates that any agent can fill; no special tooling is needed.
