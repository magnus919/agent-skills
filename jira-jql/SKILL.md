---
name: jira-jql
description: >-
  Expert-level skill for Jira Query Language (JQL). Use when the user asks about
  writing, debugging, optimizing, or understanding JQL queries; needs to filter
  Jira issues by complex criteria, date ranges, history, or cross-project conditions;
  wants to build saved filters, dashboard gadgets, or automation rules; or needs
  guidance on JQL performance, functions, operators, history operators (WAS/CHANGED),
  relative dates, role-based query patterns, or the JQL REST API.
license: MIT
compatibility: Compatible with any agent supporting the Agent Skills format
metadata:
  source: "Atlassian official docs + community best practices"
  spec-version: "1.0"
  topics: "jql,jira,query-language,atlassian"
allowed-tools: terminal web_search web_extract
---

# Jira Query Language (JQL) — Expert Reference

JQL is Atlassian's structured query language for searching Jira issues (now called "work items"). Every clause is **Field + Operator + Value**, chained with keywords.

Use this skill when:
- The user asks for help writing or debugging a JQL query
- They need to find issues across projects, sprints, versions, components
- They want to use history operators (WAS, CHANGED) for trend/sprint analysis
- Performance optimization or saved filter design is needed
- They're building automation rules, REST API calls, or dashboard gadgets with JQL

---

## 1. Core Syntax

```
field OPERATOR value [AND|OR field OPERATOR value ...] [ORDER BY field [ASC|DESC]]
```

### Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=`, `!=` | Equals, not equals | `assignee = currentUser()` |
| `>`, `<`, `>=`, `<=` | Comparison | `created >= -7d` |
| `IN`, `NOT IN` | Set membership | `status IN ("To Do", "In Progress")` |
| `IS`, `IS NOT` | Null check — only with `EMPTY` or `NULL` | `assignee IS EMPTY` |
| `~`, `!~` | Contains (text search) | `summary ~ "login*"` |
| `WAS`, `WAS NOT` | Historical value | `assignee WAS "jsmith"` |
| `WAS IN`, `WAS NOT IN` | Historical set | `fixVersion WAS IN ("Sprint 1", "Sprint 2")` |
| `CHANGED` | Field transition | `status CHANGED FROM "Open" TO "Done"` |

### Keywords

| Keyword | Purpose |
|---------|---------|
| `AND` | Both conditions must be true (binds tighter than OR) |
| `OR` | At least one condition must be true |
| `NOT` | Negates a clause |
| `ORDER BY` | Sorting — add `ASC` or `DESC` (default ASC) |
| `EMPTY` / `NULL` | Used with `IS` / `IS NOT` |

### Precedence

**AND binds tighter than OR.** `A OR B AND C` = `A OR (B AND C)`. Always parenthesize OR groups:

```jql
-- Correct
(project = A OR project = B) AND status = Open

-- Wrong — reads as project = A OR (project = B AND status = Open)
project = A OR project = B AND status = Open
```

---

## 2. Available Fields (System)

Common indexed fields that JQL accepts:

`project`, `issuetype`, `status`, `assignee`, `reporter`, `creator`, `priority`, `resolution`, `resolutiondate`, `created`, `updated`, `duedate`, `fixVersion`, `affectedVersion`, `component`, `labels`, `sprint`, `votes`, `watchers`, `workRatio`, `parentEpic`, `issueLinkType`, `statusCategory`

Custom fields work by name — quote if they contain spaces: `"Story Points"`.

**Pro tip:** Prefer IDs over names for project/sprint/version when possible — names change, IDs (`project = 1001`) don't.

---

## 3. Functions (Complete Catalog)

### Date/Time Relative Functions

All accept optional increment strings in `(+/-)nn(y|M|w|d|h|m)` format. Default unit matches the function's natural period.

