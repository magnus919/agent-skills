# Notion — Read and Edit Notion from the Terminal

Operate Notion without leaving your terminal or your agent's tool loop: retrieve pages, query databases, search across the workspace, and make confirmed property updates.

## Why Install This Skill

Teams run their operational memory in Notion — runbooks, on-call docs, product trackers, decision logs — and agents have had no bounded way to read it. This skill gives your agent a real read path (page retrieval, database queries, search) and a safe write path: creating a page or updating a property is a guarded mutation that requires a preview and an explicit confirmation, so the agent can answer questions from Notion without ever silently editing shared content.

It ships `notion-cli`, a small Python script that speaks the Notion API with no third-party dependencies. Reads are capped (`--limit`), output is clean JSON for the agent or readable text for you, and `--help` works with no token and no network. The script sends the standard `Notion-Version` header and summarizes pages as title + ID + URL instead of dumping raw block trees.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating contract, mutation gates, and verification boundaries |
| `references/` | Dated source index and an API operations reference (endpoints, pagination, property types, filters, errors) |
| `scripts/notion-cli` | Bounded, stdlib-only CLI: pages get/create/update, databases query, search; `--json`, `--limit`, mutations gated by `--dry-run`/`--yes` |
| `tests/` | 13 deterministic tests against a stub Notion API, covering the mutation gate and read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no token and no network
notion/scripts/notion-cli --help

# Find a page by text (bounded)
NOTION_TOKEN=secret_... notion/scripts/notion-cli --json search query --query "on-call runbook"

# Retrieve one page
NOTION_TOKEN=secret_... notion/scripts/notion-cli --json pages get --page-id <page-id>

# Query a database, capped at 10 rows
NOTION_TOKEN=secret_... notion/scripts/notion-cli --json --limit 10 databases query --database-id <db-id>

# Update a page property: preview first, then confirm
printf '{"Status": {"select": {"name": "Done"}}}' > props.json
NOTION_TOKEN=secret_... notion/scripts/notion-cli pages update --page-id <page-id> --properties props.json --dry-run
NOTION_TOKEN=secret_... notion/scripts/notion-cli pages update --page-id <page-id> --properties props.json --yes
```

## Triggers

Load this skill for `notion` operations: "what does the runbook say", reading pages, querying a Notion database (rows, filters), searching pages and databases, creating a page row, or updating a page property with confirmation. Do not load it for building Notion integrations or apps, workspace administration, or other knowledge bases like Confluence.

## Requirements

- Python 3.9+ for `notion-cli` (stdlib only; `--help` needs nothing else).
- A Notion integration token (`NOTION_TOKEN`, `secret_...`) with the workspace pages/databases you need **shared with the integration**. Search and database access require the corresponding capabilities in the integration settings.
- Network access to `api.notion.com` for live reads and writes. Optionally set `NOTION_VERSION` to pin the API version (default `2022-06-28`).
