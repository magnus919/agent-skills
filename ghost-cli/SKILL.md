---
name: ghost-cli
description: Manage Ghost CMS content from the terminal — create and list posts, pages,
  and tags, and fetch site info via the Ghost Admin API (v5/v6). Use when the user
  asks about ghost, cms, blog, blogging, posts, pages, tags, publishing, or site configuration.
license: MIT
compatibility: Requires GHOST_URL and GHOST_ADMIN_KEY env vars. Admin key in "id:secret"
  format from Ghost Admin → Integrations. Python 3.8+ and the `requests` library.
metadata:
  tags: ghost, cms, blog, blogging, post, page, tag, ghost-cms, content-management,
    api-client
  sources: https://ghost.org/docs/admin-api/, https://ghost.org/docs/
---

# ghost-cli — Ghost CMS from the Terminal

Manage content on a Ghost CMS site: view site info, list and create posts and pages, manage tags — all via the Ghost Admin API (v5/v6).

## Setup

1. Get your Admin API key from **Ghost Admin → Settings → Advanced → Integrations** (or **Ghost Admin → Integrations**). Create a custom integration to get a key in `id:secret` format.
2. Set these environment variables:

```bash
export GHOST_URL="https://your-ghost-site.com"     # your Ghost site URL
export GHOST_ADMIN_KEY="your-id:your-secret"        # from Ghost Admin → Integrations
```

`--help` and `--dry-run` work without credentials (lazy auth).

## Essential Commands

### site — Get site information

```bash
ghost-cli site                               # show site title, URL, description
ghost-cli --json site                        # machine-readable JSON
ghost-cli --dry-run site                     # preview without API call
```

Shows: site title, URL, description.

### posts — List blog posts

```bash
ghost-cli posts                              # 20 most recent posts
ghost-cli posts --limit 50                   # more results
ghost-cli posts --status published           # only published posts
ghost-cli posts --status draft               # only draft posts
ghost-cli posts --status scheduled           # only scheduled posts
ghost-cli posts --limit 10 --json            # 10 most recent as JSON
```

Shows: title, status, slug, and last-updated date for each post.

### create-post — Create a new blog post

```bash
ghost-cli create-post --title "My First Post"                               # draft, no HTML
ghost-cli create-post --title "Hello World" --html "<p>Hello!</p>"          # with HTML content
ghost-cli create-post --title "Ready" --html "<p>Published</p>" --status published  # publish immediately
ghost-cli create-post --title "Scheduled" --html "<p>Later</p>" --status scheduled  # schedule
ghost-cli create-post --title "Custom Slug" --slug "my-custom-url"          # custom URL slug
ghost-cli create-post --title "Draft" --dry-run                             # preview without creating
```

Creates the post and returns its title, slug, and status.

### pages — List pages

```bash
ghost-cli pages                              # 20 most recent pages
ghost-cli pages --limit 50                   # more results
ghost-cli pages --json                       # machine-readable JSON
```

Shows: title, status, slug, and last-updated date for each page.

### tags — List tags

```bash
ghost-cli tags                               # 50 tags with post counts
ghost-cli tags --limit 100                   # more results
ghost-cli tags --json                        # machine-readable JSON
```

Shows: tag name, slug, and number of posts using each tag.

## Global Flags

These flags work anywhere in the command — before or after the subcommand:

```bash
ghost-cli --json posts                       # JSON output
ghost-cli posts --json                       # same result, after subcommand
ghost-cli --dry-run create-post --title "Test"  # preview without API call
ghost-cli --quiet posts                      # suppress diagnostic output
ghost-cli --verbose site                     # verbose logging
```

| Flag | Effect |
|------|--------|
| `--json` | Output machine-readable JSON instead of human-readable text |
| `--dry-run` | Show what API call would be made without executing it |
| `--quiet` | Suppress non-essential diagnostic output |
| `--verbose` | Enable verbose/debug logging |

## Known Gotchas

- **Admin API key format** — The `GHOST_ADMIN_KEY` must be in `id:secret` format (e.g. `644a4c1a2b3c4d5e6f7g8h9i:abcd1234efgh5678ijkl9012`). This is the format Ghost generates when you create a Custom Integration. A plain token or JWT will not work.
- **JWT token auto-generated** — The CLI generates a short-lived JWT (HS256, 5-minute expiry) internally from the Admin API key on each request. You don't need to create or manage JWT tokens yourself.
- **5-minute JWT window** — Each JWT is valid for 300 seconds (5 minutes). If your system clock is significantly skewed, requests may fail. Ensure NTP is synced.
- **API version v6** — The CLI sends `Accept-Version: v6.0` on all requests, targeting the Ghost Admin API v6. Response shapes follow the v6 spec. May also work against v5 sites.
- **HTML content format** — Post and page content must be provided as raw HTML strings via `--html`. Markdown is not auto-converted. If you write in Markdown, convert it to HTML first (e.g. with a markdown-to-html tool).
- **No update or delete commands** — The current CLI supports listing and creating posts/pages/tags, but does not include update or delete operations. Use the Ghost Admin UI or direct API calls for those.
- **No tag creation via CLI** — Tag listing works, but `create-tag` is not exposed as a subcommand. The GhostClient class has a `create_tag` method internally but it is not wired to a CLI command.
- **Rate limiting** — Ghost Admin API enforces rate limits. For heavy operations, stagger your requests.
- **Error output** — API errors (4xx/5xx) include the response body in the error message for debugging. Auth errors (401/403) explicitly tell you to check `GHOST_ADMIN_KEY`.

## References

- [scripts/ghost-cli](scripts/ghost-cli) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, structured logging.
- [Ghost Admin API Docs](https://ghost.org/docs/admin-api/) — Official Ghost Admin API documentation.
- [Ghost Integrations](https://ghost.org/docs/integrations/) — How to create Custom Integrations and get your Admin API key.
