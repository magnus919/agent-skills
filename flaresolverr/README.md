# FlareSolverr

Use a browser-backed proxy from the terminal when a site rejects ordinary HTTP clients with a Cloudflare or DDoS-GUARD challenge.

## What you get

| Path | Purpose |
|---|---|
| `SKILL.md` | Agent routing and safe usage |
| `scripts/flaresolverr` | Dependency-free JSON CLI |
| `scripts/test-flaresolverr.sh` | Deterministic dry-run smoke checks |

## Quick start

```sh
python3 scripts/flaresolverr health
python3 scripts/flaresolverr get https://example.com
```

Set `FLARESOLVERR_SERVER` or pass `--server`. The default is `http://localhost:8191`. Keep the service private.

## Triggers

- Cloudflare or DDoS-GUARD browser challenges
- A site that requires cookie-preserving browser requests
- FlareSolverr session management from an agent workflow

## Requirements

Python 3.9+ and a running FlareSolverr service. No Python packages are required.
