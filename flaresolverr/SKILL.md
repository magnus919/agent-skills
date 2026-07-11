---
name: flaresolverr
description: Use FlareSolverr through a small CLI when a site requires a browser-backed request to pass Cloudflare or DDoS-GUARD challenges.
---

# FlareSolverr

Use this skill when ordinary HTTP retrieval is blocked by a browser challenge. FlareSolverr must already be running; this skill does not bypass authentication or authorize access to restricted content.

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
