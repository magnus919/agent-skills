# Dialogs, Disclosures, and Navigation

## Modal Dialogs

Prefer `<dialog>` with `showModal()` when it is supported by the target environment; otherwise implement the equivalent behavior deliberately and test it. A modal needs an accessible name, a visible close path, focus inside while open, unavailable/inert background content, and logical focus restoration.

For native `<dialog>`, use its modal API rather than merely toggling `open`; define intentional initial focus, closing, cancellation, and return behavior, then verify the supported browser/AT implementations. For a custom modal, supply `dialog` semantics, set `aria-modal="true"` only when the UI is genuinely modal for every user, contain Tab and Shift+Tab, and make the rest of the application unavailable without hiding the dialog.

Choose initial focus from content structure, viewport, reversibility, and the likely task. It is not always the first control. Return focus to the invoker unless it no longer exists or the workflow makes another target more appropriate. `aria-describedby` is optional and may make rich structural content harder to consume. Close requests, Escape, and light dismiss depend on the adopted pattern and product intent; define and test them. Do not put `aria-hidden` on a backdrop and never hide an ancestor containing the dialog.

## Disclosures And Navigation

Use a native `button` to control a disclosure and synchronize `aria-expanded`; connect it to the controlled region when useful. Responsive site navigation normally remains ordinary links within a navigation landmark. It is not an ARIA menu by default. Provide visible focus, logical open/close behavior, `aria-current="page"` for the current page, and target-size review including WCAG exceptions.

Use `menu`/`menuitem` roles only for application-style menus and implement their full keyboard/focus contract. Outside-click dismissal is a product choice, not a universal requirement.
