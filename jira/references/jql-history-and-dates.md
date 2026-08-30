# JQL History Predicates, Date Expressions & Saved Filters

Deep-dive on the three areas that trip up even experienced JQL writers: history operators (`WAS`, `CHANGED` and their predicates), relative-date expressions, and saved-filter composition. Pairs with [jql-functions-catalog.md](jql-functions-catalog.md), [jql-best-practices.md](jql-best-practices.md), and [jql-cookbook.md](jql-cookbook.md).

A JQL clause is a field followed by an operator followed by one or more values or functions (`project = "TEST"`); clauses join with keywords like `AND`/`OR`. Without parentheses a statement evaluates left-to-right, which is why parenthesizing OR groups matters.

## History Operators: the WAS Family

**Field restriction first:** `WAS`, `WAS IN`, `WAS NOT`, and `WAS NOT IN` work with **Assignee, Fix Version, Priority, Reporter, Resolution, and Status only**. On any other field they error out; custom-field history is simply not addressable through these operators.

### What WAS actually matches

`status WAS "In Progress"` finds issues that currently have OR previously had that value. Two subtle matching rules:

1. It matches the value name **as it was configured at the time of the change** — if your workflow renamed "In Progress" to "Active" last quarter, `status WAS "In Progress"` still finds historical states recorded under the old name.
2. It also matches the value's numeric ID — `status WAS "Resolved"` and `status WAS "4"` hit the same issues when 4 was Resolved's ID.

### Optional predicates

Every WAS-family operator accepts optional predicates:

| Predicate | Form | Meaning |
|-----------|------|---------|
| `AFTER` | `AFTER "date"` | change happened after the date |
| `BEFORE` | `BEFORE "date"` | change happened before the date |
| `BY` | `BY "user"` / `BY (user1,user2)` | user who made the change |
| `DURING` | `DURING ("date1","date2")` | change inside the window |
| `ON` | `ON "date"` | change on that exact date |

The `BY` user may be a username or an Atlassian account ID (`status WAS "Resolved" BY abcde-12345-fedcba BEFORE "2019/02/02"`). Dates use the standard JQL date format (`"2019/02/02"`) or any expression from the relative-date section below — `DURING (startOfYear(), endOfYear())` is valid.

### Walkthrough: build a "reopened bugs" query step by step

Goal: bugs that went backwards from Done back to In Progress.

```jql
-- Step 1: base form — did status ever hold "Done"?
issuetype = Bug AND status WAS Done

-- Step 2: add the transition direction with CHANGED (below):
issuetype = Bug AND status CHANGED FROM Done TO "In Progress"

-- Step 3: bound it to this year so the scan stays cheap:
issuetype = Bug AND status CHANGED FROM Done TO "In Progress" DURING (startOfYear(), endOfYear())
```

Each predicate composes: `priority CHANGED BY freddo BEFORE endOfWeek() AFTER startOfWeek()` chains two time bounds around a user bound.

### The other WAS operators

| Operator | Equivalent longhand | Example |
|----------|--------------------|---------|
| `WAS IN ("Resolved","Closed")` | `status WAS "Resolved" OR status WAS "Closed"` | `status WAS IN ("Resolved","In Progress")` |
| `WAS NOT "X"` | never held X | `status WAS NOT "In Progress" BEFORE "2011/02/02"` |
| `WAS NOT IN (...)` | `WAS NOT A AND WAS NOT B` | `status WAS NOT IN ("Resolved","In Progress")` |

### The 10,000-change truncation

If an issue has more than 10,000 changes, WAS-family queries search **only its most recent changes**. Ancient history on hyper-active issues is invisible to JQL — use the issue view or export for those. This is silent: you get results, just not complete ones.

## The CHANGED Operator

`CHANGED` finds issues whose field value *changed* (not what it changed to — that is what `FROM`/`TO` refine).

Predicates: everything WAS takes, **plus** `FROM "oldvalue"` and `TO "newvalue"`:

| Predicate | Purpose |
|-----------|---------|
| `FROM "oldvalue"` | previous value equals |
| `TO "newvalue"` | new value equals |
| `AFTER` / `BEFORE` / `DURING` / `ON` | time bounds |
| `BY "user"` | who performed the change |

Same six-field restriction applies (Assignee, Fix Version, Priority, Reporter, Resolution, Status).

Canonical patterns:

```jql
-- Any assignee change at all:
assignee CHANGED

-- Regression detector: went backwards from In Progress to Open:
status CHANGED FROM "In Progress" TO "Open"

-- Priority churn by one user this week:
priority CHANGED BY freddo AFTER startOfWeek() BEFORE endOfWeek()

-- Resolved-by-me-this-year (cookbook #33):
resolution CHANGED TO "Fixed" BY currentUser() DURING (startOfYear(), endOfYear())
```

**Prerequisites and failure mode:** `CHANGED` and the WAS family return nothing for fields without history tracking — most system fields track, some custom fields do not. If a `CHANGED` query returns zero rows, confirm transitions actually occurred and widen the date window before assuming the data is missing. Note the docs' own quirk: the >10,000-changes truncation paragraph under CHANGED still says "the WAS operator" — same limit, shared implementation.

## Relative Dates and Expressions

### Direct offsets on date fields

