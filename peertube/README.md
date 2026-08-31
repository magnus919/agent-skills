# PeerTube — Federated Video from the Terminal

Browse any PeerTube instance from the command line: latest videos, video detail, comment
threads, channels and accounts, instance stats, and OAuth2 login for your own account —
plus fediverse-wide search through SepiaSearch.

## Why Install This Skill

When your agent loads this skill, it can **navigate the federated video universe** without
a browser. That means:

- **Browse any instance** — latest videos with real offset pagination (the API has no
  `page` parameter, and most naive wrappers get this wrong)
- **Search the right scope** — instance-local search or the whole fediverse via
  SepiaSearch, with the `searchTarget` semantics documented instead of guessed
- **Inspect videos deeply** — full metadata, comment threads (the hyphenated
  `/comment-threads` route), channels, and accounts by handle (`name@host`)
- **Check instance health** — name, description, and user/video/view counters composed
  from `/config/about` + `/server/stats` anonymously
- **Authenticate safely** — OAuth2 password grant with per-instance, owner-only token
  persistence, automatic refresh, and proper server-side revocation on logout
- **Avoid the traps** — masked `client_secret` responses, token lifetimes that vary per
  instance, 2FA `x-peertube-otp`, rate-limit headers, RFC7807 error bodies

Every command is read-only except `login`/`logout`, and `--dry-run` previews any request
without touching the network.

## What You Get

| Path | Purpose |
|------|---------|
| `SKILL.md` | Complete command reference with setup, gotchas, and recipes |
| `scripts/peertube` | CLI for PeerTube API operations (`--json`, `--dry-run`, `--verbose`) |
| `scripts/test_peertube.py` | Offline test suite (all HTTP mocked, zero egress) |
| `references/auth-and-tokens.md` | The full OAuth2 flow, secret masking, token hygiene |
| `references/search-and-discovery.md` | Instance-local vs SepiaSearch search scopes |
| `references/endpoint-catalog.md` | Endpoint-by-endpoint parameters and response shapes |
| `references/gotchas-field-guide.md` | Failure signatures and version drift |
| `references/worked-recipes.md` | Multi-step CLI/jq and curl workflows |
| `evals/evals.json` | Behavioral eval cases including negative triggers |

## Quick Start

```bash
export PEERTUBE_SERVER="https://<INSTANCE_HOST>"   # any PeerTube instance
scripts/peertube server                            # instance stats, anonymous
scripts/peertube videos --limit 5 --json
scripts/peertube search --query "linux"            # searches THIS instance
```

Fediverse-wide search through SepiaSearch (same API shape, wider index):

```bash
PEERTUBE_SERVER="https://sepiasearch.org" scripts/peertube search --query "linux"
```

Optional login for your own account commands:

```bash
scripts/peertube login --username "<USERNAME>" --prompt
scripts/peertube me --json | jq '.role.label'
scripts/peertube logout                            # revokes server-side + deletes token file
```

## Triggers

Load this when asking about PeerTube, federated video, decentralized video platforms,
SepiaSearch, browsing a specific PeerTube instance's videos or channels, or PeerTube API
authentication.

## Requirements

Python 3.8+ with `requests`. One thing this skill always needs from you: **an instance
host** — export `PEERTUBE_SERVER` (e.g. `https://<INSTANCE_HOST>`) or pass
`--server https://...` per command, since PeerTube is federated and every command targets
one instance. Reads are anonymous; `me`/`my-videos` need a token from `scripts/peertube
login`. Tokens persist to `~/.config/peertube/token.json` (override the directory with
`PEERTUBE_CONFIG_DIR`). Find public instances at [joinpeertube.org](https://joinpeertube.org).
