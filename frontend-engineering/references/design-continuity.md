# Preserve Design Decisions in Implementation

Read when implementing an approved design, extending an existing interface, or
repairing visual drift in AI-generated frontend work.

## Discover before generating

Inspect the current component inventory, tokens, style guide, approved flow/mockup
revision, and relevant decision records. Map requirements to existing components
before inventing new ones. A matching-looking component is not necessarily a matching
behavioral contract; verify states, semantics and interactions.

Do not ask the user to respecify settled decisions. Ask about missing behavior or a
real conflict: 'The approved flow permits skipping, but this component requires a
value. Should this step be optional?' Route new product behavior to
`product-design-and-ux` and a new visual identity to `brand-designer`.

## Implement incrementally

Use an editable prototype, component story, or narrow vertical slice to expose
uncertain details before expanding a large page set. Keep approved structure fixed
while resolving the named problem. Reuse canonical components, tokens and styles;
record justified exceptions locally rather than creating one-off copies or quietly
rewriting the shared system. A visual reference is not authority to add dependencies,
upload assets, or change unrelated screens.

If trying another model or tool, keep the same scoped brief, reference revision,
representative content and acceptance checks. Compare actual outputs, including
review/rework time and relevant states. Do not promise that a cheaper/local model
will reproduce a reference faithfully or save money without measured evidence.
Tool choice does not replace an inspectable design contract.

## Check rendered behavior against the approved baseline

Compare the implementation at relevant widths and with realistic content density,
including long text/localization where applicable. Exercise loading, empty, error,
focus, keyboard and recovery states implicated by the flow. Review hierarchy,
spacing, typography, consistency, and actual task completion separately. A screenshot
match is not accessibility or functional proof. Use `web-accessibility` for depth
and `qa-methodology` for test strategy; use `playwright` for browser test operation.

When a prototype cannot be reproduced as specified, explain the constraint and show
a bounded alternative; do not silently substitute a visually convenient behavior.
Record mismatches, fixes and untested limits rather than claiming a visual pass from
code inspection alone.

## Leave reusable evidence

Update the existing component documentation or small local decision artifact with
its canonical implementation, supported states, tokens, reference revision and
verified behavior. Preserve the approved scope; don't infer global approval from a
single accepted screen. Mark superseded guidance so the next task cannot accidentally
reintroduce it. Finish with the actual rendered/test evidence and remaining gaps.

Example: a second dashboard reuses the approved table and filter controls. Add the
new columns and empty-state copy, test long values and keyboard sorting, and ask only
about the new sorting semantics. Do not regenerate the theme or fork the table merely
because a fresh prompt produces a different aesthetic.
