# Information Architecture

Information architecture (IA) makes objects, actions, relationships, and routes findable and understandable. Start with what people need to accomplish and locate, not with a preferred navigation control or the current database schema.

## Inventory Before Structure

Record:

- user goals and entry contexts;
- content or domain objects, their relationships, ownership, and lifecycle;
- language people use and conflicting internal terminology;
- roles, permissions, visibility boundaries, and cross-account or cross-tenant context;
- likely entry points from links, search, notifications, history, and other channels;
- frequency, urgency, risk, comparison needs, and interruption/re-entry;
- content volume, growth, freshness, archival, and deletion behavior.

Do not expose implementation nouns merely because they already exist. Do not flatten distinct user concepts because they share a table. Preserve a vocabulary conflict as an open decision until evidence resolves it.

## Derive and Test the Model

For each important object or action, answer:

| Question | Evidence to retain |
|---|---|
| Where can a person enter directly? | Entry-point inventory and required context |
| Where would they look first? | Research, domain language, support/search evidence, or explicit assumption |
| What label distinguishes it from neighbors? | Terminology evidence and rejected labels |
| What role or ownership changes visibility or action? | Permission matrix and empty/denied behavior |
| How do they move between overview, object, action, and history? | Navigation/search model and return path |
| How do they resume after interruption? | Stable identifier, preserved filters/context, and re-entry route |
| What happens when the object is missing, stale, archived, or moved? | Recovery, redirect, explanation, and support path |

Validate labels, grouping, hierarchy, navigation, and search assumptions with the smallest evidence capable of disproving them. Depending on uncertainty, that may be source review, content inventory, tree/path exercise, search-log analysis, or authorized task-based observation. Name the method and limitation; do not call an untested sitemap intuitive.

## Navigation and Disclosure Decisions

Choose navigation only after the object and task model is visible. Compare depth, breadth, orientation, backtracking, scanning, cross-linking, search dependence, permission-induced gaps, and context preservation. A sitemap, route map, or search schema documents the result; none substitutes for reasoning.

Progressive disclosure is a hypothesis. Reveal detail when it supports the next decision, but never hide information needed to assess consequence, cost, privacy, authorization, or irreversibility. Record what is hidden, the reveal trigger, how the trigger is discoverable, whether state persists, and how keyboard, touch, and assistive input reach it.

## Output Gate

Use `templates/outcomes-to-design.md` to connect goals and evidence to findability decisions, then carry entry points, labels, object context, and permissions into `templates/interface-contract.md`. IA is ready for flow design when every in-scope task has a plausible entry and return path, permission-driven absences are explained, and unresolved terminology has an owner and resolution gate.
