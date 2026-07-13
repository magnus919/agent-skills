# Outcome Probes

Use these probes to check whether a proposed design or implementation follows this skill. They are review prompts, not automated conformance tests.

## A. Modal Profile Editor

Verify an accessible dialog name, context-appropriate initial focus, inert/unavailable background, custom-modal Tab containment where relevant, visible close path, logical focus restoration, native form semantics/error recovery, and recorded browser/AT evidence. Reject backdrop `aria-hidden` and mandatory `aria-describedby` assumptions.

## B. Contact Form Recovery

Verify visible labels, native semantics, clear instructions, identified and associated errors, preserved values, context-tested summary/focus/announcement behavior, exposed success, and keyboard/screen-reader task completion. Reject universal `novalidate`, `aria-required`, `aria-errormessage`, or `role="alert"` requirements.

## C. Responsive Navigation

Verify a native button, state synchronized through `aria-expanded`, useful control relationship, ordinary navigation links, visible focus, logical close/focus behavior, current-page state, and 24 by 24 CSS-pixel target criterion with documented exceptions. Reject application-menu semantics by default.

## D. Custom Combobox

Require a documented role/state/keyboard/focus/name contract, accessibility-tree inspection, target browser/AT testing, and consideration of a proven native or maintained component before custom code.

## E. Release Verdict

Require bounded automated evidence, manual protocols, actual tested combinations, and recorded blocked/not-applicable criteria. Reject WCAG conformance or accessibility claims based on an automated scan alone.