| Function | Default Unit | Example |
|----------|-------------|---------|
| `startOfDay()` / `endOfDay()` | `d` | `created > startOfDay("-1")` = yesterday |
| `startOfWeek()` / `endOfWeek()` | `w` | `due < endOfWeek("+1w")` = end of next week |
| `startOfMonth()` / `endOfMonth()` | `M` | `created > startOfMonth("-1")` = start of last month |
| `startOfYear()` / `endOfYear()` | `y` | `resolutiondate > startOfYear()` |
| `now()` | — | Current timestamp |
| `currentLogin()` | — | When session began |
| `lastLogin()` | — | Previous login |

### User Functions

| Function | Fields | Operators | Behavior |
|----------|--------|-----------|----------|
| `currentUser()` | Assignee, Reporter, Voter, Watcher, Creator + custom User | `=`, `!=` | Your identity |
| `membersOf("group")` | Assignee, Reporter, Voter, Watcher, Creator | `IN`, `NOT IN`, `WAS IN`, `WAS NOT IN` | Group members. For teams: `membersOf(id:<teamId>)` |
| `componentsLeadByUser(user)` | Component | `IN`, `NOT IN` | Omit user = current user |
| `spacesLeadByUser(user)` | Project (Space) | `IN`, `NOT IN` | Omit user = current user |
| `spacesWhereUserHasPermission(p)` | Project | `IN`, `NOT IN` | e.g. `"Edit work items"` |
| `spacesWhereUserHasRole(role)` | Project | `IN`, `NOT IN` | e.g. `"Administrators"` |

### Sprint/Version Functions

| Function | Fields | Behavior |
|----------|--------|----------|
| `openSprints()` | Sprint | Active, not yet completed |
| `closedSprints()` | Sprint | Completed sprints |
| `earliestUnreleasedVersion(project)` | AffectedVersion, FixVersion, custom Version | Earliest unreleased in release order |
| `latestReleasedVersion(project)` | Same | Most recently released version |
| `releasedVersions(project)` | Same | All released. Omit project for all |
| `unreleasedVersions(project)` | Same | All unreleased. Omit project for all |

### Issue Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `linkedIssues(key, linkType?)` | `issue in linkedIssues("ABC-44")` | Link type optional — e.g. `"is blocked by"` |
| `parentEpic` (field) | `parentEpic = DEMO-123` | Stories/subtasks in an epic |
| `issueHistory()` | `issue in issueHistory()` | Recently viewed |
| `votedWorkItems()` | `issue in votedWorkItems()` | You voted on these |
| `watchedWorkItems()` | `issue in watchedWorkItems()` | You watch these |
| `updatedBy(user, from?, to?)` | `issue in updatedBy(jsmith, "-8d")` | Updated by user. Rounds < 1d up to 1d |

### Jira Service Management Functions

| Function | Field Type | Effect |
|----------|-----------|--------|
| `approved()`, `pending()` | Custom Approval | Approval state |
| `approver(user)`, `pendingApprovalBy(user)` | Custom Approval | Specific approver |
| `myApproval()`, `myPendingApproval()` | Custom Approval | Current user as approver |
| `breached()`, `running()`, `paused()`, `completed()` | SLA | SLA state |
| `remaining()` | SLA | Compare remaining time |
| `withinCalendarHours()` | SLA | Running within calendar |
| `customerDetail("Field", "Value")` | Reporter, Organization | Customer attribute search |
| `organizationDetail("Field", "Value")` | Organization | Org attribute search |
| `organizationMembers("Org")` | Reporter, Assignee | Members of organization |

### Custom Field Functions

| Function | Field Type | Use With |
|----------|-----------|----------|
| `cascadeOption(parent, child?)` | Cascading Select | `IN`, `NOT IN` |
| `choiceOption(value1, value2...)` | Multiple Choice / Dropdown | `IN`, `NOT IN` |

Use `none` keyword to search for empty cascade tiers: `location in cascadeOption("USA", none)`.

---

## 4. History Operators (WAS / CHANGED)

JQL can search issue *history*, not just current state. This is unique to JQL vs SQL.

### WAS / WAS NOT / WAS IN / WAS NOT IN

