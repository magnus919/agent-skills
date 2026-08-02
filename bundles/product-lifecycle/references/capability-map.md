# Capability Map — product-lifecycle bundle

This map indexes product management capabilities to their owning specialist
skills. When a user needs a specific capability, load the owning skill directly
rather than traversing the full lifecycle. The lifecycle bundle provides
cross-phase routing; this map provides point lookup.

## Capability → Owning skill

| Capability area | Owning skill |
|---|---|
| Stakeholder discovery, user research, requirements elicitation | [product-discovery](../../product-discovery/SKILL.md) |
| Product vision, strategy, competitive positioning | [product-strategy](../../product-strategy/SKILL.md) |
| Strategic frameworks (Five Forces, Blue Ocean, Ansoff) | [strategy-frameworks](../../strategy-frameworks/SKILL.md) |
| Market sizing (TAM/SAM/SOM), product-market fit | [product-strategy](../../product-strategy/SKILL.md) |
| Outcome roadmaps, Now/Next/Later views | [product-roadmapping-and-portfolio](../../product-roadmapping-and-portfolio/SKILL.md) |
| Strategic bets, portfolio management, continue/pause/kill | [product-roadmapping-and-portfolio](../../product-roadmapping-and-portfolio/SKILL.md) |
| Prioritization frameworks (RICE, MoSCoW, Kano, OST) | [product-methodology](../../product-methodology/SKILL.md) |
| Information architecture, task flows, interaction design | [product-design-and-ux](../../product-design-and-ux/SKILL.md) |
| Experiment design, method selection, guardrails | [product-experimentation](../../product-experimentation/SKILL.md) |
| Statistical design, causal inference, A/B analysis | [data-scientist](../../data-scientist/SKILL.md) |
| Specification, acceptance criteria, phase gates | [spec-driven-development](../../spec-driven-development/SKILL.md) |
| Work breakdown, dependency mapping, rollout planning | [implementation-planning](../../implementation-planning/SKILL.md) |
| Release process, progressive delivery, versioning | [release-engineering](../../release-engineering/SKILL.md) |
| Production readiness, launch evidence, go/no-go | [production-readiness](../../production-readiness/SKILL.md) |
| Onboarding, activation, feature discovery, sustained use | [product-adoption](../../product-adoption/SKILL.md) |
| Metric trees, tracking plans, outcome measurement | [product-analytics-and-measurement](../../product-analytics-and-measurement/SKILL.md) |
| Customer success, account health, renewals (conditional) | [conditional-customer-success](../../conditional-customer-success/SKILL.md) |
| Outcome review, assumption updates, retirement decisions | [product-lifecycle-learning](../../product-lifecycle-learning/SKILL.md) |
| Decision rights, governance cadences, evidence standards | [product-operations-and-governance](../../product-operations-and-governance/SKILL.md) |
| Financial modeling, unit economics, pricing | [financial-modeling](../../financial-modeling/SKILL.md) |
| Go-to-market strategy, positioning, acquisition | [go-to-market](../../go-to-market/SKILL.md) |
| Privacy requirements, data lifecycle, retention | [privacy-engineering](../../privacy-engineering/SKILL.md) |
| Security requirements, threat modeling, secure design | [secure-software-engineering](../../secure-software-engineering/SKILL.md) |
| Legal analysis, regulatory landscape, IP strategy | [legal-strategy](../../legal-strategy/SKILL.md) |
| Data pipelines, ETL, schema design | [data-engineering](../../data-engineering/SKILL.md) |
| Production resilience, recovery, game days | [resilience-and-recovery](../../resilience-and-recovery/SKILL.md) |
| Capacity planning, cost engineering, SLO-cost tradeoffs | [capacity-and-cost-engineering](../../capacity-and-cost-engineering/SKILL.md) |
| Migration planning, expand/contract, cutover | [migration-engineering](../../migration-engineering/SKILL.md) |
| Incident learning, post-incident improvement | [incident-learning](../../incident-learning/SKILL.md) |
| Site reliability, SLOs, alerting, incident response | [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) |
| Platform engineering, infrastructure, CI/CD | [platform-engineering](../../platform-engineering/SKILL.md) |
| QA strategy, test planning, quality gates | [qa-methodology](../../qa-methodology/SKILL.md) |
| Verification methodology, evidence trails | [verification-methodology](../../verification-methodology/SKILL.md) |
| Software delivery lifecycle (SDLC) | [neckbeard](../../bundles/neckbeard/SKILL.md) |

## Cross-cutting concerns

These capabilities span multiple phases and are loaded on trigger, not by phase:

| Cross-cutting concern | Owning skill | When loaded |
|---|---|---|
| Product governance, decision rights, cadences | [product-operations-and-governance](../../product-operations-and-governance/SKILL.md) | When setting up or changing governance; at phase boundaries where a decision needs formal authority |
| Prioritization (RICE, MoSCoW, Kano, OST) | [product-methodology](../../product-methodology/SKILL.md) | When a phase produces alternatives that need ranking |
| Privacy and data protection | [privacy-engineering](../../privacy-engineering/SKILL.md) | When any phase handles PII, consent, retention, or data flows |
| Security | [secure-software-engineering](../../secure-software-engineering/SKILL.md) | When any phase touches trust boundaries, auth, or sensitive data |
| Evidence standards and verification | [verification-methodology](../../verification-methodology/SKILL.md) | At every phase gate where evidence is required |
