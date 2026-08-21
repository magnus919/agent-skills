---
name: enterprise-architecture
description: >-
  Design and evolve enterprise architectures by connecting business capabilities,
  value streams, applications, information, technology, operating models, and
  transition choices. Use when mapping an enterprise portfolio, comparing current
  and target states, sequencing transition architectures, or defining federated
  architecture decision rights and stakeholder communication. Do not use for
  system or solution design, API or data-platform design, organizational or talent
  design, product roadmaps, technology adoption, or corporate strategy; route
  those to the named specialist skills.
license: MIT
compatibility: Platform-agnostic methodology. No runtime dependencies.
metadata:
  tags: enterprise-architecture, capability-mapping, value-streams, application-portfolio, operating-model, decision-rights
---

# Enterprise Architecture

Use this skill to make enterprise-wide structure and change legible without turning
architecture into a shelf of diagrams. Connect outcomes to capabilities, value
streams, applications, information, technology, ownership, and a feasible sequence
of change.

## Workflow

1. **Frame the enterprise question.** State the outcome, scope, time horizon,
   stakeholders, constraints, authority, and evidence gaps. Separate strategy,
   product commitments, operational facts, and architectural hypotheses.
2. **Map the landscape.** Identify capabilities and value streams, then relate
   applications, information objects, technology dependencies, owners, costs,
   risks, duplication, and lifecycle status. Use
   `references/capability-value-stream-and-portfolio-mapping.md`.
3. **Describe states.** Record the current state from evidence, define a target
   state from explicit principles and outcomes, and identify constraints that make
   a direct jump unsafe or unrealistic. Use
   `references/current-target-and-transition-architecture.md`.
4. **Choose the operating model.** Compare centralized, federated, and hybrid
   arrangements against decision locality, coordination cost, required coherence,
   skills, and risk. Do not prescribe reporting lines or compensation. Use
   `references/enterprise-operating-model-and-roles.md`.
5. **Make authority executable.** Assign decision rights, consultation, standards,
   exceptions, escalation, and feedback to named roles. Use
   `references/federated-governance-and-decision-rights.md`.
6. **Engage and publish for use.** Adapt views to stakeholder jobs, make uncertainty
   and provenance visible, and maintain accessible, findable information with a
   review owner. Use `references/stakeholder-engagement-and-architecture-information.md`.
7. **Sequence change.** Connect transition increments to capabilities, outcomes,
   dependencies, investment assumptions, and exit evidence. Use
   `templates/transition-architecture-roadmap.md`; hand approved delivery plans to
   `implementation-planning` or `migration-engineering` as appropriate.

## Output Contract

Produce an enterprise context brief, capability/application portfolio view,
current-target-transition assessment, operating-model and decision-rights record,
or transition roadmap. Every material claim must be labeled as evidence,
assumption, decision, or open question and have a source or named owner.

## Ownership Boundaries

- System boundaries, runtime behavior, architecture characteristics, and solution
  tradeoffs belong to `software-architecture`.
- API contracts and API portfolio mechanics belong to `api-design-and-evolution`.
- Data platforms, data products, data models, and data governance belong to
  `data-architect`.
- Reporting structures, team topology, talent, compensation, and culture belong to
  `org-design`; this skill records organizational dependencies without designing HR
  systems.
- Product bets, product outcomes, and product sequencing belong to
  `product-roadmapping-and-portfolio`.
- Technology adoption posture, build-versus-buy, standards, and technology
  governance mechanics belong to `technology-radar`.
- Corporate direction, competitive choices, capital allocation, and M&A belong to
  `strategy-frameworks`.
- Process optimization and operational execution belong to `operational-design`;
  enterprise architecture may use its findings as evidence.
- Approved cross-system execution belongs to `implementation-planning` and
  `migration-engineering`, not this skill.

## When Not To Use

Use the narrow owner when the request has no enterprise portfolio, cross-domain
alignment, operating-model, or transition-architecture question. Do not use this
skill to produce a solution design, organization chart, product roadmap, technology
radar entry, data architecture, API contract, or corporate strategy verdict.

## Reference Guide

| Decision point | Load |
|---|---|
| Mapping capabilities, value streams, applications, information, or duplication | `references/capability-value-stream-and-portfolio-mapping.md` |
| Comparing current, target, and transition states | `references/current-target-and-transition-architecture.md` |
| Selecting an enterprise operating model and defining architecture roles | `references/enterprise-operating-model-and-roles.md` |
| Assigning decision rights, standards, exceptions, or escalation | `references/federated-governance-and-decision-rights.md` |
| Interviewing stakeholders or publishing usable architecture information | `references/stakeholder-engagement-and-architecture-information.md` |
| Establishing scope and evidence | `templates/enterprise-context-brief.md` |
| Creating a portfolio view | `templates/capability-portfolio-view.md` |
| Sequencing target-state change | `templates/transition-architecture-roadmap.md` |
| Checking provenance and transformation constraints | `references/source-index.md` |

## Completion

Stop when the enterprise scope and decision owner are explicit, the portfolio and
state claims have evidence or named gaps, transition increments have dependencies
and exit evidence, decision rights include conflict handling, and specialist
handoffs are recorded. Escalate unresolved authority or strategy conflicts rather
than resolving them by assumption.
