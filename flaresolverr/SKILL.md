---
name: flaresolverr
description: Use the minimal FlareSolverr wrapper for a one-off health check or browser-backed GET/POST when ordinary retrieval is blocked by Cloudflare or DDoS-GUARD. Choose flaresolverr-cli instead for named session lifecycle, cookie-only returns, dry-run planning, or the full operational command surface.
---

# FlareSolverr

## Quick Start

```sh
python3 scripts/flaresolverr --server http://localhost:8191 health
```

Use this skill when ordinary HTTP retrieval is blocked by a browser challenge. FlareSolverr must already be running; this skill does not bypass authentication or authorize access to restricted content.

## When not to use

Use [flaresolverr-cli](../flaresolverr-cli/SKILL.md) when the task names that CLI, requires creating/listing/destroying named sessions, needs cookie-only responses or dry-run planning, or needs the full operational command surface. Keep this skill for the smaller one-off health, GET, or POST path.

## Mutation Gate

The health command is read-only discovery. GET and POST send traffic to an external target, and POST may change target state.

> Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.

A POST or any request intended to change target state requires an explicit user directive. This skill does not authorize deletion, privilege changes, authentication bypass, or irreversible cleanup.

## CLI

```text
python3 flaresolverr/scripts/flaresolverr --server http://localhost:8191 health
python3 flaresolverr/scripts/flaresolverr --server http://localhost:8191 get https://example.com
python3 flaresolverr/scripts/flaresolverr session create
python3 flaresolverr/scripts/flaresolverr session list
python3 flaresolverr/scripts/flaresolverr session destroy SESSION_ID
```

Every command emits JSON. `get` and `post` use FlareSolverr's `/v1` API and preserve the returned status, URL, headers, and response body. Use `--timeout` to bound a request and `--session` when a site needs cookie continuity.

## Setup

Run FlareSolverr separately, commonly with Docker:

```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    ports: ["8191:8191"]
    environment:
      LOG_LEVEL: info
```

Do not expose the service publicly. Prefer a pinned image tag in production and use the vendor's documentation for browser and platform compatibility.
