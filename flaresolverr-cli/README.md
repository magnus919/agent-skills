# Cloudflare Bypass Proxy from the Terminal

Drive a FlareSolverr instance from the command line. FlareSolverr is an open-source proxy server that launches a headless Chrome browser to solve Cloudflare and DDoS-GUARD JavaScript challenges, returning the unblocked HTML and cookies to your client.

## Why Install This Skill

When your agent loads this skill, it can **interact with any FlareSolverr proxy server** without writing raw HTTP requests. That means:

- **Check server health** — verify the FlareSolverr instance is running and ready before sending traffic
- **Manage browser sessions** — create, list, and destroy persistent headless Chrome sessions for fast, stateful scraping
- **Solve Cloudflare challenges** — fetch pages behind Cloudflare and DDoS-GUARD protection with a single command, getting back unblocked HTML, cookies, and user-agent strings
- **Structured output** — every command supports `--json` for piping into scripts and `--dry-run` for previewing API calls before making them

FlareSolverr is widely used in the *arr ecosystem (Prowlarr, Jackett) and by anyone who needs reliable access to Cloudflare-protected sites. This CLI makes it first-class for agent workflows.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with flag tables, examples, and gotchas |
| `scripts/flaresolverr-cli` | Single-file Python CLI (stdlib only, zero pip dependencies) |
| `tests/test_cli.py` | Deterministic smoke tests covering all commands in dry-run mode |

## Quick Start

```bash
# Start FlareSolverr (one-time setup)
docker run -d --name=flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest

# Point the CLI at it
export FLARESOLVERR_URL="http://localhost:8191"

# Verify it works
./scripts/flaresolverr-cli health
./scripts/flaresolverr-cli info
```

## Triggers

Load this when the user mentions FlareSolverr, Cloudflare bypass, anti-bot proxy, headless browser proxy, or needs to fetch a page behind Cloudflare or DDoS-GUARD protection.

## Requirements

Python 3.8+ (stdlib only, no pip installs needed). A running [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance (Docker: `ghcr.io/flaresolverr/flaresolverr`). Set `FLARESOLVERR_URL` to the server address (defaults to `http://localhost:8191`).
