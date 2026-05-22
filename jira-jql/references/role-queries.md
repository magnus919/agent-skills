# JQL — Role-Based Ready Queries

## Developers

```jql
-- My plate, sorted by urgency
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC

-- Bugs I reported that haven't been fixed
reporter = currentUser() AND status != Done

-- Where I'm mentioned (standup prep)
comment ~ currentUser()

-- My completed work this week
resolution = Fixed AND resolutiondate >= -7d AND assignee = currentUser()

-- This week's deadlines
duedate >= startOfWeek() AND duedate <= endOfWeek()

-- My blocked tickets
issueLinkType = "is blocked by" AND assignee = currentUser()

-- Subtasks of a specific story
parent = "PROJ-123"

-- Watched but not closed
watcher = currentUser() AND status != Closed

-- Full-text search across summary, description, comments
text ~ "error message here"

-- Recent unplanned work
created >= -3d AND assignee = currentUser() AND resolution = Unresolved
```

## Scrum Masters

```jql
-- Unassigned in active sprint
sprint IN openSprints() AND assignee IS EMPTY

-- Zombie tickets (not touched in 30 days)
status NOT IN (Closed, Done) AND updated < -30d

-- Recently completed this sprint
status CHANGED TO Done AFTER startOfWeek()

-- Reopened tickets (quality regression)
status CHANGED FROM Done TO "In Progress"

-- Volatility — new issues created this sprint
sprint IN openSprints() AND created >= -1w

-- Team's in-flight work
assignee in membersOf("Dev Team") AND status = "In Progress"

-- Carried-over issues (current sprint + was in previous)
fixVersion = "Current Sprint" AND fixVersion WAS "Last Sprint"

-- Issues blocked (any)
issueLinkType = "is blocked by"

-- Sprint capacity check
sprint IN openSprints() AND assignee in membersOf("Dev Team")
```

## Product Owners / Managers

```jql
-- Pre-launch readiness
fixVersion = earliestUnreleasedVersion() AND status != Done

-- Firefighting view
priority IN (Critical, Highest) AND resolution = Unresolved

-- Upcoming due dates
duedate >= startOfMonth() AND duedate <= endOfMonth() AND resolution = Unresolved

-- Pending approvals (JSM)
approvals = pending()

-- Epics without stories attached (requires ScriptRunner)
issuetype = Epic AND issueFunction not in hasLinkType("Epic-Story Link")

-- Component-level tech debt
component = "Backend" AND status != Done ORDER BY priority DESC

-- Recently reported bugs by component
issuetype = Bug AND created >= -14d ORDER BY created DESC

-- Cross-project view for portfolio
project in ("Project Mercury", "PTC") AND issuetype in ("Epic", "Task") AND status = "To Do" AND created >= -180d

-- Status-category aggregation
statusCategory = "In Progress" OR statusCategory = "To Do"

-- Feature completeness by version
fixVersion = "v2.0" AND status != Done ORDER BY component, priority
```

## Power Users

```jql
-- Issues where custom cascading select has specific values
location in cascadeOption("USA", "New York")

-- Issues assigned to any admin
assignee in membersOf("jira-administrators")

-- Issues where I was the previous assignee
assignee WAS currentUser()

-- Resolved by current user this year (retrospective)
resolution CHANGED TO "Fixed" BY currentUser() DURING (startOfYear(), endOfYear())

-- Issues updated by specific user in last week
issue in updatedBy(jsmith, "-8d")

-- Issues linked through specific link type
issue in linkedIssues("PROJ-123", "is duplicated by")

-- Issues that were in a specific sprint historically
sprint WAS "Sprint 5"

-- Epics with their children
parentEpic = "PROJ-EPIC-1"

-- Everything that changed status in last 24h
status CHANGED AFTER -1d

-- All subtask issue types
issuetype in subtaskWorkTypes()

-- Issues that breached SLA (JSM)
SLA = breached()
```

## Automation / Admin Queries

```jql
-- Issues from users not in a group (for access reviews)
reporter NOT IN membersOf("internal-users")

-- Issues in projects user has no role in (permission audit)
project NOT IN spacesWhereUserHasRole("Developers")

-- Old unassigned tickets (automation: assign or close)
assignee IS EMPTY AND created < -90d AND resolution = Unresolved

-- Bulk transition candidates
status = "In Progress" AND updated < -14d

-- Stale sprints (automation: warn or move)
sprint IN closedSprints() AND resolution = Unresolved
```