Date fields accept an increment string directly: `(+/-)nn(y|M|w|d|h)` — years, months (capital M!), weeks, days, hours. No function call needed:

```jql
created >= -7d          /* last seven days */
updated < -30d          /* untouched for a month */
duedate <= 2w           /* due within two weeks */
```

Case matters: `-1m` is minutes, `-1M` is months. If you drop the unit entirely the default depends on context (days for the bare-number legacy form).

### Function forms

| Expression | Evaluates to | Typical use |
|------------|--------------|-------------|
| `startOfDay()` | today 00:00 local | `created > startOfDay()` |
| `endOfDay()` | today 23:59 local | `due < endOfDay("+1")` |
| `startOfWeek()` | week start (Sunday default) | `created >= startOfWeek()` |
| `endOfWeek()` | week end (Saturday default) | `due <= endOfWeek()` |
| `startOfMonth()` / `endOfMonth()` | month boundaries | `resolved >= startOfMonth("-1M")` |
| `startOfYear()` / `endOfYear()` | Jan 1 / Dec 31 | retrospective windows |
| `now()` | exact current timestamp | `updated < now()` |

Offsets compose inside functions: `startOfWeek("+1d")` shifts to Monday on Sunday-default sites; `endOfMonth("+15d")` lands mid-next-month. Full parameter tables per function live in [jql-functions-catalog.md](jql-functions-catalog.md).

### Timezone trap

Jira evaluates dates in the querying user's timezone. A dashboard shared across regions shows different rows for the same `startOfDay()` query near midnight boundaries. For cross-timezone automation prefer explicit dates over day-grain relatives.

### Keep relatives in saved filters

Relative expressions re-evaluate at every run — exactly what you want in a saved filter. Freezing an absolute date into a filter meant as "this week" is a classic mistake: the filter silently stops matching next week.

## Saved Filters: Composition and Naming Conventions

Saved filters turn long JQL into reusable, shareable building blocks. From the filter lifecycle: save a search, manage/update/copy/delete it, star favorites, subscribe yourself or others to scheduled email delivery, share with colleagues (or outside the organization via links), export results (RSS, Excel), and drive dashboard gadgets.

### Composing queries with `filter =`

```jql
filter = "My Team Open Bugs" AND priority in (High, Highest)
filter = 10203 AND updated >= -7d        -- numeric filter IDs also work
```

Sub-queries compose once and get reused everywhere; fix logic in one place instead of pasting the same clause into twenty dashboards. Performance-wise this does not make Jira faster by itself (Jira expands the filter), but it makes the optimization advice in [jql-best-practices.md](jql-best-practices.md) applyable from a single edit point.

### Naming conventions that survive contact with reality

Jira does **not** enforce unique filter names — two people can each own "Open Bugs", and name-based references resolve ambiguously. Conventions that keep dashboards and subscriptions maintainable:

1. **Prefix by owning team or domain** — `platform-api-stale-prs`, `mobile-crash-triage`. Collisions become visible instead of silent.
2. **Encode scope and cadence** — `weekly-security-review`, `sprint-current-blocked`. Readers of a subscription email should know cadence without opening the filter.
3. **Never rename a filter others reference** — dashboard gadgets and subscriptions bind by filter identity, but humans navigate by name; renames strand both. Copy-and-deprecate instead.
4. **Prefer the numeric ID in scripts** — `filter = 10203` survives renames exactly like project IDs do; reserve name-based references for interactive use.
5. **Keep one canonical "definition" filter per recurring question** — then derive variants (`... AND assignee IS EMPTY`) rather than duplicating the whole query.

Sharing rules matter before composition works: a gadget or subscription breaks with "Filter not found" for any viewer lacking permission to the underlying filter — grant the audience access to the filter itself, not just the dashboard.

## Quick Pitfall Reference

| Symptom | Likely cause |
|---------|--------------|
| `WAS` errors on a custom field | History operators limited to Assignee/Fix Version/Priority/Reporter/Resolution/Status |
| Old history missing on a busy issue | >10,000 changes truncated to recent-only search |
| `CHANGED` returns nothing | No history tracking on the field, or transitions never actually happened |
| Month offset behaved like minutes | `-1m` (minutes) vs `-1M` (months) case sensitivity |
| Same filter shows different rows per region | Day-grain relatives evaluate in each user's timezone |
| Gadget says "Filter not found" | Viewer lacks permission to the referenced saved filter |

Attribution: adapted in part from the retired jira-jql skill, sourced from Atlassian official documentation.

## Sources

- JQL operators (WAS/CHANGED/predicate reference): https://support.atlassian.com/jira-software-cloud/docs/jql-operators/
- Advanced searching overview (clause structure, precedence, bounded JQL): https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/
- What is advanced search (precedence, reserved words, bounded/unbounded): https://support.atlassian.com/jira-software-cloud/docs/what-is-advanced-search-in-jira-cloud/
- JQL functions (date functions, increment syntax): https://support.atlassian.com/jira-software-cloud/docs/jql-functions/
- Save your search as a filter: https://support.atlassian.com/jira-software-cloud/docs/save-your-search-as-a-filter/
- JQL optimization recommendations: https://support.atlassian.com/jira-software-cloud/docs/jql-optimization-recommendations/
- Search endpoint that runs JQL over REST (startAt/maxResults envelope): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