```
assignee WAS "jsmith"                              -- Was assigned to jsmith at any point
fixVersion WAS "Sprint A"                          -- Was in Sprint A historically
status WAS IN ("In Progress", "Under Review")      -- Was any of these statuses
```

WAS supports a **predicate clause** for time bounds:

```
status WAS "In Progress" DURING (startOfWeek(), endOfWeek())
assignee WAS "jsmith" BEFORE "2024/01/01"
status WAS "Open" BY currentUser()
```

### CHANGED

```
status CHANGED FROM "Open" TO "Done"                       -- Transition took place
status CHANGED FROM "Open" TO "Done" AFTER -1d             -- Today
status CHANGED TO "Done" BY currentUser()                   -- Who did it
resolution CHANGED TO "Fixed" DURING (startOfYear(), endOfYear())  -- Year recap
```

**Supported operators for `CHANGED` predicate:** `AFTER`, `BEFORE`, `DURING`, `BY`, `FROM`, `TO`

---

## 5. Relative Date Expressions

All date fields support ISO 8601 absolute dates AND relative offsets:

| Expression | Meaning |
|-----------|---------|
| `-1d` | 1 day ago |
| `-2w` | 2 weeks ago |
| `+1M` | 1 month from now |
| `-3h` | 3 hours ago |
| `-1y` | 1 year ago |
| `"2026-05-22"` | Absolute date |
| `"2026/05/22"` | Absolute date (alternative) |

Common dynamic patterns:

```jql
created >= -7d                                          -- Last 7 days
duedate >= startOfWeek() AND duedate <= endOfWeek()     -- This week
resolutiondate >= startOfDay(-3M) AND resolutiondate < endOfDay(-3M)  -- Exactly 3 months ago
created > startOfMonth("-1")                            -- Since start of last month
updated < -30d                                          -- Zombie tickets (not touched in 30 days)
```

---

## 6. Best Practices & Performance

### Write Efficient Queries

1. **Filter by project first** — narrows the search space immediately
2. **Use `IN` instead of chained `OR`** — `status IN (3 values)` vs `status = X OR status = Y OR status = Z`
3. **Prefer indexed fields** — `project`, `issuetype`, `status`, `assignee` are indexed
4. **Avoid negations** — `!=`, `!~`, `NOT`, `NOT IN` scan wider
5. **No leading wildcards** — `summary ~ "*bug"` forces full-scan
6. **Don't sort in JQL if downstream sorts** — redundant sort wastes time

### Handle Empty Values Correctly

`!=` does NOT include empty/null values. Explicitly include EMPTY:

```jql
-- Finds all issues NOT assigned to current user, INCLUDING unassigned
(assignee != currentUser() OR assignee IS EMPTY)

-- NOT this — misses unassigned issues
assignee != currentUser()
```

### Organize Saved Filters

- **Break complex queries into reusable sub-filters** — save sub-queries as filters, then compose: `filter = "Unresolved ABC bugs" AND assignee = currentUser()`
- **Consistent naming convention**: `{Sprint}_{Epic}_{OrderedBy}` — e.g. `CurrentSprint_AudioDevEpic_OrderedByAssignee`
- **Use relative dates in saved filters** — they stay dynamic: `created >= startOfMonth()`

### Scope-Sort Pattern

Start broad, narrow iteratively:

```jql
-- Step 1: all open issues
project = PWC AND status = open

-- Step 2: narrow by sprint
project = PWC AND status = open AND fixVersion = "Current Sprint"

-- Step 3: carried-over issues only
project = PWC AND status = open AND fixVersion = "Current Sprint" AND fixVersion WAS "Last Sprint"

-- Step 4: sort by priority then assignee
... ORDER BY priority, assignee
```

---

## 7. Role-Based Ready Queries

### Developers

```jql
-- My unresolved issues by priority
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC

-- Bugs I reported
reporter = currentUser() AND status != Done

-- My completed work this week
resolution = Fixed AND resolutiondate >= -7d AND assignee = currentUser()

-- Where I'm mentioned in comments
comment ~ currentUser()
```

### Scrum Masters

