# Discovery Brief: Capacity and Cost Engineering

## Survey scope

This brief surveys adjacent skills in the agent-skills catalog to define the ownership boundaries of `capacity-and-cost-engineering`. The goal is to own technical capacity models, unit economics connected to infrastructure decisions, budget and quota controls, load/soak evidence standards, and cost-performance tradeoff records — without duplicating financial P&L modeling, infrastructure implementation, SRE operations, product analytics measurement, production-readiness assembly, or product roadmapping.

## Skills surveyed

### financial-modeling

**What financial-modeling owns:** P&L statements, balance sheets, cash-flow models, fundraising scenarios, cap tables, SaaS operating metrics (ARR/MRR, churn, NDR, Rule of 40, Magic Number, burn multiple), pricing strategy, and segment-level unit economics (CAC, LTV, contribution margin, CAC payback). It is the authoritative owner of financial models, SaaS metrics, and fundraising mathematics.

**Boundary:** Financial-modeling owns the *financial* view of cost and unit economics — what a customer segment costs to acquire and serve, how revenue and expenses compose a P&L, and whether the business model is viable. Capacity-and-cost-engineering owns the *technical* view — what a request costs in compute and network, how capacity scales with demand, what a service costs to operate at a given SLO, and whether a budget constraint permits a specific infrastructure decision. Financial-modeling's unit economics answer "is this segment profitable?"; capacity-and-cost-engineering's unit economics answer "what does it cost to serve one more request and how do we optimize that without breaking SLOs?"

**Routing decision:** Capacity-and-cost-engineering routes P&L construction, fundraising scenarios, SaaS-metric definitions, and pricing-strategy work to [financial-modeling](../financial-modeling/SKILL.md). Financial-modeling is the authoritative source for financial statements, SaaS metrics, and fundraising. Capacity-and-cost-engineering owns technical unit cost (cost per request, cost per GB stored, cost per provisioned capacity unit), capacity-driven cost projections, and cost-performance tradeoff records — the work that connects infrastructure spend to reliability and demand decisions.

### platform-engineering

**What platform-engineering owns:** Infrastructure as code, CI/CD pipelines, container orchestration, service networking, secret management, observability strategy, cloud architecture, and cost governance at the platform layer. It builds and operates the delivery platform.

**Boundary:** Platform-engineering owns the *implementation* of infrastructure that satisfies capacity and cost requirements — provisioning compute, configuring autoscaling, setting up cost-allocation tags, and implementing cloud resource governance. Capacity-and-cost-engineering owns the *requirements and models*: what the capacity model predicts, what the unit cost should be, what the budget threshold is, and how cost constraints interact with SLOs. Platform engineering implements the autoscaling group; capacity-and-cost-engineering defines the scaling policy, the cost ceiling, and the evidence standard that proves the scaling meets demand under load.

**Routing decision:** Capacity-and-cost-engineering routes infrastructure implementation, autoscaling configuration, cost-allocation tag setup, and cloud resource provisioning to [platform-engineering](../platform-engineering/SKILL.md). Platform-engineering's IaC patterns and cloud-platforms reference are the authoritative sources for implementation. Capacity-and-cost-engineering owns the capacity model, the unit-cost calculation, the budget threshold, and the load/soak evidence that validates the implementation.

### site-reliability-engineering

**What SRE owns:** SLO/SLI framework, error budget governance, incident command, on-call operations, blameless postmortems, monitoring and alerting, toil elimination, and product-focused reliability. It owns the live-service health boundary and the operational response to reliability events.

**Boundary:** SRE owns the reliability target (SLO) and the error budget that governs how much unreliability is acceptable. Capacity-and-cost-engineering owns the capacity and cost dimensions that interact with that reliability target: how much capacity is needed to meet the SLO at projected demand, what it costs to provision that capacity, and what tradeoffs exist when budget constraints prevent provisioning to the reliability target. SRE defines the SLO; capacity-and-cost-engineering calculates what it costs to meet it and what the degraded-capacity alternative looks like.

**Routing decision:** Capacity-and-cost-engineering routes SLO definition, error budget policy, incident command, and reliability engineering to [site-reliability-engineering](../site-reliability-engineering/SKILL.md). SRE is the authoritative source for reliability targets. Capacity-and-cost-engineering owns the SLO-cost tradeoff record — the artifact that makes the cost of a reliability target explicit and records the decision when budget constrains the achievable SLO.

### product-analytics-and-measurement

**What product-analytics-and-measurement owns:** Metric trees, event taxonomies, tracking plans, instrumentation QA, dashboard contracts, product funnels, cohort analysis, and measurement governance. It turns intended product outcomes into observable, governed evidence.

**Boundary:** Product-analytics owns the *demand signal* — user traffic patterns, growth rates, feature adoption, and usage trends that drive capacity forecasts. Capacity-and-cost-engineering consumes those demand signals as inputs to capacity models but does not own the instrumentation or metric definitions that produce them. Product-analytics tells us how many users are coming; capacity-and-cost-engineering translates that into what infrastructure and spend are required.

**Routing decision:** Capacity-and-cost-engineering routes demand measurement, traffic forecasting instrumentation, event taxonomy, and tracking-plan design to [product-analytics-and-measurement](../product-analytics-and-measurement/SKILL.md). Product-analytics is the authoritative source for demand signals. Capacity-and-cost-engineering owns the capacity model that translates demand into infrastructure requirements and cost projections.

