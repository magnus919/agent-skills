# Forms, Errors, and Authentication

Use a native `<form>` and semantic input types where they fit. Give each control a visible label, explain constraints before submission when useful, group related controls with `fieldset` and `legend`, and preserve entered values after recoverable errors.

## Error Recovery

- Identify errors in text and visually without color alone; make them specific enough to correct. Explain required formats and constraints before they cause avoidable failures.
- Associate error and help text with the relevant field when that relationship helps. Set `aria-invalid` when a field is invalid; do not mechanically duplicate native `required` with `aria-required`.
- Decide whether to use native validation, custom validation, or both for the product and environment. Do not universally add `novalidate`.
- Choose an error summary, focus movement, and announcement behavior for the flow, then test with keyboard and target AT. `aria-errormessage` and assertive live regions are optional tools, not defaults. If focus moves to a summary, its links or references must lead to the affected controls.
- Preserve valid and recoverable entries. Give destructive or consequential submissions review, confirmation, correction, or reversal appropriate to the risk.
- Expose successful submission or saved status without interrupting unrelated work.

## Input Purpose, Repetition, And Help

Use native input types and autocomplete tokens when they accurately identify common user data. Keep help mechanisms in a consistent relative order when WCAG 3.2.6 applies. Within the same process, reuse or offer previously entered information when WCAG 3.3.7 applies, while respecting its security, essential-purpose, and stale-information exceptions.

## Authentication

WCAG 2.2 SC 3.3.8 is Accessible Authentication (Minimum), AA; SC 3.3.7 is Redundant Entry, A. Support password managers and paste. Read the criterion for alternatives and exceptions before evaluating CAPTCHA, biometrics, or cognitive-function tests; do not make categorical claims beyond its text.

## Evidence Questions

Can a keyboard and screen-reader user find instructions, submit, understand every error, correct it without re-entering recoverable data, and perceive success? Record the actual tested behavior rather than assumed ARIA output.
