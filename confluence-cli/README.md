# Confluence Wiki from the Terminal

Interact with Atlassian Confluence Cloud via the REST API v2. List spaces, browse pages, view content, search with CQL, and create pages.

## Why Install This Skill

When your agent loads this skill, it can **navigate your Confluence documentation** without opening a browser. That means:

- **Find pages across spaces** — list, search, and view content
- **Search with CQL** — complex queries matching Jira-style filtering
- **Create documentation** — create pages from the terminal
- **Retrieve page body content** — extract the full text of any page

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/confluence-cli` | CLI tool for Confluence operations |

## Quick Start

```bash
export CONFLUENCE_EMAIL="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
export CONFLUENCE_SERVER="https://your-domain.atlassian.net"
```

## Triggers

Load this when the user mentions Confluence, a space key (e.g. DEV), or asks about documentation, wiki pages, or knowledge base articles.

## Requirements

Python 3.8+ with `requests`. API token from id.atlassian.com (free, same token as Jira).
