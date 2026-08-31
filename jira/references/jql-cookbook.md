# JQL Cookbook — Role-Based Ready Queries

Fifty ready-to-run JQL queries organized by role. Every query is copy-pasteable; substitute your own project keys, group names, and issue keys. Pairs with [jql-functions-catalog.md](jql-functions-catalog.md) for function semantics and [jql-best-practices.md](jql-best-practices.md) for performance rules.

## Developers (10 queries)

```jql
-- 1. My plate, sorted by urgency
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC
```

```jql
-- 2. Bugs I reported that haven't been fixed
reporter = currentUser() AND status != Done
```

```jql
-- 3. Where I'm mentioned (standup prep)
comment ~ currentUser()
```

```jql
-- 4. My completed work this week
resolution = Fixed AND resolutiondate >= -7d AND assignee = currentUser()
```

```jql
-- 5. This week's deadlines
duedate >= startOfWeek() AND duedate <= endOfWeek()
```

```jql
-- 6. My blocked tickets
issueLinkType = "is blocked by" AND assignee = currentUser()
```

```jql
-- 7. Subtasks of a specific story
parent = "PROJ-123"
```

```jql
-- 8. Watched but not closed
watcher = currentUser() AND status != Closed
```

```jql
-- 9. Full-text search across summary, description, and comments
text ~ "error message here"
```

```jql
-- 10. Recent unplanned work
created >= -3d AND assignee = currentUser() AND resolution = Unresolved
```

## Scrum Masters (9 queries)

```jql
-- 11. Unassigned in active sprint
sprint IN openSprints() AND assignee IS EMPTY
```

```jql
-- 12. Zombie tickets (not touched in 30 days)
status NOT IN (Closed, Done) AND updated < -30d
```

```jql
-- 13. Recently completed this sprint
status CHANGED TO Done AFTER startOfWeek()
```

```jql
-- 14. Reopened tickets (quality regression flag)
status CHANGED FROM Done TO "In Progress"
```

```jql
-- 15. Volatility — new issues created into the current sprint
sprint IN openSprints() AND created >= -1w
```

```jql
-- 16. Team's in-flight work
assignee in membersOf("Dev Team") AND status = "In Progress"
```

```jql
-- 17. Carried-over issues (in current sprint, was in previous)
fixVersion = "Current Sprint" AND fixVersion WAS "Last Sprint"
```

```jql
-- 18. Issues blocked by anything
issueLinkType = "is blocked by"
```

```jql
-- 19. Sprint capacity check
sprint IN openSprints() AND assignee in membersOf("Dev Team")
```

## Product Owners / Managers (10 queries)

```jql
-- 20. Pre-release readiness
fixVersion = earliestUnreleasedVersion() AND status != Done
```

```jql
-- 21. Firefighting view — critical unresolved bugs
priority IN (Critical, Highest) AND resolution = Unresolved
```

```jql
-- 22. Due within the calendar month
duedate >= startOfMonth() AND duedate <= endOfMonth() AND resolution = Unresolved
```

```jql
-- 23. Pending approvals awaiting action (JSM)
approvals = pending()
```

```jql
-- 24. Epics without stories attached (requires ScriptRunner)
issuetype = Epic AND issueFunction not in hasLinkType("Epic-Story Link")
```

```jql
-- 25. Component-level tech debt
component = "Backend" AND status != Done ORDER BY priority DESC
```

```jql
-- 26. Recently reported bugs for triage review
issuetype = Bug AND created >= -14d ORDER BY created DESC
```

```jql
-- 27. Cross-project portfolio view
project in ("Project Mercury", "PTC") AND issuetype in ("Epic", "Task") AND status = "To Do" AND created >= -180d
```

```jql
-- 28. Status-category rollup across workflows
statusCategory = "In Progress" OR statusCategory = "To Do"
```

```jql
-- 29. Feature completeness for a release
fixVersion = "v2.0" AND status != Done ORDER BY component, priority
```

## Power Users (12 queries)

```jql
-- 30. Cascading select matches a specific path
location in cascadeOption("USA", "New York")
```

```jql
-- 31. Issues assigned to any administrator
assignee in membersOf("jira-administrators")
```

```jql
-- 32. Issues where I was the previous assignee
assignee WAS currentUser()
```

```jql
-- 33. Resolved by me this year (retrospective input)
resolution CHANGED TO "Fixed" BY currentUser() DURING (startOfYear(), endOfYear())
```

```jql
-- 34. Issues updated by a specific user in the last week
issue in updatedBy(jsmith, "-8d")
```

```jql
-- 35. Issues linked through a specific link type
issue in linkedIssues("PROJ-123", "is duplicated by")
```

```jql
-- 36. Issues that were in a specific sprint historically
sprint WAS "Sprint 5"
```

```jql
-- 37. Children of an epic
parentEpic = "PROJ-EPIC-1"
```

```jql
-- 38. Everything that changed status in the last 24 hours
status CHANGED AFTER -1d
```

```jql
-- 39. All subtask issue types
issuetype in subtaskWorkTypes()
```

```jql
-- 40. Issues that breached SLA (JSM)
SLA = breached()
```

```jql
-- 41. Approval requests assigned to me as approver (JSM)
approvals = myPendingApproval()
```

## Automation / Admin Queries (9 queries)

```jql
-- 42. Reports from users outside an internal group (access reviews)
reporter NOT IN membersOf("internal-users")
```

```jql
-- 43. Projects where the user holds no Developers role (permission audit)
project NOT IN spacesWhereUserHasRole("Developers")
```

```jql
-- 44. Old unassigned tickets (automation: assign or close)
assignee IS EMPTY AND created < -90d AND resolution = Unresolved
```

```jql
-- 45. Bulk transition candidates (stalled in progress)
status = "In Progress" AND updated < -14d
```

```jql
-- 46. Stale sprints still holding unresolved work (automation: warn or move)
sprint IN closedSprints() AND resolution = Unresolved
```

```jql
-- 47. Approvals decided by a specific user (audit trail, JSM)
approvals = approver(jsmith)
```

```jql
-- 48. SLA clocks at risk of breach soon (JSM monitoring)
SLA != completed() AND SLA <= remaining("-4h")
```

```jql
-- 49. Requests from one customer organization (JSM triage split)
reporter in organizationMembers("YOUR_ORG") AND resolution = Unresolved
```

```jql
-- 50. Backlog hygiene: never-scheduled and long untouched
(sprint IS EMPTY OR sprint NOT IN openSprints()) AND updated < -60d AND resolution = Unresolved
```

Attribution: adapted from the retired jira-jql skill, sourced from Atlassian official documentation and community best practices.

## Sources

- Advanced searching (JQL): https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/
- JQL functions reference: https://support.atlassian.com/jira-software-cloud/docs/jql-functions/
- Search endpoint used to run JQL over REST: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
