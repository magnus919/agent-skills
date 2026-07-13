# Routing

Keep the semantic and interaction contract framework-agnostic first. Then use the current official documentation for the chosen framework or component library to implement it; do not assume a universal framework or library.

| Situation | Route |
|---|---|
| Hugo template architecture, theme-wide layout, or CMS rendering | [hugo-theme](../../hugo-theme/SKILL.md) and its [design/accessibility reference](../../hugo-theme/references/design-accessibility.md) |
| Stakeholder evidence and validation | [product-discovery](../../product-discovery/SKILL.md) |
| Product scope, priority, or rationale | [product-methodology](../../product-methodology/SKILL.md) |
| User-facing behavior, task flows, state/recovery models, or engineering UX handoff | [product-design-and-ux](../../product-design-and-ux/SKILL.md); keep accessibility conformance depth here |
| Browser platform behavior | WHATWG HTML in `source-index.md` |
| ARIA roles/pattern contracts | WAI-ARIA 1.2 and APG in `source-index.md` |
| Framework-specific component API | Current official documentation after requirements are defined |

Do not route to a library merely because it advertises accessibility. Confirm its behavior against the user task and target browser/AT support.
