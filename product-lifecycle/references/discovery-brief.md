# Bounded Discovery Brief — product-lifecycle bundle

## Bundle boundary

The `product-lifecycle` bundle is a thin orchestration umbrella that composes
existing product skills across nine lifecycle phases — from discovery through
post-launch learning. It provides **cross-skill routing and evidence handoff**.
It is NOT another product methodology and does NOT duplicate any specialist's
step-by-step method.

The bundle answers a specific gap: the catalog has strong individual product
skills (discovery, strategy, UX, experimentation, analytics, adoption,
methodology, GTM, financial modeling, operations/governance, lifecycle
learning) but no composition layer that routes a product through a coherent
lifecycle with phase-entry evidence, handoff artifacts, and stop/escalation
rules. A user who wants to evaluate a new product idea end-to-end currently
must manually chain skills. This bundle provides that routing.

## Comparison with existing bundles

### bundles/neckbeard

neckbeard is an SDLC delivery operating model — it routes a **code change**
through framing, discovery, design, implementation, review, verification,
delivery, and learning. It owns the cross-stage contracts for software delivery
(change contract, evidence ledger, stop rules) and composes specialist
engineering skills. The product-lifecycle bundle is complementary: it routes a
**product** through its lifecycle phases (discovery, strategy, roadmap, UX,
experimentation, delivery handoff, adoption, success, lifecycle review) and
composes specialist product skills. The delivery-handoff phase of the product
lifecycle explicitly hands off to production skills — production-readiness,
release-engineering, and the neckbeard change-request journey for the
implementation and delivery of product decisions. The two bundles intersect at
the delivery-handoff boundary but own different domains.

### bundles/workflow-architect

workflow-architect is a meta-skill that discovers a **person's** workflow
through conversation or observation and generates a tailored skills bundle. It
is an interrogation/observation tool, not a product management operating model.
The product-lifecycle bundle does not discover or generate workflows; it
provides a fixed, opinionated lifecycle routing table for product work. A user
might run workflow-architect to discover their own product workflow and then
use the product-lifecycle bundle as a reference for building it.

### bundles/tailscale

tailscale is a domain-specific infrastructure bundle for self-hosted
Tailscale/Headscale VPN. It has no product management content and no lifecycle
routing. No overlap with product-lifecycle. Mentioned here only for comparison
completeness.

### bundles/research-and-vault

research-and-vault is a thin orchestrator for a repeatable research-to-notes
pipeline: gather sources, extract atomic claims, create durable notes. It
composes web-research and note-taking capabilities. While the
product-lifecycle bundle's discovery phase may consume research outputs,
research-and-vault is a content-capture pipeline, not a product management
lifecycle. No overlap. Mentioned here for comparison completeness.

## Adjacent product skills surveyed

The following specialist skills exist in the catalog and are composed (never
duplicated) by the product-lifecycle bundle:

| Skill | Role in lifecycle |
|---|---|
| `product-discovery` | Phase 1 — stakeholder discovery, requirements, acceptance criteria |
| `product-strategy` | Phase 2 — vision, strategy, competitive positioning, market sizing |
| `product-roadmapping-and-portfolio` | Phase 3 — outcome roadmaps, strategic bets, portfolio views |
| `product-design-and-ux` | Phase 4 — information architecture, task flows, interface contracts |
| `product-experimentation` | Phase 5 — experiment design, method selection, guardrails, readouts |
| `implementation-planning` | Phase 6 — work breakdown, dependency mapping, rollout strategy |
| `spec-driven-development` | Phase 6 — formal specification, phase gates, implementation pipeline |
| `release-engineering` | Phase 6 — release process, progressive delivery, readiness gates |
| `production-readiness` | Phase 6 — risk-scaled launch evidence, go/no-go/defer/exception |
| `product-adoption` | Phase 7 — onboarding, activation, behavior change, sustained use |
| `product-analytics-and-measurement` | Phase 8 — metric trees, tracking plans, outcome measurement |
| `conditional-customer-success` | Phase 8 — success plans, health evidence, renewal signals (conditional) |
| `product-lifecycle-learning` | Phase 9 — outcome review, assumption updates, continue/retire decisions |
| `product-operations-and-governance` | Cross-cutting — decision rights, cadences, evidence standards |
| `product-methodology` | Cross-cutting — RICE, MoSCoW, prioritization frameworks |
| `go-to-market` | Phase 7/8 — positioning, acquisition strategy, growth modeling |
| `financial-modeling` | Phase 2/8 — unit economics, pricing, business model analysis |
| `data-scientist` | Phase 5/8 — statistical design, causal inference, experiment analysis |

Additional skills that may be routed to contextually: `site-reliability-engineering`,
`platform-engineering`, `secure-software-engineering`, `qa-methodology`,
`verification-methodology`, `strategy-frameworks`, `legal-strategy`,
`data-engineering`, `security-audit-methodology`.

## What this bundle does NOT own

- **Product discovery methodology.** Routes to `product-discovery`.
- **Product strategy frameworks.** Routes to `product-strategy` and `strategy-frameworks`.
- **UX design process.** Routes to `product-design-and-ux`.
- **Experimentation statistics and method.** Routes to `product-experimentation` and `data-scientist`.
- **Release engineering, CI/CD, deployment.** Routes to `release-engineering` and `production-readiness`.
- **Analytics instrumentation and pipelines.** Routes to `product-analytics-and-measurement` and `data-engineering`.
- **Customer success account management.** Routes to `conditional-customer-success` (conditional on product type).
- **Software delivery lifecycle.** Routes to `bundles/neckbeard` and `implementation-planning`.
- **Financial modeling and pricing.** Routes to `financial-modeling`.
- **GTM strategy and execution.** Routes to `go-to-market`.
- **Privacy, security, legal compliance.** Routes to `privacy-engineering`, `secure-software-engineering`, `legal-strategy`.
- **A universal B2B SaaS product model.** The bundle does not assume B2B SaaS. Customer-success routing is
  CONDITIONAL; internal tools, public-service products, transactional products, and consumer products proceed
  without it. Phase contracts use product-type-agnostic language.

## Design decisions

1. **Thin umbrella with real routing links.** Every phase routes to a named specialist skill via a
   relative markdown link. The umbrella SKILL.md never restates a specialist's step-by-step method.
2. **Evidence ledger as cross-phase handoff.** Each phase writes to a lifecycle evidence ledger; the
   next phase reads it. This is the artifact that makes the bundle composable — it is the handoff
   contract between phases.
3. **Stop/escalation at every phase.** Every phase has explicit escalation behavior. The bundle
   supports stopped paths (e.g., discovery shows no viable problem, experimentation disproves the
   hypothesis, adoption fails to meet thresholds) as legitimate outcomes.
4. **Conditional customer-success routing.** The bundle explicitly gates customer-success routing on
   product type. Products without accounts, renewals, QBRs, or customer-success teams proceed without
   loading `conditional-customer-success`.
5. **Capability map.** A separate reference (`capability-map.md`) maps capability areas to owning
   skills so users can discover which skill to load for a specific need without traversing the full
   lifecycle table.
