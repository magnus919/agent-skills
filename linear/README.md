# Linear: focused issue and document operations from the terminal

## Why Install This Skill

Give an agent a small, predictable way to work with Linear without running an MCP server or
installing a package. It can find teams, projects, cycles, and issues, inspect documents, and
make carefully previewed issue changes through Linear's public API.

The CLI stays intentionally narrow: it favors bounded reads, JSON output (compact with `--json`,
indented without it), and dry-run previews over a large API mirror. That makes routine
project-management work easier to audit.

## What You Get

| Path | Provides |
|---|---|
| `scripts/linear` | Dependency-free Python CLI for Linear GraphQL reads and issue mutations |
| `SKILL.md` | Agent workflow, safety gate, command routing, and official API links |
| `tests/test_linear.py` | Offline tests for parsing, safety gates, GraphQL contracts, and dry-run behavior |
| `references/` | Linear workflow, GraphQL, integration-boundary, and source guidance |

## Quick Start

Set one credential for live API calls. Use a placeholder, never a real token in documentation or shell history.

```bash
export LINEAR_API_KEY='your-linear-personal-api-key'
# Or: export LINEAR_ACCESS_TOKEN='your-oauth-access-token'

linear/scripts/linear team list --limit 20 --json
linear/scripts/linear issue search "customer import" --json
```

Preview a write before confirming it:

```bash
linear/scripts/linear issue create --team ENG --title "Review import errors" --dry-run --json
```

## Triggers

- List, search, inspect, create, update, move, or comment on Linear issues
- Find Linear teams, projects, cycles, or documents
- Run a small, explicit Linear GraphQL query from a terminal

## Requirements

- Python 3.8 or later; no third-party packages
- Network access for live API calls
- `LINEAR_API_KEY` or `LINEAR_ACCESS_TOKEN` for live API calls
- A Linear workspace and credentials with permission for the requested action
