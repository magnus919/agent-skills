---
name: jira
description: 'Interact with Atlassian Jira from the terminal: search issues with
  JQL, view details, create issues, add comments, list projects, and transition
  status. Includes a full JQL language reference (functions, operators, history
  queries, performance tuning). Use when the user mentions Jira, a ticket key
  (e.g. PROJ-123), asks about issues, bugs, tasks, projects, or sprint work,
  or needs to write, debug, or optimize JQL queries. Do not use for GitHub or
  GitLab issue tracking, Jira site administration, or generic ticketing systems.'
license: MIT
compatibility: Requires JIRA_EMAIL and JIRA_API_TOKEN env vars (free from id.atlassian.com/manage/api-tokens),
  Python 3.8+, and the `requests` library. Also requires JIRA_SERVER (defaults to
  your-domain.atlassian.net).
metadata:
  tags: jira, atlassian, issue-tracking, project-management, api-client
  sources: https://developer.atlassian.com/cloud/jira/platform/rest/v3/, https://id.atlassian.com/manage/api-tokens
---

# jira — Jira Issue Tracker from the Terminal

Interact with Atlassian Jira Cloud via the REST API v3. Search issues, view details, create issues, add comments, list projects, and transition status.

## Setup

1. Generate an API token at [id.atlassian.com/manage/api-tokens](https://id.atlassian.com/manage/api-tokens)
2. Set environment variables:

```bash
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_SERVER="https://your-domain.atlassian.net"  # defaults to this format
```

`--help` and `--dry-run` work without credentials.

## Essential Commands

### me — Current user profile

```bash
jira me                                  # your account info
jira me --json                           # machine-readable
```

### list — Search issues

```bash
jira list                                                # recent issues
jira list --project PROJ                                 # by project
jira list --jql 'assignee=currentuser() AND status=Open' # custom JQL
jira list --project PROJ --max 5 --json                  # top 5 as JSON
```

The `--jql` flag accepts any valid JQL. The `--project` flag is a shortcut for `project=KEY`.

### view — Issue details

```bash
jira view PROJ-123                        # full details
jira view PROJ-123 --json                 # machine-readable
```

Shows: summary, type, status, priority, assignee, reporter, timestamps, and description (plain text extracted from Atlassian Document Format).

### projects — List projects

```bash
jira projects                             # all accessible projects
jira projects --json                      # machine-readable
```

### create — Create an issue

```bash
jira create --project PROJ --summary "Fix login bug"            # Task (default)
jira create --project PROJ --summary "Crash on startup" --type Bug
jira create --project PROJ --summary "Add dark mode" --type Story --priority High
jira create --project PROJ --summary "Test" --dry-run           # preview
```

### comment — Add a comment

```bash
jira comment PROJ-123 -m "Fixed in latest build"   # add comment
jira comment PROJ-123 -m "Looking into it" --dry-run
```

### transition — Change issue status

```bash
jira transition PROJ-123 --to "In Progress"         # by name
jira transition PROJ-123 --to "Done"                # by name
jira transition PROJ-123 --to "31"                  # by ID
jira transition PROJ-123 --to "In Review" --dry-run
```

The CLI looks up available transitions for the issue and matches by name or ID. If the transition doesn't exist, it shows available options.

## Global Flags

All flags work in any position:

```bash
jira --json list --project PROJ          # flag before subcommand
jira list --project PROJ --json          # flag after subcommand
jira --dry-run create --project PROJ --summary "Test"  # preview
jira --quiet list                        # suppress non-essential output
```

## Known Gotchas

- **Authentication** uses HTTP Basic Auth with email + API token. This is the email address tied to your Atlassian account, not a username.
- **Atlassian Document Format (ADF)** — Issue descriptions and comments use ADF (JSON structure), not plain text or markdown. The CLI extracts plain text from ADF, but creating issues with rich formatting requires ADF JSON via `--description`.
- **Transitions are workflow-specific** — Available transitions depend on the issue's current status and the project's workflow. The CLI lists available options when an invalid transition is requested.
- **Rate limits** — Jira Cloud has rate limits. The API returns 429 if exceeded. The CLI does not auto-retry.
- **Project keys are case-sensitive** in some contexts, but the Jira API generally accepts uppercase or lowercase.

### JQL gotchas

- **`!=` excludes empty values** — `assignee != currentUser()` silently drops unassigned issues. Write `(assignee != currentUser() OR assignee IS EMPTY)` to include them.
- **AND binds tighter than OR** — `A OR B AND C` parses as `A OR (B AND C)`. Always parenthesize OR groups.
- **No leading wildcards** — `summary ~ "*bug"` forces a full scan and is very slow; put wildcards after the first few characters.
- **Filter by project first** — the single biggest JQL performance lever on large instances.
- **JQL has no aggregation** — no COUNT/SUM/AVG in the query language itself.
- **History operators need history tracking** — `WAS`/`CHANGED` return nothing for custom fields without history enabled.
- **Search endpoint duality** — this CLI uses the classic `/rest/api/3/search` endpoint with offset pagination (`startAt`, `maxResults`). Atlassian's enhanced `/rest/api/3/search/jql` replaces it with a `nextPageToken` model and no offset; the classic endpoint is being deprecated, so expect migration. Mixing the two pagination models is a common source of truncated or erroring result pages.

## Multi-Step Pipeline Recipes

### Sprint hygiene sweep

Find stalled sprint work, then bulk-review each ticket:

```bash
jira list --jql 'sprint IN openSprints() AND updated < -14d AND status != Done' --json \
  | jq -r '.issues[].key' \
  | while read -r key; do jira view "$key"; done
```

The `--json` output shape from `list` is `{"total": N, "issues": [{"key", "summary", "status", "assignee", "issuetype", "priority"}]}` — pipe through `jq -r '.issues[].key'` to feed follow-up commands.

### My-week digest

```bash
jira list --jql 'assignee = currentUser() AND updated >= startOfWeek()' --max 50 --json \
  | jq -r '.issues[] | "\(.key)\t\(.status)\t\(.summary)"'
```

More ready-to-run queries live in [references/jql-cookbook.md](references/jql-cookbook.md), organized by role (developers, scrum masters, product owners, admins).

## Reference Files

| File | Topic | Read when |
|------|-------|-----------|
| [references/jql-functions-catalog.md](references/jql-functions-catalog.md) | Every JQL function with fields/operators — date/time, user, sprint/version, issue, custom field, plus JSM approval and SLA functions | Writing or debugging a query that uses functions; checking which operators a function supports |
| [references/jql-best-practices.md](references/jql-best-practices.md) | Performance rules, operator precedence, the empty-value trap, common mistakes, troubleshooting flow, marketplace extensions | A query is slow, returns wrong/zero results, or mixes AND/OR |
| [references/jql-cookbook.md](references/jql-cookbook.md) | 50 ready-to-run JQL queries organized by role (developers, scrum masters, product owners/managers, power users, admins) | Building dashboards, saved filters, automation rules, or sprint reviews |

## References

- [scripts/jira](scripts/jira) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, structured logging.
- [Jira REST API v3 docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) — Official API reference.
- [API Token Management](https://id.atlassian.com/manage/api-tokens) — Generate and revoke tokens.

## When not to use

Do not use this skill for GitHub or GitLab issue tracking (each platform has its own tooling), for Jira site administration such as project permissions, workflow schemes, or user management, or for writing application code against the Jira REST API — see the Atlassian developer docs for integration development instead.
