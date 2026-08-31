# Transistor.fm — Podcast Hosting from the Terminal

Manage your Transistor.fm podcast account over its official API: browse
shows and episodes, publish episodes, pull download analytics, and run
private-podcast subscriber lists — all from the terminal.

## Why Install This Skill

When your agent loads this skill, it can **operate your Transistor.fm
podcast hosting** without the dashboard, including the part no other tool
gives an agent: the full episode publish lifecycle.

- **Publish episodes end to end** — create a draft, attach audio (URL or
  authorized local-file upload), then publish or schedule it through
  Transistor's dedicated publish endpoint
- **Browse your catalog** — shows, episodes, drafts, season/number
  metadata, with JSON:API compound documents unwrapped for jq
- **Track downloads** — per-day analytics windows for shows and episodes,
  summed and ready for reports
- **Run private podcasts** — list, add (single or batch), and revoke
  subscribers; register webhooks so you push instead of poll
- **Stay under the rate limit** — dry-run request plans and clear 429
  guidance (Transistor allows 10 requests per 10 seconds)

## What You Get

| Path | Purpose |
|------|---------|
| `SKILL.md` | Command reference, publish-lifecycle recipe, jq guidance, gotchas |
| `scripts/transistor` | Bundled Python CLI for the Transistor.fm v1 API (read + write commands) |
| `scripts/test_transistor.py` | Offline mocked test suite (canned JSON:API documents, zero network) |
| `references/auth-and-basics.md` | API-key auth, JSON:API envelope and jq patterns, pagination, errors |
| `references/endpoint-catalog.md` | Every endpoint's method, path, and parameters |
| `references/episode-publish-lifecycle.md` | Draft → audio → publish/schedule/unpublish, exact request shapes |
| `references/gotchas-and-recipes.md` | Symptom → cause → fix guide plus multi-step workflows |

## Quick Start

```bash
export TRANSISTOR_API_KEY="<API_KEY>"   # Dashboard -> Account -> API Access

transistor user                          # verify the key
transistor shows                         # list your podcasts
transistor episodes --status draft       # what is not out yet?

# Publish pipeline: create (draft) -> attach audio -> publish
EP=$(transistor episode-create --show <SHOW_ID> --title "Ep 12" \
     --audio-url "https://example.com/ep12.mp3" --json | jq -r '.id')
transistor episode-publish --id "$EP"
```

`--help` and `--dry-run` work without an API key; preview any request with
`transistor --dry-run episode-publish --id 123`.

## Triggers

Load this skill when the user mentions Transistor or Transistor.fm, podcast
hosting, publishing a podcast episode, scheduling or unpublishing episodes,
podcast download analytics, or private podcast subscribers.

## Requirements

Python 3.8+ with `requests`, plus a Transistor.fm API key (Account page →
API Access). The key carries your dashboard role per podcast; treat it like
a password. No other services or credentials are involved.
