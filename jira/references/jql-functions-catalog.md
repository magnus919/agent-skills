# JQL Functions — Complete Catalog

Every JQL function with its supported fields, operators, and worked syntax. Pairs with [jql-best-practices.md](jql-best-practices.md) for performance rules and [jql-cookbook.md](jql-cookbook.md) for ready-to-run queries.

Increment strings follow the `(+/-)nn(y|M|w|d|h|m)` pattern everywhere a date function accepts an offset; if the unit qualifier is omitted it defaults to the function's natural period.

## Date and Time Functions

All accept an optional increment string `(+/-)nn(y|M|w|d|h|m)`. If the unit qualifier is omitted, it defaults to the natural period shown below.

**Supported fields:** Created, Due, Resolved, Updated, custom Date/Time fields
**Supported operators:** `=, !=, >, >=, <, <=, WAS*, WAS IN*, WAS NOT*, WAS NOT IN*, CHANGED*` (* predicate position only)
**Unsupported operators:** `~, !~, IS, IS NOT, IN, NOT IN`

| Function | Syntax | Notes |
|----------|--------|-------|
| `startOfDay()` | `created > startOfDay("-1")` | Start of current day. Default unit: d |
| `endOfDay()` | `due < endOfDay("+2")` | End of current day. Default unit: d |
| `startOfWeek()` | `created > startOfWeek("+1d")` | Start of week (Sunday default; +1d shifts to Monday) |
| `endOfWeek()` | `due < endOfWeek("+1")` | End of week (Saturday default by Saturday) |
| `startOfMonth()` | `created > startOfMonth("-1")` | Start of current month |
| `endOfMonth()` | `due < endOfMonth("+15d")` | End of current month. +15d = 15th of next month |
| `startOfYear()` | `created > startOfYear()` | January 1st |
| `endOfYear()` | `due < endOfYear()` | December 31st |
| `now()` | `updated < now()` | Current exact time |
| `currentLogin()` | `updated > currentLogin()` | When the session started |
| `lastLogin()` | `created > lastLogin()` | Previous login timestamp |

Relative offsets work directly on date fields without a function: `created >= -7d`, `updated < -30d`.

## User Functions

### `currentUser()`

Your identity. Only works for logged-in users (not anonymous access).

- **Fields:** Assignee, Reporter, Voter, Watcher, Creator, custom User fields
- **Operators:** `=`, `!=`

### `membersOf(group)`

Members of a group or team.

- **Syntax:** `membersOf("group-name")`, or `membersOf(id:<teamId>)` for teams
- **Fields:** Assignee, Reporter, Voter, Watcher, Creator, custom User fields
- **Operators:** `IN, NOT IN, WAS IN, WAS NOT IN`
- Does **NOT** support project roles — groups and teams only

### `componentsLeadByUser(user)`

Components led by a user. Omit the user argument to mean the current user.

- **Fields:** Component
- **Operators:** `IN, NOT IN`

### `spacesLeadByUser(user)`

Projects led by a user. Omit the user argument to mean the current user.

- **Fields:** Project (Space)
- **Operators:** `IN, NOT IN`

### `spacesWhereUserHasPermission(permission)`

Projects where you hold a specific permission, e.g. `"Edit work items"`.

- **Fields:** Project
- **Operators:** `IN, NOT IN`
- Only available for logged-in users

### `spacesWhereUserHasRole(rolename)`

Projects where you have a specific role, e.g. `"Administrators"`.

- **Fields:** Project
- **Operators:** `IN, NOT IN`

## Sprint and Version Functions

### `openSprints()`

Active sprints that have started but not yet completed.

- **Fields:** Sprint
- **Operators:** `IN, NOT IN`
- Issues can belong to open AND closed sprints simultaneously

### `closedSprints()`

Completed sprints.

- **Fields:** Sprint
- **Operators:** `IN, NOT IN`

### `earliestUnreleasedVersion(project)`

Earliest unreleased version, ordered by the Releases page order (bottom = earliest).

- **Fields:** AffectedVersion, FixVersion, custom Version fields
- **Operators:** `=, !=`

### `latestReleasedVersion(project)`

Most recently released version.

- **Fields:** AffectedVersion, FixVersion, custom Version fields
- **Operators:** `=, !=`

### `releasedVersions(project)`

All released versions. Omit the project argument to search across all projects.

- **Fields:** AffectedVersion, FixVersion, custom Version fields
- **Operators:** `IN, NOT IN`

### `unreleasedVersions(project)`

All unreleased versions. Omit the project argument to search across all projects.

