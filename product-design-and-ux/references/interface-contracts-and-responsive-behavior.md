# Interface Contracts and Inclusive Responsive Behavior

An interface contract describes observable behavior, not visual styling, component names, or framework APIs. It lets design, content, accessibility, engineering, testing, operations, and product review the same boundary without assuming the mockup contains all behavior.

## Contract Fields

For each surface or meaningful state, specify:

- linked outcome, task, evidence, role, and entry conditions;
- content, source, freshness, formatting responsibility, and fallback;
- controls and their purpose, visible label, accessible name/role/state expectation, and enabled/disabled/hidden rules;
- allowed actions, validation timing, error placement, correction path, and preservation of input;
- transition trigger, destination, focus or orientation outcome, persistence, and re-entry;
- permission checks at view and action boundaries, including changed or expired authority;
- side effects, commit boundary, retry/deduplication behavior, cancellation, undo, and completion evidence;
- telemetry purpose and minimum event fields, without default content capture;
- assumptions, unresolved decisions, owners, and resolution gates.

The contract should describe what a person can observe and do. Leave layout coordinates, CSS, component props, and internal service calls to implementation artifacts unless they are externally constrained.

## Responsive Behavior as Constraints

Do not reduce responsiveness to named device breakpoints. For each relevant constraint, record what remains available, what changes, and how context survives:

| Constraint | Contract questions |
|---|---|
| Available width and zoom/reflow | What can wrap, stack, scroll, collapse, or remain pinned without losing order, labels, comparison, or actions? |
| Text expansion and localization | Which containers grow, which labels cannot truncate, and what happens to tables, controls, errors, and status? |
| Orientation and viewport change | Is work preserved? Does focus or reading position remain logical? |
| Keyboard, pointer, touch, switch, and voice input | Is every action reachable with appropriate target, order, naming, and non-drag alternative? |
| Reduced motion or animation failure | Is meaning preserved without motion, and can movement be suppressed where required? |
| Degraded connectivity and delayed work | What becomes unavailable, queued, stale, partial, retryable, or cancellable? |
| Interruption and re-entry | What draft, filters, step, ownership, permission, and conflict information is restored or revalidated? |

Only include constraints relevant to the supported product context, but record why a high-risk constraint was ruled out. Fixed pixel values may be implementation evidence, not the reasoning model.

## Accessibility Boundary

Carry keyboard reachability, focus outcome, accessible name/role/state expectations, text alternatives, error recovery, reflow, motion, and input alternatives into the interaction contract. Route exact success-criterion applicability, native semantics, ARIA selection, browser/assistive-technology matrices, and conformance evidence to [web-accessibility](../../web-accessibility/SKILL.md).

An accessibility field is useful only when it is observable. Replace “accessible control” with the intended name, role, state/value, keyboard behavior, focus outcome, error behavior, and evidence path.

## Contract Review

Review one contract against its task/state model and data/permission boundary. Reject it when a transition has no recovery, a mutation lacks completion evidence, a role can see but not understand an unavailable action, content ownership is missing, telemetry has no purpose/minimization rule, or responsive behavior is deferred to “the frontend.” Use `templates/interface-contract.md` to capture the result.
