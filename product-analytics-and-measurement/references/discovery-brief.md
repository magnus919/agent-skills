# Discovery Brief: Product Analytics and Measurement

## Purpose

This brief maps existing metrics-related content across the agent-skills catalog and resolves ownership boundaries for the new `product-analytics-and-measurement` skill. It ensures the skill adds net-new capability rather than duplicating existing methodology.

## Skills Surveyed

### product-strategy (`../product-strategy/SKILL.md`)

**What it owns:** North Star metric definition, product vision, competitive positioning, roadmap prioritization (RICE, Kano, OST), product-market fit assessment (Sean Ellis test, retention curves), market sizing (TAM/SAM/SOM), platform strategy, and product lifecycle management.

**Boundary:** Product-strategy defines *what* the North Star is at the strategic level. It does not specify *how* to measure it — it names the metric (e.g., "weekly active users") but does not define the event taxonomy, tracking plan, instrumentation QA, or dashboard contract needed to produce that metric reliably. Product-strategy's retention curves are strategic frameworks (e.g., "does the retention curve flatten above 30%?"), not operational cohort definitions with identity resolution and session boundary rules.

**Handoff:** This skill (product-analytics-and-measurement) receives the North Star and strategic metric choices from product-strategy and operationalizes them into measurable, governed evidence.

### go-to-market (`../go-to-market/SKILL.md`)

**What it owns:** Positioning and messaging (April Dunford), acquisition channel strategy (paid, organic, PLG, SLG), brand architecture, growth modeling (CAC/LTV by channel, cohort analysis by acquisition channel), market entry strategy, and competitive response.

**Boundary:** GTM's growth modeling uses CAC/LTV and cohort analysis as strategic frameworks for channel investment decisions. It does not define how those cohorts are constructed in the analytics system, how identity is resolved across anonymous-to-known-user transitions, or how the event data feeding CAC/LTV calculations is instrumented and QA'd. GTM's funnel metrics are channel-level; this skill defines the underlying event and session model that makes those funnels computable.

**Handoff:** This skill provides the measurement infrastructure (event definitions, identity resolution, tracking plan) that GTM's growth models consume. The two skills are complementary: GTM asks "which channel delivers the best CAC/LTV?", this skill ensures CAC and LTV are computed from trustworthy, well-instrumented data.

### financial-modeling (`../financial-modeling/SKILL.md`)

**What it owns:** Assumptions-led financial models, unit economics (CAC, LTV, contribution margin, payback), pricing strategy, fundraising scenarios, cap tables, and SaaS operating metrics (ARR/MRR, churn, NDR, Rule of 40, Magic Number, burn multiple).

**Boundary:** Financial-modeling defines *what* these metrics mean for financial analysis and scenario planning. It does not define the event-level instrumentation or tracking plan that produces the raw data feeding those metrics. For example, financial-modeling defines churn as "the percentage of revenue or customers lost over a period," but does not specify how churn events are captured, how the customer lifecycle state machine is modeled in the analytics system, or how to QA the churn calculation end-to-end.

**Handoff:** This skill defines the measurement contracts (event definitions, data quality rules, metric formulas at the analytics layer) that financial-modeling's SaaS metrics depend on. Financial-modeling is the consumer of well-measured ARR, churn, and NDR; this skill is the producer.

### data-engineering (`../data-engineering/SKILL.md`)

**What it owns:** Database operations, ETL/ELT pipeline design (dbt patterns, incremental loading), SQL analytical patterns, data quality monitoring at the pipeline level, schema migration, and storage infrastructure management.

**Boundary:** Data-engineering implements the pipelines that move and transform data. This skill defines *what* data should exist (the tracking plan, the event schema, the quality rules) and *how to verify* it is correct (instrumentation QA). Data-engineering then implements the pipeline that ingests, transforms, and stores that data. The handoff is: this skill produces a tracking plan contract; data-engineering builds the pipeline to ingest it.

**Handoff:** Clear and complementary. This skill is the "what and why" of measurement data; data-engineering is the "how" of moving and storing it. Neither duplicates the other.

