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

| Framework | Origin | Primary source | Treatment |
|---|---|---|---|
| RICE | Intercom (Sean McBride, 2016) | [Intercom: RICE prioritization](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/) | Paraphrased with attribution; the source article's wording and examples are not reproduced. |
| MoSCoW | Dai Clegg, Oracle UK (1994); later adopted by DSDM | [Agile Business Consortium: MoSCoW prioritisation](https://www.agilebusiness.org/dsdm-project-framework/moscow-prioritisation.html) | Paraphrased with attribution; capacity guidance is presented as a planning heuristic, not a universal rule. |
| Opportunity Solution Trees | Teresa Torres (Product Talk) | [Product Talk: Opportunity Solution Trees](https://www.producttalk.org/opportunity-solution-tree/) | Paraphrased with attribution; proprietary diagrams and book text are not reproduced. |
| Decision log | Synthesized from ADR practice | [ADR pattern (Michael Nygard, 2011)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Original synthesis informed by the cited pattern. |
| Spec template | Synthesized from PRD conventions | — | Original synthesis from common product-documentation practice. |
| Stakeholder communication | Synthesized from PM communication practice | — | Original synthesis from common communication practice. |

## Review Date

Source review completed July 2026. Framework URLs verified live.

## Boundary with Adjacent Skills

| Skill | Relationship | Status |
|---|---|---|
| `product-discovery` | Upstream — feeds validated evidence into methodology | Ships in this catalog |
| `product-design-and-ux` | Downstream — turns approved scope and evidence into user-facing behavior and interaction handoff | Ships in this catalog |
