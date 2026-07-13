# Web Accessibility

Build web interfaces people can operate, understand, and recover from across keyboard, pointer, zoom, motion, and assistive technologies.

## Why Install This Skill

Visually polished interfaces can still strand people in a modal, hide focus behind sticky UI, make errors impossible to fix, or announce the wrong thing to a screen reader. This skill helps turn a feature's user flow into explicit accessibility requirements before code is written.

It gives your agent a framework-neutral way to choose native controls, define custom-widget contracts only when needed, and collect evidence from automated checks and real manual tasks. It treats passing a scanner as useful but limited evidence, not a promise of accessibility or WCAG conformance.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Workflow, decision rules, routing, and reference guide. |
| `references/source-index.md` | Primary sources with status, version, URL, and decision use. |
| `references/` | Focused guidance for semantics, focus, forms, widgets, adaptive UI, testing, routing, and outcome probes. |
| `assets/` | Reusable acceptance-criteria, design-review, implementation-review, and release-evidence templates. |

## Quick Start

Ask your agent to turn a feature flow into accessibility acceptance criteria before implementation. For example:

```text
Design an accessible profile editor modal. Define keyboard, focus, form recovery,
and browser/AT verification requirements before writing code.
```

No API key, package, or framework is required.

## Triggers

- Accessibility, a11y, WCAG, ARIA, accessible name, screen reader, or assistive technology.
- Keyboard navigation, focus order, focus trap, focus restoration, dialog, modal, disclosure, or responsive navigation.
- Form labels, validation, errors, accessible authentication, live regions, or recovery.
- Comboboxes, tabs, listboxes, menus, grids, target size, drag alternatives, zoom, reflow, contrast, or reduced motion.
- Accessibility testing, axe, manual testing, accessibility review, or release evidence.

## Requirements

- Access to the interface and its supported browser/AT environment for meaningful verification.
- Optional automated testing tools may provide bounded rule-level evidence; manual keyboard, accessibility-tree, and selected screen-reader testing remain required for interaction risk.
