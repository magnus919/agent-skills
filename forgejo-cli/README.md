# Forgejo / Gitea CLI — Self-Hosted Git Forge

Manage issues, pull requests, repositories, labels, webhooks, and Actions runners on a self-hosted Forgejo or Gitea instance — all from the terminal.

## Why Install This Skill

When your agent loads this skill, it can **manage your entire self-hosted Git forge** without a browser. That means:

- **List, create, and search repositories** — manage your code hosting
- **Handle issues** — list, show, create, comment, label, assign
- **Manage pull requests** — list, diff, review, comment, merge with branch protection
- **Configure webhooks** — list, create, delete
- **Manage labels** — list and create custom labels

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with authentication setup and examples |
| `scripts/forgejo-cli` | Python CLI tool |

## Quick Start

Two token profiles in `~/.hermes/.env`:
- `FORGEJO_AGENT_TOKEN` — for automated operations (default)
- `FORGEJO_USER_TOKEN` — for user-level operations (`--user` flag)

## Triggers

Load this when dealing with Forgejo, Gitea, self-hosted git forges, or any repository management on your own infrastructure.

## Requirements

Python 3.8+ with `requests` library. Self-hosted Forgejo or Gitea instance.
