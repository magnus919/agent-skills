# C4 Diagram Communication Review

Use this reference after the C4 level and model scope are chosen, and before calling a diagram complete. It improves the communication artifact without changing C4 ownership.

## 1. Audience and job

Write one sentence for the primary reader and the decision or task the view supports. For example: "A new maintainer needs to locate the system boundary and its external dependencies before changing the import path." If different readers need different jobs, produce separate views or a short sequence rather than one overloaded diagram.

## 2. Abstraction and representation

- Keep every element at the selected C4 level unless a deliberate reference to an adjacent level is labeled and explained.
- Use one vocabulary for people, systems, containers, components, code, stores, and relationships; do not make shape or color carry an undocumented category.
- Keep boundaries meaningful: a boundary should represent a real ownership or modeling scope, not a decorative grouping.
- Make relationship direction, interaction purpose, and technology detail comparable across the view. Do not label one edge with a protocol while labeling another with an unresolved business claim.
- Preserve the same element identity and naming across related C4 views. If a view omits an element, state that it is out of scope rather than implying it does not exist.

## 3. Narrative and visual hierarchy

Give the reader an entry point and an intended read order. Use title, short purpose statement, boundary order, spatial grouping, and relationship emphasis to lead from context to the claim that matters. Keep the primary path visually dominant; demote supporting paths and move implementation detail to a deeper view. A legend explains notation, not the story, so do not use it as a substitute for a caption.

Reduce signal loss by removing relationships that do not support the stated job, splitting dense views, shortening labels, and moving rationale to an ADR or accompanying prose. More nodes and edges are not evidence of completeness.

## 4. Labels, legend, and uncertainty

Use names that a reader can recognize without decoding internal abbreviations. Label relationships with the interaction or dependency the reader needs to understand. Add a legend only for non-obvious shapes, line styles, or categories, and keep it consistent with the diagram. Mark inferred, proposed, stale, or unknown elements and relationships in text or a documented line style; never imply certainty through polished layout.

## 5. Accessibility and review evidence

Meaning must survive grayscale, color-vision differences, zoom, small screens, and a text-only reading path. Pair color with labels, shapes, line styles, or explicit annotations. Provide a concise textual summary or table that names boundaries, elements, relationships, reading order, and uncertainty. Route full WCAG/ARIA and assistive-technology evaluation to `web-accessibility`.

Capture review evidence: audience/job, selected C4 level, source/model validation, rendered-tool and version, viewport or output surface, accessibility fallback, uncertainty register, reviewer, date, and concrete findings or accepted exceptions. Review the rendered result, not only the DSL or Mermaid source. A valid model and valid syntax are necessary but insufficient; a diagram can pass both and still fail its communication job.
