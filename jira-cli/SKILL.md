---
name: jira-cli
description: >-
  Interact with Atlassian Jira from the terminal: search issues, view
  details, create issues, add comments, list projects, and transition
  status. Use when the user mentions Jira, a ticket key (e.g. PROJ-123),
  or asks about issues, bugs, tasks, projects, or sprint work.
license: MIT
compatibility: Requires JIRA_EMAIL and JIRA_API_TOKEN env vars (free from
  id.atlassian.com/manage/api-tokens), Python 3.8+, and the `requests`
  library. Also requires JIRA_SERVER (defaults to your-domain.atlassian.net).
metadata:
  tags: [jira, atlassian, issue-tracking, project-management, api-client]
  sources:
    - https://developer.atlassian.com/cloud/jira/platform/rest/v3/
    - https://id.atlassian.com/manage/api-tokens
---

# jira-cli — Jira Issue Tracker from the Terminal

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
jira-cli me                                  # your account info
jira-cli me --json                           # machine-readable
```

### list — Search issues

```bash
jira-cli list                                                # recent issues
jira-cli list --project PROJ                                 # by project
jira-cli list --jql 'assignee=currentuser() AND status=Open' # custom JQL
jira-cli list --project PROJ --max 5 --json                  # top 5 as JSON
```

The `--jql` flag accepts any valid JQL. The `--project` flag is a shortcut for `project=KEY`.

### view — Issue details

```bash
jira-cli view PROJ-123                        # full details
jira-cli view PROJ-123 --json                 # machine-readable
```

Shows: summary, type, status, priority, assignee, reporter, timestamps, and description (plain text extracted from Atlassian Document Format).

### projects — List projects

```bash
jira-cli projects                             # all accessible projects
jira-cli projects --json                      # machine-readable
```

### create — Create an issue

```bash
jira-cli create --project PROJ --summary "Fix login bug"            # Task (default)
jira-cli create --project PROJ --summary "Crash on startup" --type Bug
jira-cli create --project PROJ --summary "Add dark mode" --type Story --priority High
jira-cli create --project PROJ --summary "Test" --dry-run           # preview
```

### comment — Add a comment

```bash
jira-cli comment PROJ-123 -m "Fixed in latest build"   # add comment
jira-cli comment PROJ-123 -m "Looking into it" --dry-run
```

### transition — Change issue status

```bash
jira-cli transition PROJ-123 --to "In Progress"         # by name
jira-cli transition PROJ-123 --to "Done"                # by name
jira-cli transition PROJ-123 --to "31"                  # by ID
jira-cli transition PROJ-123 --to "In Review" --dry-run
```

The CLI looks up available transitions for the issue and matches by name or ID. If the transition doesn't exist, it shows available options.

## Global Flags

All flags work in any position:

```bash
jira-cli --json list --project PROJ          # flag before subcommand
jira-cli list --project PROJ --json          # flag after subcommand
jira-cli --dry-run create --project PROJ --summary "Test"  # preview
jira-cli --quiet list                        # suppress non-essential output
```

## Known Gotchas

- **Authentication** uses HTTP Basic Auth with email + API token. This is the email address tied to your Atlassian account, not a username.
- **Atlassian Document Format (ADF)** — Issue descriptions and comments use ADF (JSON structure), not plain text or markdown. The CLI extracts plain text from ADF, but creating issues with rich formatting requires ADF JSON via `--description`.
- **Transitions are workflow-specific** — Available transitions depend on the issue's current status and the project's workflow. The CLI lists available options when an invalid transition is requested.
- **Rate limits** — Jira Cloud has rate limits. The API returns 429 if exceeded. The CLI does not auto-retry.
- **Project keys are case-sensitive** in some contexts, but the Jira API generally accepts uppercase or lowercase.

## References

- [scripts/jira-cli](scripts/jira-cli) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, structured logging.
- [Jira REST API v3 docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) — Official API reference.
- [API Token Management](https://id.atlassian.com/manage/api-tokens) — Generate and revoke tokens.
