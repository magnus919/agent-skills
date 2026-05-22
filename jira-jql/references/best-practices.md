# JQL Best Practices, Gotchas & Troubleshooting

## Performance Optimization

### Do's
- **Filter by project first** — narrows the search space immediately
- **Use `IN` over chained `OR`** — `status IN ("X", "Y")` vs `status = X OR status = Y`
- **Prefer indexed fields** — `project`, `issuetype`, `status`, `assignee` are always indexed
- **Use IDs for stable entities** — `project = 1001` survives renames; `project = "Old Name"` breaks
- **Break complex queries into saved filters** — reference with `filter = "Saved Filter Name"`

### Don'ts
- **Don't lead with wildcards** — `summary ~ "*bug"` forces full-text scan across all issues
- **Don't overuse negations** — `!=`, `!~`, `NOT` scan wider than positive conditions
- **Don't sort in JQL when downstream sorts** — redundant sorting wastes server cycles
- **Don't mix AND/OR without parentheses** — AND binds tighter than OR, results will surprise

## Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Missing EMPTY on negation | `assignee != currentUser()` | `(assignee != currentUser() OR assignee IS EMPTY)` |
| AND/OR precedence | `A OR B AND C` | `(A OR B) AND C` |
| Name vs ID fragility | `project = "My Project"` | `project = 1001` |
| Searching by renamed sprint | `sprint = "Sprint 1"` | Use sprint ID |
| Status but no resolution | `status = Done` | Add `resolution IS NOT EMPTY` or `resolution = Fixed` |
| Missing timezone offsets | `created > startOfDay()` | Jira uses the user's configured timezone |
| Forgetting sprint scope | `sprint IS EMPTY` | Also check `sprint NOT IN openSprints()` for backlog |

## Gotchas

### Core Platform
- **Atlassian is renaming "issue" to "work item"** — old terms (project, issue, fixVersion) still work. No migration needed. New docs use "work item" but queries are backward-compatible.
- **JQL has NO aggregation** — COUNT, SUM, AVG don't exist. Must use dashboard gadgets (pie chart, statistics), marketplace apps (eazyBI, ScriptRunner), or Jira REST API with external processing.
- **No recursive hierarchy traversal** — can't grab epics + their stories + their subtasks in one query. Run three separate JQL statements or use marketplace plugins.
- **`IS EMPTY` only works for fields that exist** — can't find issues that *never had a value* for a field.
- **`!=` excludes nulls** — always pair with `OR field IS EMPTY` if you want truly everything except the value.

### Function-Specific
- **`membersOf()` does NOT support project roles** — only Jira groups and teams (by teamId).
- **`updatedBy()` rounds to 1 day minimum** — `updatedBy(jsmith, "-1h")` becomes `-1d`.
- **`votedWorkItems()` / `watchedWorkItems()` capped at 32,000** — if you watch more, results truncate silently.
- **`cascadeOption(none)` is keyword-based** — to literally search for a value "none", wrap in quotes: `cascadeOption("\"none\"")`.

### Jira Cloud-Specific
- **Saved filters can share names** — Jira doesn't prevent duplicates. Bad for dashboard gadgets.
- **Auto-suggest list depends on permissions** — if you can't see a field in autocomplete, you may lack permission for it.
- **JQL AI assistant exists** — button left of JQL bar in Cloud. Early-stage; useful for beginners but misses nuance.
- **Some custom fields don't log history** — `CHANGED` and `WAS` won't work on fields without history tracking enabled.

### ScriptRunner (if available)
- **Powerful but heavier** — `issueFunction` can create custom JQL expressions but adds latency
- **Common use:** `issueFunction in hasLinkType("Epic-Story Link")`, `issueFunction in commented("by user after -1d")`

## Troubleshooting Flow

**"No results, query looks valid"**
1. Check field name spelling (custom fields especially)
2. Verify project/sprint/version existence
3. Check case sensitivity — values may be case-sensitive depending on Jira config
4. Try `ORDER BY created DESC` to confirm query works but returns no matches

**"Query is very slow"**
1. Remove leading wildcards from text searches
2. Add project filter first
3. Replace `OR` chains with `IN`
4. Remove negations if possible
5. Reduce result set with tighter date/status filters

**"Field doesn't exist"**
1. Field may be disabled for this project
2. May be a custom field from an uninstalled marketplace app
3. Check if the user running it has permission to that field

**"CHANGED returns nothing"**
1. The field may not track history
2. Verify date range — `CHANGED TO "Done" AFTER startOfDay()` may be too narrow
3. Check that the transition actually happened (some workflows skip statuses)

**"WAS operator returns no results"**
1. The field must have a trackable history (most system fields do)
2. Verify the value was ever set — `WAS` returns nothing if the field was always current value

## Marketplace Extensions

| Plugin | Hosting | What It Adds |
|--------|---------|-------------|
| JQL Tricks Plugin | Server/DC | 50+ extra functions |
| JQL Search Extensions | Cloud | Find issues, comments, attachments, subtasks, versions, epics, links |
| JQL Booster Pack | Server/DC | 15+ user-related functions, archived version filtering |
| JQL Functions Collection | Server/DC | String and date format functions |
| Groups & Organizations JQL | Server/DC | Match multi-group custom field values |
| ScriptRunner | Cloud/Server/DC | Custom Groovy JQL functions — most powerful and flexible |
