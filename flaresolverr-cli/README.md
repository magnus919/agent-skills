# FlareSolverr CLI: Browser-Backed Requests From the Terminal

## Why Install This Skill

Use this skill when an authorized site requires a browser-backed request to handle a Cloudflare or DDoS-GUARD challenge. It gives an agent a small terminal interface for sending GET and POST requests through an existing private FlareSolverr service.

It also provides a readiness probe and browser-session lifecycle commands, without requiring a Python package or raw HTTP request construction. Results are JSON, making them practical to inspect or pass to another tool.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Agent-facing command reference and safe-use guidance. |
| `scripts/flaresolverr-cli` | Dependency-free Python CLI for FlareSolverr's `/v1` API. |

## Quick Start

```sh
# Run FlareSolverr separately, then optionally set its address.
export FLARESOLVERR_SERVER="http://localhost:8191"

# Verify the service is ready.
python3 scripts/flaresolverr-cli health

# Send a browser-backed request.
python3 scripts/flaresolverr-cli get https://example.com
```

`FLARESOLVERR_SERVER` defaults to `http://localhost:8191`. Add `--server URL` for a one-command override or `--timeout SECONDS` to change the 60-second HTTP timeout. Successful commands write JSON to stdout; request failures write JSON to stderr and exit nonzero.

## Triggers

- A Cloudflare or DDoS-GUARD browser challenge blocks an authorized request.
- A workflow needs browser-backed GET or POST requests through an existing FlareSolverr service.
- A workflow needs to check FlareSolverr readiness or create, list, or destroy a session.

## Requirements

Python 3.8+ with no pip dependencies. A running private [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) instance is required. Do not expose that service publicly, and use it only for sites you are authorized to access.
