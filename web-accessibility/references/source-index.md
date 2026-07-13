# Primary Source Index

Use the source appropriate to the decision. Version/status matters: specifications define requirements or platform behavior, while APG and tutorials inform implementation and must be tested in the target environment.

| Source | Type and exact status/version | Canonical URL | Decision use |
|---|---|---|---|
| Web Content Accessibility Guidelines (WCAG) 2.2 | W3C Recommendation, 2023-10-05 | https://www.w3.org/TR/WCAG22/ | Success criteria, conformance scope, levels, and exceptions. |
| What's New in WCAG 2.2 | W3C WAI informative explainer, retrieved 2026-07-13 | https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ | Check the nine additions and removed 4.1.1 Parsing criterion. |
| WAI-ARIA 1.2 | W3C Recommendation, 2023-06-06 | https://www.w3.org/TR/wai-aria-1.2/ | Roles, states, properties, and native-host-language-first rule. |
| ARIA Authoring Practices Guide | W3C WAI informative guidance, retrieved 2026-07-13 | https://www.w3.org/WAI/ARIA/apg/ | Pattern contracts and examples; validate with audience-relevant browser/AT combinations. |
| Accessible Name and Description Computation 1.2 | W3C draft technical specification, retrieved 2026-07-13 | https://www.w3.org/TR/accname-1.2/ | Algorithmic name/description edge cases; verify document status before a standards claim and inspect computed results. |
| HTML Living Standard | WHATWG Living Standard, retrieved 2026-07-13 | https://html.spec.whatwg.org/multipage/ | Native HTML behavior for dialog, details/summary, forms, inert, focus, and controls. |
| WAI accessibility evaluation tools | W3C WAI informative guidance, retrieved 2026-07-13 | https://www.w3.org/WAI/test-evaluate/tools/ | Limits of tools and need for human evaluation. |
| WAI involving users | W3C WAI informative guidance, retrieved 2026-07-13 | https://www.w3.org/WAI/test-evaluate/involving-users/ | When disabled-user research is proportionate to risk and context. |

## WCAG 2.2 Changes To Apply

WCAG 2.2 adds nine success criteria:

- 2.4.11 Focus Not Obscured (Minimum), AA
- 2.4.12 Focus Not Obscured (Enhanced), AAA
- 2.4.13 Focus Appearance, AAA
- 2.5.7 Dragging Movements, AA
- 2.5.8 Target Size (Minimum), AA
- 3.2.6 Consistent Help, A
- 3.3.7 Redundant Entry, A
- 3.3.8 Accessible Authentication (Minimum), AA
- 3.3.9 Accessible Authentication (Enhanced), AAA

It removes obsolete 4.1.1 Parsing.

Read the criterion before applying it: do not rely on abbreviated lists for exceptions, applicability, or a conformance claim.
