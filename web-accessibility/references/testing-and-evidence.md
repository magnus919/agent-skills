# Hybrid Testing and Evidence

Automated tools execute specific rules in a particular DOM, browser, and configuration. Record the tool, version, rule set, URL/state, and result. Treat findings as bounded evidence, not a semantic proof or an accessibility/WCAG verdict.

## What Automation Can And Cannot Establish

| Automated evidence can often detect | It usually cannot decide reliably |
|---|---|
| Missing or empty required attributes, invalid role/state combinations, some unnamed controls, some label relationships, some contrast failures, duplicate identifiers, and detectable DOM rule violations | Whether alternative text conveys purpose, headings and focus order make sense, a custom widget follows its full keyboard contract, status timing is understandable, errors are recoverable, target exceptions apply, screen-reader output is useful, or a disabled person can complete the task |

Investigate every finding in context. Also inspect sampled passes: a rule can pass because it did not apply, did not reach a state, or could not determine the human judgment.

## Manual Protocol

1. Establish the supported browser, operating system, AT, input, viewport, language, and feature state. Use audience/support evidence rather than a universal matrix.
2. Complete the primary task and its failure/recovery paths with keyboard alone, including reverse navigation. Record focus order, visibility, obscuring, traps, cancellation, restoration, and unexpected context changes.
3. Inspect the browser accessibility tree in every material state. Record role, name, description, state, value, relationships, hidden/inert exposure, and live updates.
4. With each selected screen-reader/browser combination, navigate by page structure, controls, and ordinary reading; enter and leave interaction modes as that AT requires; complete the task, trigger errors, recover, and verify changed states. Record actual speech/braille output where it matters.
5. Test pointer and touch alternatives, drag replacement, target spacing, zoom/reflow, text spacing, contrast, reduced motion, media controls, responsive states, and platform settings relevant to the feature.
6. Re-run automated checks in open/closed, valid/invalid, enabled/disabled, selected/unselected, loading/complete, and responsive states they otherwise miss.

## Evidence Set

| Method | What to record |
|---|---|
| Deterministic/static checks | Exact tool, version, rules, scope, state, findings, and acknowledged blind spots. |
| Keyboard tasks | Forward/reverse navigation, visible focus, order, traps, Escape, state changes, and recovery. |
| Accessibility tree | Browser/version and observed role, name, state, value, and relationships for each key state. |
| Screen reader | Actual browser/AT/version combinations selected from audience/support data; tasks, results, and defects. |
| Adaptive UI | Zoom/reflow, text spacing, contrast, motion, target, pointer, responsive, and drag-alternative checks. |
| User research | Participant/task findings when product risk, audience, or novelty makes it warranted. |

## Release Rule

For each acceptance criterion, mark pass, fail, blocked, or not applicable and link evidence. A passing automated scan alone cannot produce a pass verdict for accessibility. Report untested combinations and residual risk plainly.
