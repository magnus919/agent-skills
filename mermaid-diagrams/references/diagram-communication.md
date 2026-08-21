# Mermaid Diagram Communication Review

Use this reference after selecting the Mermaid diagram type and before delivery. It supplements syntax and rendering checks with a review of the artifact's human job.

## Audience, job, and narrative

Write the primary audience, the question they need answered, and the target surface: README, issue, wiki, PDF, mobile screen, or another renderer. Put a short purpose statement before the diagram. Arrange nodes and edges so the intended entry point and read order are apparent; use direction, grouping, captions, and a dominant path intentionally. If two audiences need different levels of detail, split the diagram rather than making one canvas serve both.

## Consistent representation

- Use one abstraction level and one meaning for each shape, line style, arrow direction, and boundary.
- Keep labels parallel: comparable nodes should expose comparable facts, and comparable edges should describe comparable relationships.
- Use subgraphs for real scopes or meaningful groups, not as decoration. Keep related views consistent in names and boundaries.
- Treat layout configuration as communication design. Split dense diagrams, shorten labels with deliberate line breaks, and tune spacing only after removing unnecessary signal.
- Add a legend for non-obvious notation, and make it agree with the actual diagram. A legend cannot repair a missing narrative.

## Signal, uncertainty, and color

Prefer the smallest diagram that answers the stated question. Remove nodes and edges that do not support it, or move them to a linked detail view. Mark proposed, inferred, stale, or unknown relationships in text, labels, or documented line styles. Never let a polished render imply evidence that the source does not have. Pair color with text, shape, line style, or position so meaning remains available in grayscale and for readers with color-vision differences.

## Accessibility and review evidence

Provide a text-only summary or table that names the entry point, nodes, boundaries, relationships, read order, and uncertainty. Use readable labels, sufficient contrast, scalable output, and a target-surface check; do not rely on emoji or color as the only identifier. Route complete WCAG/ARIA and assistive-technology conformance work to `web-accessibility`.

Record the audience/job, diagram type, renderer and version, target surface and viewport, source validation result, rendered review result, text fallback, uncertainty notes, reviewer, date, and concrete findings or accepted exceptions. Review the rendered output at the size readers will encounter. Mermaid syntax and rendering can both pass while the communication artifact still fails its job.