### data-scientist (`../data-scientist/SKILL.md`)

**What it owns:** Statistical inference, experimental design (A/B testing, power analysis), causal inference (DAGs, IV, RDD, DID), regression and Bayesian analysis, model selection, and research methodology.

**Boundary:** Data-scientist analyzes data that has already been collected and structured. This skill ensures that the data feeding those analyses is well-defined, properly instrumented, and trustworthy. For example, data-scientist runs the statistical test on an A/B experiment; this skill ensures the experiment's success metric is observable, properly tracked, and QA'd before the test begins.

**Handoff:** Data-scientist is the consumer of well-measured data. This skill ensures the measurement foundation exists before statistical analysis begins.

## What This Skill Owns

| Owned capability | Not owned by any existing skill |
|-----------------|--------------------------------|
| Metric tree construction and governance | No skill decomposes a North Star into an owned, observable, actionable tree with leading/lagging indicators and countermetrics. |
| Event taxonomy and tracking plan contracts | No skill defines event naming conventions, property schemas, identity resolution rules, session boundaries, data quality rules, and event ownership in a unified contract. |
| Instrumentation QA methodology | No skill provides a systematic checklist for verifying instrumentation correctness across client, server, pipeline, and end-to-end layers. |
| Dashboard contracts | No skill pins metric definitions, data sources, refresh cadences, and ownership into a dashboard-level contract. |
| Measurement decision cadence | No skill defines the rhythm (daily/weekly/monthly/quarterly) at which metrics are reviewed, deprecated, and updated. |
| Privacy-aware measurement design | No skill addresses consent boundaries, minimization, aggregation thresholds, and retention in the context of product measurement. |
| Cross-team metric conflict resolution | No skill provides a framework for resolving when two teams define the same metric differently. |

## What This Skill Routes (Does Not Own)

| Routed capability | Target skill |
|------------------|-------------|
| Statistical inference, experiment design, causal analysis | `data-scientist` |
| Pipeline implementation, ETL/ELT, dbt models | `data-engineering` |
| Data architecture, storage selection, schema design at infrastructure level | `data-architect` |
| North Star and product vision definition | `product-strategy` |
| Growth modeling, CAC/LTV by channel | `go-to-market` |
| Financial SaaS metrics (ARR, NDR, Rule of 40) | `financial-modeling` |
| System observability, error budgets, infrastructure monitoring | `site-reliability-engineering` |
| General BI dashboard building and data visualization | BI tooling (external to this catalog) |

## Product Scope Beyond SaaS

This skill is designed to work across product types, not only SaaS:

- **SaaS products** — subscription metrics, activation funnels, feature adoption, churn measurement.
- **Internal tools** — productivity metrics, workflow completion rates, time-to-task, adoption within the organization.
- **Public services** — service delivery outcomes, accessibility metrics, equity measurement, constituent satisfaction.
- **Consumer products** — engagement loops, retention cohorts, content consumption patterns, network effects.

The metric tree and tracking plan templates are product-type-agnostic. Examples in reference files are labeled with their product context so readers can adapt, not blindly copy.

## Key Design Decisions

1. **Prose routing to not-yet-landed skills.** Five consumer skills (product-roadmapping-and-portfolio, product-experimentation, product-adoption, conditional-customer-success, product-lifecycle-learning) are referenced by name in prose only, not as markdown links, because they do not yet exist in the catalog. When they land, those prose references become resolvable links.

2. **No universal benchmarks.** Every threshold, target, or benchmark cited in examples is explicitly labeled with its product, market, stage, and business model context. The skill refuses to provide "industry standard" conversion rates or retention benchmarks without context.

3. **Reject unmeasurable metrics.** If a requested metric cannot be observed from available or feasibly instrumented data sources, the skill rejects it rather than fabricating a proxy. The rejection names the missing instrumentation constraint so the team knows what would need to change to make the metric measurable.

4. **Minimal but complete.** The skill covers the full measurement lifecycle without duplicating existing specialist skills. It adds net-new capability in the areas no existing skill covers.
