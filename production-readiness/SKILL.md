---
name: production-readiness
description: >-
  Define the minimum production evidence packet by risk class and produce
  go/no-go/defer/exception launch decisions with accountable owners.
  Cover ownership, user/business outcome, dependencies, SLOs, observability,
  support, security, data, rollback, capacity, and cost — every category with
  a named source or explicit missing-evidence outcome. Route detailed checks
  to existing specialist skills. Do not use for release pipeline mechanics
  (release-engineering) or incident response and SLO operations
  (site-reliability-engineering).
license: MIT
compatibility: Platform-agnostic methodology. No runtime dependency.
metadata:
  tags: production-readiness, launch-decision, evidence-packet, risk-scaled, go-no-go,
    readiness-review, production-evidence, cross-domain, launch-review
---

# Production Readiness

Assemble cross-domain evidence into a launch decision. This skill defines the minimum
production evidence packet by risk class, maps every evidence category to a named source
or an explicit missing-evidence outcome, and produces one of four launch decisions with
an accountable owner. It does not duplicate release checklists, does not produce a
universal risk score, and routes detailed checks to the existing specialist skills.

## When to load this

Load when any of these triggers matches:

- A service, feature, or change is approaching a launch decision and needs a
  production-readiness review.
- Evidence from multiple domains (ownership, SLOs, security, data, support, cost,
  observability) must be assembled into one reviewable record.
- A launch review board, readiness gate, or accountable owner needs a structured
  go / no-go / defer / exception recommendation.
- A migration-dependent release needs evidence that every dependency is ready.
- A low-risk documentation-only change needs proportional (not full-scale) readiness
  review.

## When not to use

- **Release pipeline mechanics** — promotion, canary stages, CI/CD gate configuration,
  versioning, and artifact management. Route to
  [release-engineering](../release-engineering/SKILL.md). Release-engineering owns the
  pipeline gate; production-readiness owns the cross-domain evidence assembly and
  launch decision.
- **Incident response, SLO operations, on-call, and reliability engineering.** Route to
  [site-reliability-engineering](../site-reliability-engineering/SKILL.md).
  SRE owns the live-service health boundary; production-readiness owns the pre-launch
  readiness boundary.
- **Security implementation, threat modeling, or penetration testing.** Route to
  [secure-software-engineering](../secure-software-engineering/SKILL.md) or
  [security-audit-methodology](../security-audit-methodology/SKILL.md).
- **Data pipeline operations, schema migration engineering, or ETL/ELT design.** Route
  to [data-engineering](../data-engineering/SKILL.md).
- **Test strategy, regression planning, and quality gates.** Route to
  [qa-methodology](../qa-methodology/SKILL.md).
- **Platform infrastructure provisioning or IDP design.** Route to
  [platform-engineering](../platform-engineering/SKILL.md).
- **Implementation planning, work breakdown, or delivery coordination.** Route to
  [implementation-planning](../implementation-planning/SKILL.md).
- **Spec authoring and SDD gate mechanics.** Route to
  [spec-driven-development](../spec-driven-development/SKILL.md).
- **Verification verdicts against explicit criteria.** Route to
  [verification-methodology](../verification-methodology/SKILL.md).
- **API contract design and versioning policy.** Route to
  [api-design-and-evolution](../api-design-and-evolution/SKILL.md).
- **Statistical analysis, experimental design, or causal inference.** Route to
  [data-scientist](../data-scientist/SKILL.md).
- **End-to-end production lifecycle orchestration across all readiness dimensions.**
  Route to the production-excellence bundle (prose reference only — not yet landed).
  Production-excellence composes production-readiness, migration-engineering,
  resilience-and-recovery, capacity-and-cost-engineering, and incident-learning into
  a full production-operations lifecycle.

## Risk classes and evidence scaling

The readiness evidence packet scales by risk class. A low-risk documentation release
must not demand the same evidence as a user-facing service launch.

| Risk class | Trigger conditions | Required evidence categories | Review depth |
|---|---|---|---|
| **Low** | Docs-only change, README update, non-functional config comment, internal tool that affects ≤1 team, content-only website change with no backend | Ownership, user/business outcome (1-line statement), rollback (revert a commit) | Self-review; lightweight record |
| **Standard** | User-facing feature, internal service with >1 consumer team, API addition, data-schema additive change, performance improvement with no SLO change | All 11 categories (see checklist below); missing evidence requires explicit gap annotation with owner and date | Peer review; full readiness record |
| **High** | Customer-facing service launch, SLO-bearing change, auth/authz change, data migration with irreversibility, payment/billing path, compliance-scoped change, trust-boundary crossing | All 11 categories with evidence from a named source for every category; every gap requires a waiver with human approver | Formal review; exception requires human approval annotation distinct from automated checks |

Risk class is determined by the **highest-risk dimension** present, not by averaging or
scoring. If any single dimension (e.g. data migration irreversibility, trust-boundary
crossing) qualifies as High, the entire review is High.

## Production evidence checklist

The 11 evidence categories form the minimum production evidence packet. Every category
must have either a named source artifact or an explicit missing-evidence outcome.

