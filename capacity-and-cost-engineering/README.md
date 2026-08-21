# Capacity and Cost Engineering

Connect demand, performance, reliability, and spend into defensible capacity and cost decisions.

## Why Install This Skill

Every service that serves users has a capacity limit and a cost. When your agent can model capacity, calculate unit cost, define budget controls, and require load-test evidence for capacity claims, it stops treating infrastructure as "someone else's problem" and starts making decisions that respect real-world constraints. This skill fills the gap between the financial team's P&L models (which don't know what a request costs in compute) and the platform team's infrastructure-as-code (which doesn't know why a specific SLO target was chosen or what it costs).

After installing this skill, your agent can: project capacity from growth forecasts with utilization targets and scaling triggers; model multi-tenant demand distributions, hot tenants, partition skew, and pooled versus siloed headroom; connect tier promises to quotas, admission, and contextual fairness evidence; calculate platform baseline, tenant-variable, and allocated unit cost; define budget thresholds with operational consequences (alert, throttle, deny); design representative per-tenant load and soak tests as mandatory capacity evidence; and resolve SLO-cost tradeoffs with explicit evidence, ownership, and accountability.

## What You Get

| Directory | What it provides |
|-----------|-----------------|
| `SKILL.md` | Core methodology: connected dimensions (demand/performance/reliability/spend), multi-tenant loading route, working method with five steps, four named scenarios, routing table to adjacent skills, and guardrails against generic cloud-cost tips and universal thresholds |
| `README.md` | This human-facing overview |
| `references/discovery-brief.md` | Ownership boundary analysis for financial, platform, SRE, analytics, SaaS architecture, security, software architecture, readiness, roadmap, and recovery concerns |
| `references/multi-tenant-capacity-and-unit-cost.md` | Original method for tenant distributions, hot tenants, partition skew, pooled/siloed headroom, tier promises, admission, fairness evidence, shared-cost allocation, and tenant-variable unit cost |
| `references/source-index.md` | Public provenance and transformation boundary |
| `templates/capacity-model.md` | Fillable capacity model: demand assumptions, capacity-unit mapping, utilization targets with rationale, scaling triggers, evidence sources, ownership, and tradeoffs |
| `templates/unit-economics-record.md` | Fillable unit-economics record: unit definition, cost numerator with allocation method, demand denominator, unit-cost calculation formula, cost-per-SLO comparison, and structured assumptions/evidence/ownership/tradeoffs fields |
| `templates/load-soak-test-plan.md` | Fillable load/soak test plan: objective, target throughput, duration, environment requirements, success criteria (latency percentiles, error rate, utilization), data collection, and evidence record |
| `templates/budget-quota-decision.md` | Fillable budget/quota decision: budget owner, period, thresholds (alert/soft/hard), quota/rate-limit configuration, enforcement mechanism, operational behavior at each threshold, cost attribution, and approval |
| `templates/slo-cost-tradeoff-record.md` | Fillable SLO-cost tradeoff record: SLO under discussion, current and projected cost, alternative SLO comparison, degradation path, error budget impact, accountable owner, and approval |
| `templates/tenant-capacity-model.md` | Fillable tenant capacity and unit-cost model covering profiles, skew, pooled/siloed comparison, quotas, fairness, cost allocation, and representative per-tenant load/soak evidence |
| `evals/evals.json` | Ten output-quality evaluation cases covering general capacity/cost decisions plus tenant distributions, pooled/siloed headroom, fairness, tenant-variable cost, and routing boundaries |

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
- Modeling multi-tenant demand distributions, hot tenants, partition skew, quotas, fairness, pooled/siloed headroom, or tenant-variable unit cost

## Requirements

- No runtime dependencies, API keys, or system tools.
- No specific Python version, package, or service required.
- The skill references templates that any agent can fill; no special tooling is needed.
