# Trakt — Media Discovery Signals in the Terminal

## Why Install This Skill

Give your agent a reliable way to answer "what is everyone watching?" without confusing a current Trakt discovery ranking with a metadata catalog. The skill covers movies and shows that are trending, broadly popular, or anticipated, and produces JSON that can feed media automation.

Public discovery reads need an application Client ID, not a user login. OAuth boundaries, required headers, pagination, rate-limit behavior, and the difference between Trakt IDs and TMDb metadata are documented so workflows fail clearly instead of silently mixing services.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Command guide, recipes, gotchas, and routing |
| `scripts/trakt` | Executable CLI with JSON and dry-run modes |
| `scripts/test_trakt.py` | Offline pytest and unittest suite, including header injection and pagination |
| `references/auth-and-request-contract.md` | Required headers, OAuth boundary, and errors |
| `references/discovery-endpoints.md` | Trending/popular/anticipated semantics and paging |
| `references/recipes-and-operations.md` | jq pipelines and rate-safe operations |
| `evals/evals.json` | Six representative usage-quality cases |

## Quick Start

```sh
export TRAKT_CLIENT_ID="YOUR_TRAKT_CLIENT_ID"
trakt movie trending --limit 10
trakt --json tv anticipated --page 2 | jq '.pagination'
```

Create a free Client ID at [trakt.tv/oauth/applications](https://trakt.tv/oauth/applications). Preview commands with `trakt --dry-run --json movie popular` without credentials or network access.

## Triggers

Load this skill for Trakt API discovery, trending movies or shows, popular rankings, anticipated releases, watch-signal pipelines, or Trakt pagination and authentication questions. Do not use it for TMDb catalog metadata, credits, images, or provider lookups.

## Requirements

- Python 3.8 or newer
- `requests`
- A Trakt application Client ID in `TRAKT_CLIENT_ID` for live reads
- No OAuth login is needed for the public discovery commands