| # | Evidence category | Source / evidence | Gap / missing |
|---|---|---|---|
| 1 | **Ownership** | `source:` team name, on-call rotation, escalation path, or service catalog entry | `missing:` "no owner identified — deferred to <name>, due <date>" |
| 2 | **User/business outcome** | `source:` success metric, OKR link, or product brief with measurable target | `missing:` "outcome not defined — deferred to product owner, due <date>" |
| 3 | **Dependencies** | `source:` dependency map, health-check results, or upstream SLO status | `missing:` "dependency map incomplete — deferred to <name>, due <date>" |
| 4 | **SLOs** | `source:` SLO declaration, error-budget policy, or SLO dashboard link | `missing:` "SLOs not declared — deferred to SRE, due <date>" |
| 5 | **Observability** | `source:` dashboard link, alert rules, log/monitoring coverage, or Golden Signals report | `missing:` "observability gap — deferred to <name>, due <date>" |
| 6 | **Support** | `source:` runbook, support playbook, escalation matrix, or support-handoff document | `missing:` "no runbook — deferred to <name>, due <date>" |
| 7 | **Security** | `source:` security review record, threat-model summary, or security-acceptance sign-off | `missing:` "security review not completed — deferred to security team, due <date>" |
| 8 | **Data** | `source:` data-classification record, retention/deletion policy, backup/restore test evidence, or migration test result | `missing:` "data classification not available — deferred to data owner, due <date>" |
| 9 | **Rollback** | `source:` rollback runbook with rehearsal log, or revert-plan with recovery-time estimate | `missing:` "no rollback plan — deferred to <name>, due <date>" |
| 10 | **Capacity** | `source:` capacity model, load-test report, quota/limit review, or cost projection | `missing:` "capacity model not built — deferred to <name>, due <date>" |
| 11 | **Cost** | `source:` cost estimate, budget approval, or cost-attribution record | `missing:` "cost estimate not available — deferred to finance owner, due <date>" |

## Structured fields (mandatory)

These four categories must appear as structured fields (checklist markers,
table rows, or labeled form fields) — never only narrative prose.

- [ ] **Ownership** — named owner or owning team with escalation path; recorded in the evidence checklist above.
- [ ] **Rollback** — rollback plan or recovery path with rehearsal evidence; recorded in the evidence checklist above.
- [ ] **Support** — runbook, support playbook, or handoff document; recorded in the evidence checklist above.
- [ ] **Observability** — dashboards, alert rules, monitoring coverage; recorded in the evidence checklist above.

## Launch decision outcomes

Every readiness review produces exactly one of four outcomes. The accountable owner is
recorded with the decision.

| Outcome | Meaning | Required evidence | Accountable owner |
|---|---|---|---|
| **Go** | Approved — proceed to launch | All evidence categories for the risk class are satisfied with named sources; no unresolved gaps | Named launch approver (e.g., service owner, launch-review chair) |
| **No-go** | Blocked — do not launch | At least one blocking gap exists with a named missing-evidence entry; the gap is material to the risk class | Named launch approver |
| **Defer** | Postponed — re-review after conditions are met | Deferred gaps are recorded with owner and due date; the deferral reason is explicit | Named launch approver + gap owners |
| **Exception** | Approved with waiver — launch despite unresolved gap | The specific gap is named; a named human approver explicitly grants the exception; the exception annotation is distinct from automated checks and cannot be self-granted | Named human approver (distinct from the automated review) |

The exception outcome requires an **explicit human-approval annotation** — a named
individual who approves the waiver. This approval is distinct from any automated
check result and must be recorded separately (e.g., in an escalation record or
exception log). The exception cannot be self-granted by the submitter.

## Workflow

1. **Determine risk class.** Map the change against the trigger-condition table above.
   Select Low, Standard, or High.
2. **Collect evidence.** For each of the 11 categories, record a named source or a
   gap with owner and due date. Use the readiness record template.
3. **Assess completeness.** Check that every category has an entry. A category with
   a gap annotation is complete for the purpose of the review — the gap is visible.
4. **Produce a launch decision.** Map the evidence against the risk-class requirements
   and produce one of: Go, No-go, Defer, Exception.
5. **Record the decision.** Commit the readiness record with the accountable owner
   and, for exceptions, the explicit human-approval annotation.

## No universal risk score

This skill does not produce a universal risk score, aggregate risk rating, or total
risk number. Each evidence dimension stands on its own and is assessed against the
risk-class requirements individually. If individual dimensions are evaluated
separately (e.g., a security dimension assessment or a data dimension assessment),
the rationale for any weighting is stated explicitly in that dimension's evidence
entry — there is no single number that summarizes readiness.

## File map

| Path | Loaded when |
|---|---|
| [references/discovery-brief.md](references/discovery-brief.md) | Understanding the ownership boundaries with sibling production and engineering skills |
| [references/readiness-record.md](references/readiness-record.md) | Filling a readiness record template or reviewing a submitted record |

## Route-to table

| When the need is... | Route to |
|---|---|
| Release promotion, canary stages, CI/CD gates, versioning | [release-engineering](../release-engineering/SKILL.md) |
| Live-service SLOs, incident response, on-call, error budgets | [site-reliability-engineering](../site-reliability-engineering/SKILL.md) |
| Security requirements, threat modeling, secure defaults | [secure-software-engineering](../secure-software-engineering/SKILL.md) |
| Data pipelines, schema migration, ETL/ELT | [data-engineering](../data-engineering/SKILL.md) |
| Test strategy, regression planning, quality gates | [qa-methodology](../qa-methodology/SKILL.md) |
| Platform infrastructure, IDP, service networking | [platform-engineering](../platform-engineering/SKILL.md) |
| Work breakdown, dependency mapping, rollout sequencing | [implementation-planning](../implementation-planning/SKILL.md) |
| Spec authoring, acceptance criteria, SDD phase gates | [spec-driven-development](../spec-driven-development/SKILL.md) |
| Verification verdicts against explicit criteria | [verification-methodology](../verification-methodology/SKILL.md) |
| API contract design and versioning | [api-design-and-evolution](../api-design-and-evolution/SKILL.md) |
| Statistical analysis, experimental design | [data-scientist](../data-scientist/SKILL.md) |
| Full production-operations lifecycle | production-excellence bundle (prose reference — routes to a future bundle composing production-readiness, migration-engineering, resilience-and-recovery, capacity-and-cost-engineering, and incident-learning) |
