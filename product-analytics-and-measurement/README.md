# Product Analytics and Measurement

Turn intended product outcomes into observable, governed evidence.

## Why Install This Skill

Most product teams measure what is easy, not what matters. They inherit dashboards built by previous teams, track events nobody reviews, and discover too late that a "North Star" metric was never actually measurable. When metrics conflict across teams — marketing counts an activation differently than product — there is no contract to resolve the disagreement.

After installing this skill, your agent can define a complete measurement system for any product: decompose a North Star into a metric tree with leading and lagging indicators, produce an event tracking plan with identity and data-quality rules, audit instrumentation before trusting the numbers, and establish a dashboard contract and decision cadence so measurement drives action instead of accumulating dashboards. The skill works across SaaS, internal tools, public services, and consumer products — not just one business model.

## What You Get

| Directory | What it provides |
|-----------|-----------------|
| [`SKILL.md`](SKILL.md) | Core methodology: metric trees, tracking plans, instrumentation QA, privacy-aware measurement, dashboard contracts, and decision cadence. Includes the Loading Guide, When to Use / When Not to Use, and related-skill routing. |
| [`references/discovery-brief.md`](references/discovery-brief.md) | Bounded discovery brief mapping existing metrics content across product-strategy, go-to-market, financial-modeling, data-engineering, and data-scientist, with ownership boundaries. |
| [`references/metric-tree.md`](references/metric-tree.md) | How to build, validate, and maintain a metric tree: leading/lagging indicators, countermetrics, ownership rules, measurability gates, and examples across product types. |
| [`templates/tracking-plan.md`](templates/tracking-plan.md) | Fillable tracking plan template: event taxonomy, property schema, identity resolution, session definition, data quality rules, and ownership fields. |
| [`templates/instrumentation-qa-checklist.md`](templates/instrumentation-qa-checklist.md) | Checklist for verifying instrumentation quality across client, server, pipeline, and end-to-end layers before trusting a metric on a dashboard. |
| [`templates/outcome-review.md`](templates/outcome-review.md) | Template for a recurring product outcome review: metric tree health, countermetric checks, decision log, and metric deprecation/retirement decisions. |
| [`evals/evals.json`](evals/evals.json) | Output-quality evaluation cases covering new features, internal products, public services, conflicting metrics, and unmeasurable-North-Star rejection. |

## Quick Start

Load the skill when your task involves defining product metrics, designing tracking, or auditing instrumentation. The agent will follow the working method in `SKILL.md`:

1. Define the outcome and decompose into a metric tree (`references/metric-tree.md`).
2. Verify measurability — reject unmeasurable metrics rather than fabricate proxies.
3. Produce a tracking plan contract (`templates/tracking-plan.md`).
4. QA the instrumentation before trusting the dashboard (`templates/instrumentation-qa-checklist.md`).
5. Establish a decision cadence and outcome review rhythm (`templates/outcome-review.md`).

No API keys, external services, or software dependencies are required. The skill is purely methodological.

## Triggers

Load this skill when the user asks about:

- Defining product metrics, North Star, success metrics, or OKR measurement
- Building a metric tree, leading/lagging indicators, or countermetrics
- Designing an event taxonomy, tracking plan, or analytics specification
- Auditing instrumentation quality or analytics data trustworthiness
- Setting up product funnels, cohort definitions, retention measurement, or adoption tracking
- Creating dashboard contracts with metric definitions, sources, and ownership
- Resolving conflicting metric definitions between teams
- Establishing a product measurement cadence or outcome review process
- Privacy-aware measurement design (consent boundaries, minimization, aggregation thresholds)

Do **not** load for statistical inference or experiment design (use `data-scientist`), data pipeline implementation (use `data-engineering`), data architecture (use `data-architect`), observability or infrastructure monitoring (use `site-reliability-engineering`), or general BI dashboard building.

## Requirements

- No software dependencies, API keys, or external services required.
- Compatible with any Agent Skills harness that supports markdown skill loading.
- Purely methodological — all outputs are documents (metric trees, tracking plans, checklists, review templates).
