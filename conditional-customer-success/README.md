# Conditional Customer Success — recurring human-relationship practices

Guide customer-success practices for products with recurring human
relationships: success plans, health evidence, renewal and expansion signals,
quarterly business reviews (QBRs), handoffs to product/support/engineering,
escalation paths, and closed-loop Voice of Customer operations. This skill is
**conditional** — it loads only when the product has accounts, renewals, QBRs,
or a customer-success team. When those conditions are absent, it declines and
routes the caller to the appropriate alternative.

## Why Install This Skill

Many products have human relationships with their customers — account managers,
renewal conversations, quarterly business reviews, success plans, and
structured escalation paths. When those relationships exist, customer-success
practice brings discipline: evidence-based health tracking instead of gut-feel
red accounts, structured escalation instead of ad-hoc fire drills, and
closed-loop feedback that ensures customer insights reach the product team and
the customer hears back what happened.

This skill fills a gap in the catalog: no dedicated customer-success
capability existed. Isolated pieces lived across onboarding, renewal,
expansion, and stakeholder skills, but nothing connected them into a coherent
practice with clear artifacts, evidence standards, and handoff protocols.

After installing, your agent can: assess whether customer-success practice
applies to a given product context (and decline when it does not), build
success plans anchored to customer outcomes, maintain evidence-based health
records that surface conflicting signals rather than hiding them, design
escalation paths with explicit human-judgment gates, run structured QBRs,
handoff account evidence to product/support/engineering teams with context,
and operate a closed-loop Voice of Customer process from insight to product
change to customer communication.

## What You Get

| Directory Entry | What It Provides |
|---|---|
| `SKILL.md` | Core methodology: applicability decision, success plans, health/risk records, escalation, handoffs, closed-loop feedback, QBR structure, privacy and human-judgment boundaries, and routing to related skills. |
| `README.md` | This file — human-facing overview. |
| `references/discovery-brief.md` | Bounded discovery brief: surveys existing onboarding/renewal/expansion/stakeholder content, defines when customer-success applies and when it routes to analytics/adoption/lifecycle-learning. |
| `references/privacy-and-human-judgment.md` | Full privacy and human-judgment boundaries: consent framework, surveillance-risk guidance, decision-support vs. automated-decision rules, escalation-gate requirements. |
| `templates/applicability-decision.md` | Structured applicability assessment — records which preconditions are present/absent and produces a proceed-or-decline verdict. |
| `templates/success-plan.md` | Customer success plan template: desired outcomes, product-capability alignment, measurable milestones, evidence gates, relationship owner. |
| `templates/health-risk-record.md` | Evidence-based health/risk record: signal, source, trend, confidence, and conflicting-signal tracking per dimension. |
| `templates/escalation-and-feedback-closure.md` | Escalation path definition template and closed-loop feedback closure record. |
| `evals/evals.json` | Schema-valid evaluation manifest with five output-quality cases covering B2B subscription, internal-tool decline, public-service, renewal-risk, and conflicting health evidence. |

## Quick Start

No API keys or external dependencies are required. The skill loads when the
agent detects a product context with accounts, renewals, QBRs, or a
customer-success team.

1. When customer-success practice is considered, the agent first produces an
   applicability decision using the template.
2. If the context qualifies (accounts, renewals, QBRs, or CS team present),
   the agent proceeds through the relevant artifacts.
3. If the context does not qualify (no accounts, no renewals, no QBRs, no CS
   team), the agent declines and routes to product-analytics-and-measurement,
   product-adoption, or product-lifecycle-learning.

To validate the skill:

```sh
ruby scripts/validate-skills.rb
.venv/bin/python scripts/validate-evals.py
.venv/bin/python -m eval_runner conditional-customer-success/evals/evals.json --adapter fake --output-dir /tmp/eval-smoke-cs
```

## Triggers

Load this skill when the user asks about: customer success, success plans,
account health, health scoring, renewal risk, churn risk, expansion signals,
quarterly business reviews (QBRs), executive business reviews, voice of
customer, closed-loop feedback, customer escalation, account management,
account handoff, customer communication after product changes.

Do NOT load when the context has no accounts, no renewals, no QBRs, and no
customer-success team. Examples: internal tools without recurring human
relationships, pure transactional products, public services without
account-based engagement, consumer apps without human CS relationships.

## Requirements

- No API keys, external services, or runtime dependencies.
- The skill references existing skills in the catalog (product-analytics-and-measurement, product-adoption, product-experimentation, go-to-market) and prose-references skills not yet landed (product-lifecycle-learning).
- Templates are markdown files with no special rendering requirements.
