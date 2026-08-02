# Discovery Brief — Conditional Customer Success

**Date**: 2026-08-02
**Scope**: Issue #192 — `feat: add conditional customer-success skill`

## Survey of Existing Content

### What already exists in the catalog

| Existing Skill / Area | Relevant Content | Ownership Boundary |
|---|---|---|
| `go-to-market` | Account planning, customer segmentation, expansion strategy, pricing and packaging | Owns commercial motion (acquisition, conversion, pricing, account-tier design). CS consumes account-tier context; does not own commercial design. |
| `product-adoption` | Onboarding, activation, behavior change, feature discovery, sustained-use review, cohort segmentation, non-SaaS adoption contexts | Owns adoption-side diagnostics and plans. CS consumes adoption signals as health dimensions; does not own adoption methodology. |
| `product-analytics-and-measurement` | Metric trees, tracking plans, instrumentation QA, measurement governance | Owns metric definitions and instrumentation. CS consumes health metrics and evidence from the analytics layer. |
| `product-experimentation` | Experiment design, readout, ship/no-ship decisions, stopping rules | Owns experiment method. CS may propose experiments (intervention tests for at-risk accounts) but does not own experiment design. |
| `product-strategy` | North Star, product vision, strategic context, portfolio thinking | Owns strategic direction. CS informs strategy with customer evidence; does not set strategy. |
| `product-methodology` | Prioritization frameworks (RICE, etc.), discovery techniques, stakeholder alignment | Owns tactical product method. CS consumes prioritization context; does not own RICE or discovery. |
| `financial-modeling` | Unit economics, CAC, LTV, churn modeling, renewal forecasting | Owns financial model. CS provides account-level evidence (health, risk) that feeds financial models. |
| `data-scientist` | Statistical inference, causal analysis, experiment analysis | Owns statistical method. CS routes complex health-signal analysis here. |
| `product-roadmapping-and-portfolio` | Roadmap construction, portfolio balancing, investment allocation | Owns roadmap. CS feeds customer evidence into roadmap inputs; does not own prioritization. |

### What is missing (the gap)

No dedicated customer-success capability exists in the catalog. The existing
skills cover isolated pieces:

- Onboarding and activation (`product-adoption`) but not ongoing success
  management or account health.
- Renewal modeling (`financial-modeling`) but not the human relationship
  practice (QBRs, success plans, escalation).
- Expansion strategy (`go-to-market`) but not the evidence-based
  account-expansion signal from CS.
- Stakeholder alignment (`product-methodology`) but not the closed-loop
  Voice of Customer process.

No skill currently defines:
1. When customer-success practice applies and when it should not be loaded.
2. Success plans as living artifacts connecting customer intent to product
   evidence.
3. Health/risk records that are evidence-based, not automated scores.
4. QBR structure and cadence.
5. Escalation paths with explicit human-judgment gates.
6. Handoff protocols between CS, product, support, and engineering.
7. Closed-loop feedback closure (customer insight → product change → customer
   communication).
8. Privacy boundaries specific to customer-success data.

## Ownership Boundaries

### What this skill owns

- **Applicability decision**: determining whether CS practice applies to a
  given product context.
- **Success plans**: desired outcomes, product-capability alignment,
  milestones, evidence gates, relationship ownership.
- **Health/risk records**: evidence-based, signal-per-dimension, with
  trend, confidence, and conflicting-signal tracking.
- **QBR structure**: evidence-review cadence and format (not sales
  presentations).
- **Escalation paths**: trigger thresholds, named decision-makers, human-
  judgment gates, fallback rules.
- **Handoff protocols**: structured handoffs to product, support, and
  engineering with account context and evidence.
- **Closed-loop feedback**: insight → validation → product decision →
  implementation → customer communication → closure record.
- **Privacy and human-judgment boundaries**: consent framework,
  surveillance-risk guidance, decision-support rules, escalation-gate
  requirements.

### What this skill does NOT own (routes to specialists)

| Concern | Routed to | Why |
|---|---|---|
| Metric definition, tracking plans, instrumentation | `product-analytics-and-measurement` | Owns measurement infrastructure |
| Adoption diagnostics, onboarding design, activation plans | `product-adoption` | Owns adoption lifecycle |
| Statistical analysis of health signals | `data-scientist` | Owns statistical method |
| Commercial pricing, packaging, contract terms | `go-to-market` | Owns commercial design |
| Financial modeling (CAC, LTV, churn) | `financial-modeling` | Owns financial models |
| Experiment design for CS interventions | `product-experimentation` | Owns experiment method |
| Product roadmap decisions from CS evidence | `product-roadmapping-and-portfolio` | Owns roadmap |
| Retirement communication, sunset coordination | `product-lifecycle-learning` | Owns lifecycle closure |

## Routing Decision Tree

```
Is there a recurring human relationship?
├── YES: Are there accounts, renewals, QBRs, OR a CS team?
│   ├── YES → LOAD conditional-customer-success
│   └── NO  → Route to product-adoption (adoption-side) or product-lifecycle-learning
└── NO  → DECLINE. Route to:
    ├── product-analytics-and-measurement (for health metrics)
    ├── product-adoption (for adoption diagnostics)
    └── product-lifecycle-learning (for churn/retirement patterns)
```

## Product-Model Applicability Matrix

| Model | Accounts? | Renewals? | QBRs? | CS Team? | CS Applies? | Adaptation |
|---|---|---|---|---|---|---|
| B2B Subscription | Yes | Yes | Yes | Yes | Full | Standard artifacts |
| Transactional | Partial | No (repeat purchase) | Event-triggered | Sometimes | Partial | Adapted success plans, purchase-frequency health |
| Public Service | Rare | No | Program-review | Rare | Minimal | Service-outcome plans; stricter privacy; often decline |
| Internal Product | Sometimes | No | Internal-service-review | Sometimes | Conditional | Internal SLA plans; often decline |

## Routing to Skills Not Yet Landed

`product-lifecycle-learning` (prose reference) is the destination for:
- Sustained health decline after 2+ remediation attempts.
- Churn-pattern learning across the portfolio.
- Retirement communication plans and migration-support coordination.

Until it lands, this skill records the routing in prose. The routing becomes
a resolved link when the directory exists.
