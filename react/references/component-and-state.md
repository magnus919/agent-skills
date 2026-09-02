# React Component And State Patterns

## Start with ownership

Describe each value as one of local UI state, server/cache state, URL state, or
cross-cutting application state. Keep state at the lowest common owner. If a
value is derived from other values, compute it during render or in a memoized
calculation when measurement proves the calculation costly; do not create a
second source of truth.

A practical component boundary usually owns one interaction or visual contract.
Split when a component has unrelated state machines, repeated markup, or an
API that requires consumers to understand implementation details. Keep domain
transformations outside presentational components when they can be tested
without a browser.

## Effects and asynchronous work

Before adding `useEffect`, name the external system it synchronizes with:
network, subscription, timer, browser API, or imperative widget. If none exists,
prefer render derivation or an event handler. Every effect should have a cleanup
when it creates a subscription, timer, listener, or request that can outlive the
render.

For a request keyed by an input, use an abort signal or an active-request guard,
handle abort as non-error cancellation, and ensure a late response cannot replace
newer data. Model `status` explicitly (`idle`, `pending`, `success`, `error`) and
render all meaningful states. Avoid catching an error only to log it and leave a
permanently pending screen.

## Interaction contracts

Use controlled inputs when validation, submission, or external reset is part of
the feature; otherwise an uncontrolled input with a ref may be simpler. Keep
submit handlers idempotent, disable or guard while pending, and preserve the
user's entered data on recoverable errors. Announce validation and server errors
through the accessible structure, not only a color or toast.

For lists, key rows with stable domain identity. If a row has local state, an
index key can transfer that state to another record after sorting or deletion.
Use functional updates for transitions based on prior state, especially when
multiple events may batch.

## Verification checklist

- Hooks are unconditional and dependencies reflect values read from the effect.
- No derived state or duplicated server state is introduced without a reason.
- Loading, empty, error, retry, and success states are represented where relevant.
- Async cleanup prevents stale writes and treats cancellation intentionally.
- Buttons and links use native semantics; keyboard and focus behavior is tested.
- Component tests cover user-visible behavior; browser flows are delegated to
  [playwright](../../playwright/SKILL.md).
- Dedicated semantic and WCAG review is delegated to
  [web-accessibility](../../web-accessibility/SKILL.md).
