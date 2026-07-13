# Keyboard, Focus, and Route Changes

Keyboard behavior is a user-flow contract, not a `keydown` handler. Document how focus enters, operates within, exits, and recovers from every interactive state.

## Baseline

- Preserve logical DOM order; avoid positive `tabindex`. Make all functionality available without a pointer.
- Ensure a visible focus indicator with sufficient contrast, including after themes, zoom, and sticky overlays are active.
- Test forward and reverse navigation. Verify that focus is not obscured by sticky headers, footers, drawers, or virtual keyboard behavior. WCAG 2.4.11 is AA; 2.4.12 and 2.4.13 are AAA.
- A focus trap is appropriate only for an actual modal. It needs a usable exit and logical restoration, not just cycling Tab.

## Route And State Changes

Before changing focus, answer: what changed, where can the user continue, and will the move lose work or context? For routes, preserve browser history behavior, expose the new page purpose, and test back/forward, validation failures, and deep links. Choose a main heading, main region, status, or retained control only when the flow supports it.

## Manual Protocol

Complete each task with keyboard alone: Tab, Shift+Tab, Enter, Space, Escape, and pattern-specific arrows/Home/End where applicable. Record order, visible focus, unexpected traps, restoration, and recovery from each failure state.