### production-readiness

**What production-readiness owns:** Cross-domain evidence assembly for launch decisions (go/no-go/defer/exception). It defines the minimum production evidence packet by risk class, maps every evidence category (ownership, SLOs, observability, security, data, capacity, cost, etc.) to a named source or gap annotation, and produces a launch decision with an accountable owner.

**Boundary:** Production-readiness *consumes* capacity and cost evidence as two of its 11 evidence categories (category 10: Capacity, category 11: Cost). Capacity-and-cost-engineering *produces* that evidence: the capacity model, load-test report, cost projection, and budget approval that production-readiness requires for its launch decision. Production-readiness assembles the go/no-go verdict; capacity-and-cost-engineering provides the capacity and cost dimensions of the evidence packet.

**Routing decision:** Capacity-and-cost-engineering feeds [production-readiness](../production-readiness/SKILL.md) as a primary evidence producer for the Capacity and Cost evidence categories. Production-readiness is the consumer of capacity-and-cost-engineering outputs. The capacity model, load/soak test report, unit-economics record, and budget/quota decision are the artifacts that satisfy categories 10 and 11 of the production-readiness evidence checklist.

### product-roadmapping-and-portfolio

**What product-roadmapping-and-portfolio owns:** Outcome-based roadmaps (Now/Next/Later), strategic-bet management, capacity allocation at the portfolio level, dependency and confidence mapping, scenario planning, continue/pause/kill/revisit criteria, and stakeholder narratives. It manages the portfolio of strategic investments.

**Boundary:** Product-roadmapping owns *portfolio-level* capacity allocation — how many bets can be pursued in parallel, which bets share engineering capacity, and how capacity constraints affect roadmap sequencing. Capacity-and-cost-engineering owns *infrastructure-level* capacity — what compute, storage, and network resources are needed to operate the services that deliver those bets, and what they cost. A roadmap decision to pursue three bets in parallel creates demand; capacity-and-cost-engineering models whether the infrastructure can support that demand and what it will cost.

**Routing decision:** Capacity-and-cost-engineering routes portfolio capacity allocation, bet sequencing, and roadmap tradeoffs to [product-roadmapping-and-portfolio](../product-roadmapping-and-portfolio/SKILL.md). Product-roadmapping owns the strategic capacity decisions. Capacity-and-cost-engineering owns the technical capacity model that confirms or constrains those decisions with infrastructure-level evidence.

### resilience-and-recovery

**What resilience-and-recovery owns:** Resilience design, degradation-path definition, recovery verification through exercises (game days, DR tests, restore tests), RTO/RPO decision records, and exercise evidence standards. It owns the work that happens before and between incidents — designing for failure and proving recovery capability.

**Boundary:** Resilience-and-recovery's degradation-path design (which functions are shed, in what order, under what conditions) directly constrains capacity-and-cost-engineering's degraded-mode capacity model. Capacity-and-cost-engineering answers: if the recommendation engine is shed (resilience decision), what does the remaining capacity requirement look like and what does it cost? Resilience defines what to shed; capacity-and-cost-engineering models the capacity and cost of the degraded state.

**Routing decision:** Capacity-and-cost-engineering routes degradation-path design, recovery verification, and RTO/RPO decision records to [resilience-and-recovery](../resilience-and-recovery/SKILL.md). Resilience-and-recovery owns the degradation design. Capacity-and-cost-engineering owns the capacity-and-cost model of degraded states and ensures that load/soak evidence covers degraded-mode capacity scenarios.

## What capacity-and-cost-engineering does NOT own

- **Financial P&L, fundraising, SaaS metrics (ARR/churn/NDR), or pricing strategy**: owned by financial-modeling. Capacity-and-cost-engineering does not build financial statements, calculate CAC/LTV, or model fundraising rounds.
- **Infrastructure implementation**: owned by platform-engineering. Capacity-and-cost-engineering does not write Terraform, configure autoscaling groups, or provision resources.
- **SLO definition and error budget governance**: owned by site-reliability-engineering. Capacity-and-cost-engineering does not define SLOs or manage error budgets — it models the cost and capacity implications of SLO choices.
- **Demand measurement and traffic instrumentation**: owned by product-analytics-and-measurement. Capacity-and-cost-engineering consumes demand signals; it does not own the tracking plan or metric tree.
- **Production launch decisions**: owned by production-readiness. Capacity-and-cost-engineering provides capacity and cost evidence; it does not make the go/no-go call.
- **Portfolio capacity allocation and roadmap sequencing**: owned by product-roadmapping-and-portfolio. Capacity-and-cost-engineering provides infrastructure-capacity evidence; it does not decide which bets to pursue or in what order.
- **Degradation-path design and recovery verification**: owned by resilience-and-recovery. Capacity-and-cost-engineering models the capacity and cost of degraded states; it does not design or exercise the degradation path.

## Summary

Capacity-and-cost-engineering fills a gap between financial modeling (which owns the business view of cost), platform engineering (which implements infrastructure), SRE (which owns reliability targets), product analytics (which owns demand signals), production-readiness (which consumes capacity/cost evidence), product roadmapping (which allocates portfolio capacity), and resilience-and-recovery (which owns degradation design). It is the method for modeling technical capacity, calculating unit cost, defining budget and quota controls, requiring load/soak evidence, and making cost-performance tradeoffs explicit — producing evidence that feeds production-readiness decisions and constrains or supports roadmap and reliability choices.
