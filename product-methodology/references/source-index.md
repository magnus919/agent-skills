# Source Index — product-methodology

Provenance, portability boundary, and source review for the `product-methodology` skill.

## Source of Truth

This skill was ported from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555), path `skills/product-methodology/`.

## Portability Boundary

The source skill was Hermes-specific. The following transformations were applied:

| Source element | Destination | Change |
|---|---|---|
| `SKILL.md` (Hermes-specific: artifact pyramid output, `skill_view()` calls, Kanban references) | Rewritten as thin progressive-disclosure index | Removed all Hermes-specific instructions; rewrote as portable reference table |
| `references/artifact-pyramid-mapping.md` | Removed | Hermes-specific output format — not portable |
| `references/customer-interview-guide.md` | Removed | Belongs to `product-discovery` skill, not product-methodology |
| `references/rice-framework.md` | Kept | Added attribution to Intercom; content is portable methodology |
| `references/moscow-prioritization.md` | Kept | Added attribution to Dai Clegg; content is portable methodology |
| `references/opportunity-solution-trees.md` | Kept | Added attribution to Teresa Torres; content is portable methodology |
| `references/decision-log.md` | Kept | Content is synthesized practice — no changes needed |
| `references/spec-template.md` | Kept | Content is synthesized practice — no changes needed |
| `references/stakeholder-communication.md` | Kept | Content is synthesized practice — no changes needed |
| (new) `references/source-index.md` | Created | This file |
| `templates/DECISION_LOG.md` | Extracted from `references/decision-log.md` | Fillable template with YAML frontmatter |
| `templates/SPEC.md` | Extracted from `references/spec-template.md` | Fillable template with YAML frontmatter |

## Framework Provenance

| Framework | Origin | Authoritative Source | Licensing |
|---|---|---|---|
| RICE | Intercom (Sean McBride, 2016) | [intercom.com/blog/rice-simple-prioritization-for-product-managers](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/) | Freely available blog content; methodology not copyrightable. References are in original language. |
| MoSCoW | Dai Clegg, Oracle UK (1994) | [Wikipedia: MoSCoW method](https://en.wikipedia.org/wiki/MoSCoW_method) | Public methodology standard; no restrictive licensing. |
| Opportunity Solution Trees | Teresa Torres (Product Talk) | [producttalk.org/opportunity-solution-tree](https://www.producttalk.org/opportunity-solution-tree/) | Freely available blog content; methodology not copyrightable. Book (*Continuous Discovery Habits*, 2020) is copyrighted but not reproduced here. |
| Decision log | Synthesized from ADR practice | [ADR pattern (Michael Nygard, 2011)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Common practice — no single copyright holder. |
| Spec template | Synthesized from PRD conventions | — | Common practice — no single copyright holder. |
| Stakeholder communication | Synthesized from PM communication practice | — | Common practice — no single copyright holder. |

## Review Date

Source review completed July 2026. Framework URLs verified live.

## Boundary with Adjacent Skills

| Skill | Relationship | Status |
|---|---|---|
| `product-discovery` | Upstream — feeds validated evidence into methodology | Ships in this catalog |
| `product-design-and-ux` | Downstream — consumes specs from methodology | Proposed (issue #24); not yet shipped in this catalog |
