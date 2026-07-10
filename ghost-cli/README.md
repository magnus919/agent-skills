# Ghost CMS from the Terminal

Manage content on a Ghost CMS site: view site info, list and create posts and pages, manage tags — all via the Ghost Admin API (v5/v6).

## Why Install This Skill

When your agent loads this skill, it can **manage your Ghost CMS content** without the web editor. That means:

- **List posts and pages** — by status (published, draft, scheduled)
- **Create content** — write and publish blog posts from the terminal
- **Manage tags** — list and browse tags
- **Check site info** — title, URL, description, version

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with setup and examples |
| `scripts/ghost-cli` | CLI tool for Ghost Admin API operations |

## Quick Start

```bash
export GHOST_URL="https://your-ghost-site.com"
export GHOST_ADMIN_KEY="your-id:your-secret"
```

API key from Ghost Admin → Integrations → Create custom integration.

## Triggers

Load this when working with Ghost CMS — managing posts, pages, tags, or checking site configuration.

## Requirements

Python 3.8+ with `requests` library.
