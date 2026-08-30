# Ghost CMS content management from the terminal

Let your agent browse, draft, publish, and schedule content on a Ghost blog or newsletter site through the Admin API — no web editor required.

## Why Install This Skill

Editing a Ghost site usually means clicking through the admin UI. This skill hands your agent direct, scripted control instead:

- **See the whole editorial state** — published posts, plus the drafts and scheduled queue that public site feeds never show.
- **Publish programmatically** — create posts and pages as drafts, then flip them live after review, with safe collision-checked updates.
- **Schedule content** — stage posts to appear at future times.
- **Keep tags tidy** — list tags with usage counts, add new ones, drive exports.

It speaks Ghost's exact authentication dialect automatically: your Admin API key (`id:secret`) becomes a fresh short-lived signed JWT for every command, so there are no tokens to mint, rotate, or paste anywhere.

Not to be confused with Ghost's official npm `ghost-cli` tool, which installs and operates Ghost servers (`ghost install`, nginx/SSL setup, upgrades). This skill manages *content* on an already-running site; that one manages *servers*.

## What You Get

| Path | Purpose |
|------|---------|
| `SKILL.md` | Command reference: setup, browse/create/publish recipes, gotchas |
| `scripts/ghost` | CLI tool covering site info, post/page/tag operations, JSON + dry-run modes |
| `scripts/test_ghost.py` | Offline test suite for the CLI (all network mocked) |
| `references/admin-auth-and-basics.md` | Full JWT signing walkthrough with auth error signatures |
| `references/content-vs-admin-api.md` | Content vs Admin API choice guide and draft-visibility trap |
| `references/posts-pages-tags-endpoints.md` | Endpoint map, pagination loop patterns, error envelope |
| `references/worked-recipes.md` | Copy-paste workflows: draft→publish, exports, scheduling |
| `references/gotchas-field-guide.md` | Symptom-first troubleshooting for common failures |

## Quick Start

```bash
export GHOST_URL="https://your-ghost-site.com"
export GHOST_ADMIN_KEY="<RECORD_KEY>"    # Ghost Admin → Integrations → Custom integration

ghost site                # connectivity check
ghost posts --status draft
ghost create-post --title "Hello from the terminal" --html "<p>First!</p>"
```

Preview any write safely by adding `--dry-run` before the subcommand.

## Triggers

Load this skill when working with Ghost CMS content: listing posts/pages/tags, drafting or publishing blog content, scheduling posts, exporting site content, fixing Ghost API authentication errors, or investigating why drafts don't show up in a Ghost site feed.

## Requirements

- Python 3.8+ with the `requests` library.
- A running Ghost 5.x/6.x site where you can create a Custom Integration (Ghost Admin → Settings → Integrations).
- The integration's **Admin API Key** exported as `GHOST_ADMIN_KEY`, plus the site URL as `GHOST_URL`. Keep the key server-side; it signs mutations and must never ship in client code or CI logs.
