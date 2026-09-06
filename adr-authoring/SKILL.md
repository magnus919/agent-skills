---
name: adr-authoring
description: Write, review, and maintain architecture decision records with clear context, alternatives, consequences, confirmation links, and lifecycle governance. Use when a consequential technical decision or its enforceable architectural constraint must remain understandable. Do not use for system-wide evolutionary architecture design, general observability, or operating a named test or CI tool.
license: MIT
compatibility: No runtime dependency.
metadata:
  source_repo: https://github.com/magnus919/hermes-profiles
  source_commit: 867a555
---


# ADR Authoring

Architecture Decision Records for capturing design rationale. ADRs supply the temporal dimension — decisions over time — that structure-only views (C4) miss.

## Start with Repository Conventions

1. Read the repository's agent instructions, contributing guide, ADR index, template, and a few recent records before drafting. Reuse the established location, numbering, headings, status vocabulary, approval process, and amendment policy.
2. Treat this skill's layouts and templates as fallbacks only. Do not move, renumber, rename, or rewrite existing ADRs to fit the skill. If local conventions conflict, preserve the existing records and identify the specific conflict before changing the convention.
3. If no convention exists, use a flat `docs/adr/` directory, stable sequential identifiers, a small index, and a lightweight Nygard template (MADR when option analysis needs more structure). Read `references/project-setup-guide.md` only when establishing a new decision log.
4. Read `references/adr-to-pyramid-mapping.md` only if the project already uses artifact pyramids or the user requests that organization. Index links can provide layered navigation without relocating canonical records.

## Decision, Approval, and Evidence

Keep these three facts distinct, using the repository's existing fields or linked records:

- **Proposal:** What is recommended, why, alternatives, consequences, and unresolved questions. A draft or recommendation is not an accepted decision.
- **Decision authority and scope:** Who approved what, when, and for which environment or stage. Approval to experiment permits the bounded experiment; it does not establish production adoption. An accepted ADR may authorize only an experiment if that scope is explicit. Do not invent a decider, date, or broader approval.
- **Implementation evidence:** Links to changes, checks, observed results, and remaining gaps. Acceptance does not prove implementation; passing a prototype check does not prove production readiness. Label a validation plan as planned until results exist.

For example, “approved an isolated database trial” supports a trial-scoped decision. A successful restore rehearsal is evidence for the tested recovery scenario; neither fact alone means “database adopted in production.”

## ADR Lifecycle

Use the local lifecycle and amendment rules. When absent, use `proposed → accepted | rejected`, with accepted decisions later `deprecated` or `superseded` by a linked successor.

Preserve accepted rationale. By default, a changed decision gets a new ADR; update the old record's status and successor link while retaining its identifier and location. If the repository uses living documents, make dated, attributable amendments under its policy. Do not impose mutability on an immutable log or replace a living-document process with an immutable one.

Record rejection and supersession reasons, maintain the index, and preserve links. Review format and meeting length follow the team's process; acceptance requires evidence of the relevant decision authority, not a mandatory ceremony.

## Template Selection

Use the repository template first. This table applies only when no template is established.

| When | Template | Sections |
|------|----------|----------|
| Quick decision, single rationale | **Nygard** | Status, Context, Decision, Consequences |
| Multi-option trade-off analysis | **MADR** | Decision Drivers, Considered Options, Pros/Cons, Links |
| High-stakes, regulatory, compliance | **Tyree & Akerman** | 12 sections: Issue, Positions, Argument, Implications, etc. |
| Vendor/procurement decision | **Business Case** | Evaluation criteria, Cost/SWOT, Recommendations |
| QA/contract-driven environment | **Planguage** | Tag, Gist, Priority, Stakeholders, Risks |

Full catalog with section-by-section guidance in `references/adr-format.md`.

## File Naming Conventions

Follow local naming first. For a new log, use present tense imperative verb phrases, lowercase-dashes, `.md` extension:

```
001-choose-database.md
002-format-timestamps.md
003-manage-secrets.md
```

Status lives in the document header, not the filename — status changes shouldn't require renames.

## Teamwork & Governance

- **Who can create:** Any team member who has read the ADR process docs
- **What justifies:** Decisions affecting future "why", cross-team coordination, long-term maintainability, external interfaces
- **What usually does NOT:** Routine changes already covered by standards. Record a bounded experiment when its authorization, constraints, or consequences need durable rationale.
- **Roles per ADR:** Primary contact, secondary contact, accountable team
- **Amendments:** Follow repository policy; preserve decision history and distinguish new evidence from a changed decision.

See `references/adr-format.md` for the full governance model and teamwork questions.

## Fitness-Function Confirmation

**Applicability:** Use when an ADR makes a claim that can be checked through code, configuration, runtime telemetry, a scheduled audit, or a bounded human review.

Read `references/fitness-functions.md` to select the function's scope, cadence, evidence, threshold, owner, exception path, and retirement rule. Use `templates/fitness-function-record.md` for the operational record. Keep the ADR as the owner of the durable decision and its link to confirmation; keep implementation and execution in the project's test, CI, telemetry, or governance systems.

## Completion and Boundaries

Complete when the requested ADR or review follows local conventions, identifies decision scope and authority without invention, preserves history, and distinguishes observed evidence from planned checks. If acceptance is unresolved, deliver a proposed record and name the missing decision rather than claiming acceptance.

## When not to use

Route system-wide architecture and change sequencing to `software-architecture`, and named-tool implementation to the relevant operational skill. This skill owns decision rationale and confirmation links, not execution of the implementation or a general observability program.

## Contents

- `references/adr-format.md` — template catalog (11 formats: Nygard, MADR, Tyree & Akerman, Business Case, Planguage, Alexandrian, ITD, arc42, EdgeX, Gareth Morgan, NHS Wales), template selection decision tree, lifecycle stages, file naming, team governance, examples reference
- `references/adr-to-pyramid-mapping.md` — active→L2, superseded→L3, consumer routing
- `references/fitness-functions.md` — method for selecting, operating, interpreting, reviewing, and retiring checks that connect ADR claims to durable evidence
- `references/decision-sustainability.md` — 5 sustainability criteria + 8 guidelines for evaluating ADR quality before acceptance
- `references/project-setup-guide.md` — bootstrapping ADRs in a new project: directory setup, README index, CONTRIBUTING.md/AGENTS.md docs, issue-first PR workflow with worked example
- `templates/fitness-function-record.md` — reusable record for selecting, operating, reviewing, and retiring a fitness function
- `references/source-index.md` — provenance and synthesis boundary for this skill

## Canonical Reference

- Architecture Decision Record community repo — https://github.com/architecture-decision-record/architecture-decision-record
- Michael Nygard, "Documenting Architecture Decisions" — https://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions

## Portability

This skill is intentionally host-neutral. Use your agent's normal mechanisms to load the references, templates, and scripts listed here. Do not assume a particular profile system, task orchestrator, memory service, or response-handoff format.
