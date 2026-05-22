# JQL Functions — Complete Official Catalog

Full reference: https://support.atlassian.com/jira-software-cloud/docs/jql-functions/

## Date/Time Functions

All accept optional increment: `(+/-)nn(y|M|w|d|h|m)`. If the unit qualifier is omitted, it defaults to the natural period.

**Supported fields:** Created, Due, Resolved, Updated, custom Date/Time fields
**Supported operators:** `=, !=, >, >=, <, <=, WAS*, WAS IN*, WAS NOT*, WAS NOT IN*, CHANGED*` (* predicate only)
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
| `currentLogin()` | `updated > currentLogin()` | When session started |
| `lastLogin()` | `created > lastLogin()` | Previous login timestamp |

## User Functions

### `currentUser()`
Your identity. Only works for logged-in users (not anonymous).
- **Fields:** Assignee, Reporter, Voter, Watcher, Creator, custom User fields
- **Operators:** `=`, `!=`
- **Unsupported:** everything else

### `membersOf(group)`
Members of a group or team.
- **Syntax:** `membersOf("group-name")` or `membersOf(id:<teamId>)` for teams
- **Fields:** Assignee, Reporter, Voter, Watcher, Creator, custom User fields
- **Operators:** `IN, NOT IN, WAS IN, WAS NOT IN`
- **Does NOT support project roles**

### `componentsLeadByUser(user)`
Components led by a user. Omit user → current user.
- **Fields:** Component
- **Operators:** `IN, NOT IN`

### `spacesLeadByUser(user)`
Projects led by a user. Omit user → current user.
- **Fields:** Project (Space)
- **Operators:** `IN, NOT IN`

### `spacesWhereUserHasPermission(permission)`
Projects where you have a specific permission.
- **Fields:** Project
- **Operators:** `IN, NOT IN`
- Only available for logged-in users

### `spacesWhereUserHasRole(rolename)`
Projects where you have a specific role.
- **Fields:** Project
- **Operators:** `IN, NOT IN`

## Sprint/Version Functions

### `openSprints()`
Active sprints that have started but not yet completed.
- **Fields:** Sprint
- **Operators:** `IN, NOT IN`
- Issues can belong to both open AND closed sprints simultaneously

### `closedSprints()`
Completed sprints.
- **Fields:** Sprint
- **Operators:** `IN, NOT IN`

### `earliestUnreleasedVersion(project)`
Earliest unreleased version, ordered by the Releases page order (bottom = earliest).
- **Fields:** AffectedVersion, FixVersion, custom Version
- **Operators:** `=, !=`

### `latestReleasedVersion(project)`
Most recently released version.
- **Fields:** Same
- **Operators:** `=, !=`

### `releasedVersions(project)`
All released versions. Omit project for all projects.
- **Fields:** AffectedVersion, FixVersion, custom Version
- **Operators:** `IN, NOT IN`

### `unreleasedVersions(project)`
All unreleased versions. Omit project for all projects.
- **Fields:** AffectedVersion, FixVersion, custom Version
- **Operators:** `IN, NOT IN`

## Issue Functions

### `linkedIssues(key, linkType?)`
Issues linked to a specific issue.
- **Syntax:** `issue in linkedIssues("ABC-44")` or `issue in linkedIssues("ABC-44", "is blocked by")`
- **Fields:** Issue
- **Operators:** `IN, NOT IN`

### `issueHistory()` / `votedWorkItems()` / `watchedWorkItems()`
Recently viewed / voted on / watched issues.
- **Operators:** `IN, NOT IN`
- `votedWorkItems()` and `watchedWorkItems()` return up to 32,000 IDs

### `updatedBy(user, dateFrom?, dateTo?)`
Issues updated by a specific user (includes creating, updating fields, creating/deleting comments, editing comments).
- **Syntax:** `issue in updatedBy(jsmith, "-8d")` or `issue in updatedBy(jsmith, "2024/01/01", "2024/06/01")`
- **Minimum granularity:** 1 day (smaller values rounded up)

### `parentEpic` (field, not function)
Find stories/subtasks in a specific epic.
- **Syntax:** `parentEpic = DEMO-123` or `parentEpic in (DEMO-1, SAMPLE-4)`
- **Fields:** Issue
- **Operators:** `=, !=, IN, NOT IN`
- Only for company-managed projects

## Custom Field Functions

### `cascadeOption(parentOption, childOption?)`
Cascading Select custom fields.
- **Syntax:** `location in cascadeOption("USA", "New York")`
- Use `none` keyword for empty: `location in cascadeOption("USA", none)`
- **Operators:** `IN, NOT IN`

### `choiceOption(valueOption...)`
Multiple Choice or Dropdown custom fields.
- **Operators:** `IN, NOT IN`

### `standardWorkTypes()` / `subtaskWorkTypes()`
Filter by standard vs subtask issue types.
- **Fields:** Type
- **Operators:** `IN, NOT IN`

## Jira Service Management Functions

### Approval Functions
| Function | Syntax | Effect |
|----------|--------|--------|
| `approved()` | `approvals = approved()` | All approved requests |
| `pending()` | `approvals = pending()` | Has pending approval step |
| `approver(user)` | `approvals = approver(jsmith)` | Specific user is an approver (pending or completed) |
| `pendingApprovalBy(user)` | `approvals = pendingApprovalBy(jsmith)` | User has pending approval |
| `pendingBy(user)` | `approvals = pendingBy(jsmith)` | User is approver, may/may not have decided |
| `myApproval()` | `approvals = myApproval()` | Current user is approver |
| `myPendingApproval()` | `approvals = myPendingApproval()` | Current user has pending approval |
| `myPending()` | `approvals = myPending()` | Current user is approver for pending step |

### SLA Functions
| Function | Operators | Effect |
|----------|-----------|--------|
| `breached()` | `=, !=` | SLA missed its goal |
| `completed()` | `=, !=` | SLA cycle complete |
| `running()` | `=, !=` | SLA clock running |
| `paused()` | `=, !=` | SLA paused (out of calendar hours etc.) |
| `remaining()` | `=, !=, >, <, >=, <=` | Time remaining comparison |
| `withinCalendarHours()` | `=, !=` | Running within calendar hours |

### Organization Functions
| Function | Fields | Syntax |
|----------|--------|--------|
| `customerDetail("Field", "Value")` | Reporter, Assignee, Voter, Watcher | `reporter in customerDetail("Region", "APAC")` |
| `organizationDetail("Field", "Value")` | Organization | `organization in organizationDetail("Support level", "Platinum")` |
| `organizationMembers("OrgName")` | Reporter, Assignee, Voter, Watcher | `reporter in organizationMembers("Atlassian")` |

### `customerDetail()` / `organizationDetail()`
Used with multi-select dropdowns: chain multiple `AND` clauses.
- Returns up to 32,000 records
- Includes deleted/deactivated customers — exclude with `AND reporter NOT IN inactiveUsers()`
- **Operators:** `IN, NOT IN`
