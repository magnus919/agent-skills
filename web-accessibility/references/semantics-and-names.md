# Semantics, Names, and Dynamic Updates

Start with HTML that represents the content and action: headings for headings, lists for lists, links for navigation, buttons for actions, and native inputs with labels. Native controls reduce interaction code, but test their actual browser/AT behavior in the supported environment.

## Structure And Names

- Use meaningful heading hierarchy and landmarks to expose page structure. Provide a bypass mechanism where repeated blocks create real keyboard burden. Use headings for sections, not merely for visual sizing, and keep the DOM reading order meaningful when CSS is removed.
- Mark data tables as tables, provide a useful caption when it helps identify purpose, and associate header cells with data cells. `scope` is usually sufficient for simple row or column headers; simplify complex tables or verify any `headers`/`id` mapping. Do not expose layout tables as data tables.
- Give every interactive control a visible, understandable label where practical. Associate `<label for>` with form controls; name icon-only controls with visible text or a carefully chosen accessible label. A placeholder or tooltip is not a durable replacement for a label.
- Decorative images use `alt=""`; informative images need an equivalent purpose or information. Describe a linked image by the destination/action. Complex graphics need the meaningful data or explanation nearby, not a filename-shaped alt string.
- Keep visible label text in the accessible name when speech input may use it. Do not add redundant ARIA to native elements or override a useful native role.
- Names and descriptions are different. Prefer native labeling and visible instructions. For difficult cases, use the full [AccName 1.2 algorithm](https://www.w3.org/TR/accname-1.2/) and inspect the browser accessibility tree rather than following a shortcut. Verify references resolve, names are not empty, and hidden or generated content contributes only as intended.

## Dynamic Updates

Move focus only when it helps the next task. Otherwise, use a pre-existing, appropriately polite status mechanism and verify what target screen readers announce. Avoid interrupting people with assertive announcements by default. For a single-page route change, update title, main content, route state, and focus according to the task; do not force a universal focus target.

## Review Questions

1. Can a user identify each region, control, purpose, and current state without visual inference?
2. Does the computed accessibility tree expose the intended role, name, state, value, and relationships?
3. Is a dynamic change perceivable without stealing context or relying on color alone?