- **Fields:** AffectedVersion, FixVersion, custom Version fields
- **Operators:** `IN, NOT IN`

## Issue Functions

### `linkedIssues(key, linkType?)`

Issues linked to a specific issue. The link type argument is optional.

```jql
issue in linkedIssues("ABC-44")
issue in linkedIssues("ABC-44", "is blocked by")
```

- **Fields:** Issue
- **Operators:** `IN, NOT IN`

### `issueHistory()` / `votedWorkItems()` / `watchedWorkItems()`

Recently viewed, voted-on, and watched issues respectively.

- **Operators:** `IN, NOT IN`
- `votedWorkItems()` and `watchedWorkItems()` return up to 32,000 issue IDs

### `updatedBy(user, dateFrom?, dateTo?)`

Issues updated by a specific user — includes creating the issue, updating fields, creating/deleting comments, and editing comments.

```jql
issue in updatedBy(jsmith, "-8d")
issue in updatedBy(jsmith, "2024/01/01", "2024/06/01")
```

- **Operators:** `IN, NOT IN` (used with the `issue` field)
- Minimum granularity is 1 day; smaller values such as `-1h` round up to `-1d`

### `parentEpic` (field, not a function)

Find stories/subtasks belonging to a specific epic.

```jql
parentEpic = DEMO-123
parentEpic in (DEMO-1, SAMPLE-4)
```

- **Fields:** Issue
- **Operators:** `=, !=, IN, NOT IN`
- Company-managed projects only

## Custom Field Functions

### `cascadeOption(parentOption, childOption?)`

Cascading Select custom fields.

```jql
location in cascadeOption("USA", "New York")
```

Use the `none` keyword to match an empty tier: `location in cascadeOption("USA", none)`.

- **Operators:** `IN, NOT IN`

### `choiceOption(valueOption...)`

Multiple Choice or Dropdown custom fields.

- **Operators:** `IN, NOT IN`

### `standardWorkTypes()` / `subtaskWorkTypes()`

Filter by standard versus subtask issue types.

- **Fields:** Type
- **Operators:** `IN, NOT IN`

## Jira Service Management Functions

These require Jira Service Management and operate on the Approval and SLA custom fields.

### Approval Functions

| Function | Syntax | Effect |
|----------|--------|--------|
| `approved()` | `approvals = approved()` | All approved requests |
| `pending()` | `approvals = pending()` | Has a pending approval step |
| `approver(user)` | `approvals = approver(jsmith)` | Specific user is an approver (pending or completed) |
| `pendingApprovalBy(user)` | `approvals = pendingApprovalBy(jsmith)` | User has a pending approval |
| `pendingBy(user)` | `approvals = pendingBy(jsmith)` | User is an approver, may or may not have decided |
| `myApproval()` | `approvals = myApproval()` | Current user is an approver |
| `myPendingApproval()` | `approvals = myPendingApproval()` | Current user has a pending approval |
| `myPending()` | `approvals = myPending()` | Current user is the approver for a pending step |

### SLA Functions

| Function | Operators | Effect |
|----------|-----------|--------|
| `breached()` | `=, !=` | SLA missed its goal |
| `completed()` | `=, !=` | SLA cycle complete |
| `running()` | `=, !=` | SLA clock running |
| `paused()` | `=, !=` | SLA paused (out of calendar hours, etc.) |
| `remaining()` | `=, !=, >, <, >=, <=` | Compare remaining time |
| `withinCalendarHours()` | `=, !=` | Running within calendar hours |

### Organization and Customer Functions

| Function | Fields | Syntax |
|----------|--------|--------|
| `customerDetail("Field", "Value")` | Reporter, Assignee, Voter, Watcher | `reporter in customerDetail("Region", "APAC")` |
| `organizationDetail("Field", "Value")` | Organization | `organization in organizationDetail("Support level", "Platinum")` |
| `organizationMembers("OrgName")` | Reporter, Assignee, Voter, Watcher | `reporter in organizationMembers("YOUR_ORG")` |

`customerDetail()` and `organizationDetail()` pair with multi-select dropdown fields; chain multiple `AND` clauses for combined matches. Both return up to 32,000 records and include deleted/deactivated customers — exclude them with `AND reporter NOT IN inactiveUsers()`.

- **Operators:** `IN, NOT IN`

Attribution: adapted from the retired jira-jql skill, sourced from Atlassian official documentation and community best practices.

## Sources

- JQL functions reference: https://support.atlassian.com/jira-software-cloud/docs/jql-functions/
- JQL fields reference: https://support.atlassian.com/jira-software-cloud/docs/jql-fields/
- Search endpoint used to run JQL over REST: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
