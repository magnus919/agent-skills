# Production-Excellence Bundle — Bounded Discovery Brief

## Purpose

This brief records the pre-implementation survey of existing production and release
skills in the `magnus919/agent-skills` repository. It establishes what the
production-excellence bundle owns, what it routes to, and what it must not duplicate.
It satisfies acceptance criterion "A bounded discovery brief compares the bundle with
existing production and release skills" (issue #195).

## Surveyed skills

Each skill below was inspected before the bundle was authored. For every skill the
conclusion is the same: it owns a deep specialist domain and does **not** own the
cross-domain acceptance and handoff layer that assembles evidence into a launch or
operational decision.

| Skill | What it owns | What the bundle does NOT duplicate |
|---|---|---|
| [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) | SLO definition, error budgets, incident response, operational recovery, capacity planning, toil reduction | Incident command, on-call procedures, SLO math, error-budget policy, toil automation |
| [release-engineering](../../release-engineering/SKILL.md) | Release pipelines, versioning, promotion, rollout, rollback mechanics, deployment strategies | CI/CD pipeline design, artifact promotion, canary/blue-green mechanics, release-please configuration |
| [platform-engineering](../../platform-engineering/SKILL.md) | Internal developer platforms, paved roads, service catalogs, infrastructure APIs, Golden Paths | Platform architecture, IDP design, service catalog implementation, infrastructure-as-code |
| [secure-software-engineering](../../secure-software-engineering/SKILL.md) | Threat modeling, secure design, security review, vulnerability assessment, trust boundaries | STRIDE/OWASP methodology, security-review procedure, threat-model facilitation |
| [data-engineering](../../data-engineering/SKILL.md) | Database operations, ETL/ELT pipelines, data quality, schema migration, storage infrastructure | Pipeline design, dbt patterns, SQL analytical patterns, storage architecture |
| [qa-methodology](../../qa-methodology/SKILL.md) | Test strategy, regression coverage, CI quality gates, verification planning, test-level taxonomy | Test-case design, regression-suite management, test-automation framework design |
| [verification-methodology](../../verification-methodology/SKILL.md) | Verification verdicts, boundary labeling, evidence standards, gap declaration | Verification-protocol design, evidence-boundary classification |
| [production-readiness](../../production-readiness/SKILL.md) | Risk-scaled evidence packet, go/no-go/defer/exception launch decisions with accountable owners | The 11-category evidence checklist, risk-class assignment, accountable-owner identification |
| [migration-engineering](../../migration-engineering/SKILL.md) | Safe cross-system migrations — expand/contract, compatibility windows, dual-running, backfills, reconciliation, cutover, deprecation, recovery paths | Migration-strategy design, compatibility-window management, cutover sequencing |
| [resilience-and-recovery](../../resilience-and-recovery/SKILL.md) | Failure modes, degradation choices, RTO/RPO, restore testing, DR, game days, failover, data integrity, recovery communication | Game-day design, DR-runbook authoring, failover-procedure definition |
| [capacity-and-cost-engineering](../../capacity-and-cost-engineering/SKILL.md) | Demand/capacity/scaling/utilization models, unit-cost connection to SLO decisions, cost-constrained scenario analysis | Capacity-model construction, cost-attribution accounting, quota/rate-limit engineering |
| [incident-learning](../../incident-learning/SKILL.md) | Observed facts, causal hypotheses, contributing conditions, follow-up work mapping, verified closure | Incident-analysis facilitation, causal-hypothesis testing, follow-up-ticket management |
| [product-lifecycle-learning](../../product-lifecycle-learning/SKILL.md) | Expected-vs-observed outcome comparison, assumption/decision updates, continue/improve/harvest/pivot/pause/retire choices | Lifecycle-review facilitation, outcome-comparison analysis |

## Boundary statement

The production-excellence bundle owns the **acceptance and handoff layer**:

- Assembling cross-domain evidence (readiness, migration, recovery, capacity/cost,
  incident-learning) into a single production decision record.
- Running the gate model: go, no-go, defer, exception, escalation — each with
  conditions, evidence, and accountable owners.
- Producing the operational handoff record for the team that will own the service
  in production.
- Routing post-launch outcomes into incident-learning and product-lifecycle-learning
  so that production evidence flows back into decisions.

It does **not** own any specialist's runbook. It does not own incident command
(SRE), release pipeline mechanics (release-engineering), platform architecture
(platform-engineering), threat modeling (secure-software-engineering), data
pipeline design (data-engineering), or test-strategy design (qa-methodology). It
composes them — it never re-derives their methods.

## What existing bundles do NOT cover

The four pre-existing bundles were also surveyed:

- **neckbeard** owns the issue-to-PR delivery journey (9-phase SDLC). It does not
  own the production acceptance and handoff that happens after delivery.
- **workflow-architect** owns workflow discovery and skill-bundle generation. It
  does not own production decision-making.
- **tailscale** owns the Headscale/Tailscale VPN ecosystem. It is domain-specific
  networking, not production governance.
- **research-and-vault** owns the research-to-notes sequence. It is a knowledge
  workflow, not a production workflow.

None of them fill the gap this bundle fills: the cross-domain evidence assembly and
launch/operational decision layer that sits between delivery (neckbeard's phase 9)
and ongoing production operations.

## Decision: bundle owns the acceptance layer, not the specialists' runbooks

The production-excellence bundle is the thin composition layer that:

1. Reads evidence from the five production-domain specialists (production-readiness,
   migration-engineering, resilience-and-recovery, capacity-and-cost-engineering,
   incident-learning).
2. Reads applicable evidence from the existing production specialists (SRE, release,
   platform, security, data, QA).
3. Assembles that evidence into a gate decision (go/no-go/defer/exception/escalation).
4. Produces an operational handoff record.
5. Routes post-launch learning back into incident-learning and product-lifecycle-learning.

It is deliberately thin. It adds no new methodology beyond the acceptance and handoff
contract. Every specialist skill remains the authoritative source for its domain.