```jql
-- Unassigned in active sprint
sprint IN openSprints() AND assignee IS EMPTY

-- Stale tickets
status NOT IN (Closed, Done) AND updated < -30d

-- Recently completed
status CHANGED TO Done AFTER startOfWeek()

-- Reopened tickets (quality flag)
status CHANGED FROM Done TO "In Progress"

-- Team's in-progress work
assignee in membersOf("Dev Team") AND status = "In Progress"
```

### Product Owners

```jql
-- Pre-release readiness
fixVersion = earliestUnreleasedVersion() AND status != Done

-- Critical/Highest unresolved bugs
priority IN (Critical, Highest) AND resolution = Unresolved

-- Due this sprint
duedate >= startOfMonth() AND duedate <= endOfMonth() AND resolution = Unresolved

-- Pending approvals (JSM)
approvals = pending()
```

### Cross-Project Portfolio

```jql
project in ("Project Mercury", "PTC") AND issuetype in ("Epic", "Task") AND created >= -180d
```

---

## 8. Gotchas & Known Limitations

- **Standard JQL has no aggregation** — no COUNT, SUM, AVG. Use dashboard gadgets or marketplace apps.
- **Can't check linked issue status** — `issueLinkType = "is blocked by"` finds links but can't check if the blocker is resolved. Needs ScriptRunner.
- **No recursive hierarchy traversal** — epics+stories+subtasks need separate queries.
- **`updatedBy()` rounds < 1 day up to 1 day** — `updatedBy(jsmith, "-1h")` becomes 1 day.
- **`membersOf()` does NOT support project roles** — only groups and teams.
- **`IS EMPTY` works for fields that exist** — can't find issues where a field was *never* created.
- **Atlassian is renaming "issue" to "work item"** — old terms (`project`, `issue`, `fixVersion`) still work; no migration needed.
- **Starting a text search with `*` is very expensive** — put wildcards after the first few chars.

### Marketplace Extensions for Advanced Needs

| Extension | What It Adds |
|-----------|-------------|
| JQL Tricks Plugin | 50+ extra functions |
| JQL Search Extensions (Cloud) | Find comments, attachments, subtasks, epics |
| JQL Booster Pack (Server/DC) | 15+ user-related functions |
| ScriptRunner (Adaptavist) | Custom Groovy JQL functions — most powerful |

---

## 9. JQL in REST API

Query via Jira REST API v3:

```bash
curl -u email:token \
  "https://your-domain.atlassian.net/rest/api/3/search?jql=project=PWC+AND+status=Open&fields=summary,assignee"
```

Returns structured JSON. Use `jql` parameter, URL-encode when needed. Also supports `startAt`, `maxResults`, `fields`, `expand` params.

---

## 10. Edge Cases & Troubleshooting

**Query is valid but slow:** Check for leading wildcards, unindexed custom fields, or missing project filter.

**Query returns 0 results unexpectedly:** Verify field names haven't changed (esp. custom fields), check for case sensitivity in values (depends on Jira config), and ensure you're in the right project scope.

**"Filter not found" when using `filter =`:** The user doesn't have permission to that saved filter.

**`CHANGED` returns nothing:** Ensure the field actually has tracking enabled. Some custom fields don't log history.

**Jira says "Field 'X' does not exist":** The field name is wrong, disabled for this project, or requires a marketplace app.

---

## Key Reference URLs

- **Official JQL Functions:** https://support.atlassian.com/jira-software-cloud/docs/jql-functions/
- **JQL Operators:** https://support.atlassian.com/jira-software-cloud/docs/jql-operators/
- **JQL Fields:** https://support.atlassian.com/jira-software-cloud/docs/jql-fields/
- **JQL Keywords:** https://support.atlassian.com/jira-software-cloud/docs/jql-keywords/
- **JQL Performance KB:** https://confluence.atlassian.com/jirakb/understanding-jql-performance-720416549.html
- **Free Atlassian University Intro to JQL:** https://www.youtube.com/watch?v=BcHKXSiOHqw
