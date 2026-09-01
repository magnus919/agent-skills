# Jira Issue Tracker from the Terminal

Interact with Atlassian Jira Cloud via the REST API v3: search issues with JQL, view details, create issues, add comments, count matches, list projects, and transition status — plus a full JQL language reference built in.

## Why Install This Skill

When your agent loads this skill, it can **run your entire Jira workflow** without opening a browser:

- **Search anything** — by project, assignee, or arbitrary JQL; results over 50 auto-paginate
- **Count before diving in** — fast approximate counts instead of fetching every ticket
- **Create, comment, edit** — with Atlassian Document Format handled for you
- **Transition safely** — discovers valid workflow transitions per issue before changing status, and can set resolutions in the same call
- **Write better queries** — a 50-query cookbook by role, complete function catalog, performance rules, and history-operator/date-expression deep dives

The skill also knows where the bodies are buried: the legacy-vs-enhanced search endpoint split (offset paging vs `nextPageToken`), transition screens that silently require resolution fields, the `!=` empty-value trap, and rate-limit headers worth honoring.

## What You Get

| Path | Purpose |
|------|---------|
| `SKILL.md` | Command reference: setup, intent-grouped commands, pipeline recipes, jq guidance, known gotchas |
| `scripts/jira` | CLI tool for Jira REST API v3 (`--json`, `--dry-run`, lazy auth) |
| `scripts/test_jira.py` | Offline test suite for the CLI (help/errors/dry-run/mocked client logic) |
| `references/rest-auth-and-search.md` | Auth models, rate limits, error envelopes, search pagination duality |
| `references/rest-issues-and-transitions.md` | Issue CRUD shapes, transitions GET→POST flow, ADF document model |
| `references/jql-functions-catalog.md` | Every JQL function with fields and operators, incl. JSM approvals & SLAs |
| `references/jql-best-practices.md` | Performance rules, precedence, empty-value trap, troubleshooting flows |
| `references/jql-cookbook.md` | 50 ready-to-run JQL queries organized by role |
| `references/jql-history-and-dates.md` | WAS/CHANGED walkthrough, relative-date tables, saved-filter naming |
| `evals/evals.json` | Behavioral eval cases covering read-only use, pipelines, gotchas |

## Quick Start

```bash
export JIRA_EMAIL="you@company.com"
export JIRA_API_TOKEN="YOUR_API_TOKEN"     # free from https://id.atlassian.com/manage/api-tokens
export JIRA_SERVER="https://your-domain.atlassian.net"

jira me                        # verify auth works
jira list --project PROJ       # newest tickets
jira count --jql 'issuetype = Bug AND resolution = Unresolved'
jira create --project PROJ --summary "Test" --dry-run  # preview writes
jira --yes create --project PROJ --summary "Test"      # authorize a write
```

## Triggers

Load this when managing Jira issues, searching or counting tickets, creating bugs, transitioning sprint work, writing/debugging/optimizing JQL, or designing saved filters and dashboards on an Atlassian Jira Cloud site.

## Requirements

- Python 3.8+ with the `requests` library
- A free Atlassian account + API token (`JIRA_EMAIL`, `JIRA_API_TOKEN`; optional `JIRA_SERVER`)
- `jq` recommended for processing `--json` output
