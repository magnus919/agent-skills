# Jira Issue Tracker from the Terminal

Interact with Atlassian Jira Cloud via the REST API v3. Search issues, view details, create issues, add comments, list projects, and transition status.

## Why Install This Skill

When your agent loads this skill, it can **manage your entire Jira workflow** without opening a browser. That means:

- **Search issues by project, JQL, or assignee** — find anything in your tracker
- **View full issue details** — description, status, assignee, comments
- **Create and update issues** — new tasks, bugs, stories from the terminal
- **Add comments** — update threads without the web UI
- **Transition status** — move tickets through workflows
- **List projects** — see what's available

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with setup and examples |
| `scripts/jira-cli` | CLI tool for Jira REST API v3 |

## Quick Start

```bash
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_SERVER="https://your-domain.atlassian.net"
```

API token from id.atlassian.com (free).

## Triggers

Load this when managing Jira issues, searching tickets, creating bugs, or tracking project work.

## Requirements

Python 3.8+ with `requests` library.
