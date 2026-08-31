# JQL Best Practices, Performance & Troubleshooting

Performance rules, the traps JQL springs on unwary writers, and a troubleshooting flow for queries that misbehave. Pairs with [jql-functions-catalog.md](jql-functions-catalog.md) for the function reference and [jql-cookbook.md](jql-cookbook.md) for ready-to-run queries.

## Operator Precedence

**AND binds tighter than OR.** `A OR B AND C` parses as `A OR (B AND C)` — almost never what you meant. Always parenthesize OR groups:

```text
-- Correct
(project = A OR project = B) AND status = Open

-- Wrong — reads as project = A OR (project = B AND status = Open)
project = A OR project = B AND status = Open
```

Mixing AND and OR without parentheses is listed in the common-mistakes table below for a reason: results will surprise you.

## Performance Optimization

### Do's

- **Filter by project first** — narrows the search space immediately
- **Use `IN` over chained `OR`** — `status IN ("X", "Y")` vs `status = X OR status = Y`
- **Prefer indexed fields** — `project`, `issuetype`, `status`, `assignee` are always indexed
- **Use IDs for stable entities** — `project = 1001` survives renames; `project = "Old Name"` breaks when the name changes
- **Break complex queries into saved filters** — save the sub-query once, then compose with `filter = "Saved Filter Name"`
- **Keep relative dates in saved filters** — they stay dynamic instead of freezing at creation time

### Don'ts

- **Don't lead with wildcards** — `summary ~ "*bug"` forces a full-text scan across all issues; starting a text search with `*` is very expensive, put wildcards after the first few characters
- **Don't overuse negations** — `!=`, `!~`, `NOT IN`, `NOT` scan wider than positive conditions
- **Don't sort in JQL when downstream sorts** — redundant sorting wastes server cycles
- **Don't mix AND/OR without parentheses** — see precedence rule above

## The Empty-Value Trap

Negation does **not** include empty values. `!=` excludes nulls, so a plain negation silently drops unassigned issues. Explicitly include EMPTY:

```jql
-- Finds all issues NOT assigned to current user, INCLUDING unassigned
(assignee != currentUser() OR assignee IS EMPTY)

-- NOT this — misses unassigned issues entirely
assignee != currentUser()
```

The same trap applies to every negated comparison (`!=`, `NOT IN`) on optional fields. If you want "everything except X", write `(field != X OR field IS EMPTY)`.

## Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Missing EMPTY on negation | `assignee != currentUser()` | `(assignee != currentUser() OR assignee IS EMPTY)` |
| AND/OR precedence | `A OR B AND C` | `(A OR B) AND C` |
| Name vs ID fragility | `project = "My Project"` | `project = 1001` (IDs survive renames) |
| Searching by renamed sprint | `sprint = "Sprint 1"` | Use the sprint ID |
| Status but no resolution | `status = Done` | Add `resolution IS NOT EMPTY` or `resolution = Fixed` |
| Missing timezone offsets | `created > startOfDay()` | Jira evaluates dates in the user's configured timezone |
| Forgetting sprint scope | `sprint IS EMPTY` | Also check `sprint NOT IN openSprints()` to catch backlog items |

## Gotchas

### Core Platform

- **Atlassian is renaming "issue" to "work item"** — old terms (project, issue, fixVersion) still work; no migration needed. New docs say "work item", but existing queries are backward-compatible.
- **JQL has NO aggregation** — COUNT, SUM, AVG do not exist. Use dashboard gadgets (pie chart, statistics), marketplace apps such as eazyBI or ScriptRunner, or pull via REST API and aggregate externally.
- **No recursive hierarchy traversal** — you cannot fetch epics + their stories + their subtasks in one query. Run separate statements per level, or use marketplace plugins.
- **`IS EMPTY` only works for fields that exist** — it cannot find issues where a field was *never* given a value.
- **`!=` excludes nulls** — pair it with `OR field IS EMPTY` whenever you want truly everything except a value.

### Function-Specific

- **`membersOf()` does NOT support project roles** — only Jira groups and teams (by team id).
- **`updatedBy()` rounds to a 1-day minimum** — `updatedBy(jsmith, "-1h")` behaves as `-1d`.
- **`votedWorkItems()` / `watchedWorkItems()` cap at 32,000** — beyond that, results truncate silently.
- **`cascadeOption(none)` is keyword-based** — to literally match a value of "none", quote-escape it: `cascadeOption("\"none\"")`.

### Jira Cloud-Specific

- **Saved filters can share names** — Jira does not prevent duplicates, which makes name-based dashboard gadget references fragile.
- **Auto-suggest depends on permissions** — if a field never appears in autocomplete, you may simply lack permission to it.
- **A JQL AI assistant exists in Cloud** — button left of the JQL bar. Early-stage; useful for beginners but misses nuance.
- **Some custom fields don't log history** — `CHANGED` and `WAS` silently return nothing on fields without history tracking.

### ScriptRunner (if installed)

- **Powerful but heavier** — `issueFunction` adds latency versus native JQL.
- **Common uses:** `issueFunction in hasLinkType("Epic-Story Link")`, `issueFunction in commented("by user after -1d")`.

## Troubleshooting Flow

**Query returns 0 results unexpectedly**

1. Check field-name spelling (custom fields especially)
2. Verify the project/sprint/version actually exists
3. Check value case sensitivity — it depends on your Jira configuration
4. Run `ORDER BY created DESC` alone to confirm the query executes and genuinely has no matches
5. Remember the empty-value trap: negations exclude empty fields

**Query is valid but slow**

1. Remove leading wildcards from text searches
2. Add a project filter first
3. Replace `OR` chains with `IN`
4. Remove negations where possible
5. Tighten date/status bounds to shrink the candidate set

**Jira says "Field 'X' does not exist"**

1. The field may be disabled for this project
2. It may be a custom field owned by an uninstalled marketplace app
3. The querying user may lack permission to that field

**"Filter not found" when using `filter =`**

- The user lacks permission to that saved filter (or the filter was deleted).

**`CHANGED` returns nothing**

1. The field may not track history
2. Widen the date range — `CHANGED TO "Done" AFTER startOfDay()` may be too narrow
3. Confirm the transition actually happened; some workflows skip statuses

**`WAS` operator returns no results**

1. Most system fields have trackable history, but verify this one does
2. `WAS` matches past values — if the field always held its current value there is no history to match

## Marketplace Extensions for Advanced Needs

| Plugin | Hosting | What It Adds |
|--------|---------|-------------|
| JQL Tricks Plugin | Server/DC | 50+ extra functions |
| JQL Search Extensions | Cloud | Find comments, attachments, subtasks, epics, links |
| JQL Booster Pack | Server/DC | 15+ user-related functions, archived version filtering |
| JQL Functions Collection | Server/DC | String and date format functions |
| Groups & Organizations JQL | Server/DC | Match multi-group custom field values |
| ScriptRunner (Adaptavist) | Cloud/Server/DC | Custom Groovy JQL functions — most powerful and flexible |

Attribution: adapted from the retired jira-jql skill, sourced from Atlassian official documentation and community best practices.

## Sources

- Advanced searching (JQL): https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/
- Search endpoint used to run JQL over REST: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
