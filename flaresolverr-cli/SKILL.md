---
name: flaresolverr-cli
description: 'Operate the full flaresolverr-cli command surface: named browser-session
  lifecycle, structured health and service information, dry-run planning, cookie-only
  returns, and challenge-solving GET or form-POST requests. Use for explicit
  flaresolverr-cli or session-management requests; use the smaller flaresolverr skill
  for a one-off health check or basic browser-backed retrieval.'
license: MIT
compatibility: >-
  Python 3.8+ (stdlib only, no pip deps). Requires a running FlareSolverr instance
  (Docker: ghcr.io/flaresolverr/flaresolverr) and the FLARESOLVERR_URL env var set to
  the server address (defaults to http://localhost:8191).
metadata:
  tags: flaresolverr, cloudflare, proxy, anti-bot, headless-browser, selenium, web-scraping
  sources: "https://github.com/FlareSolverr/FlareSolverr, https://hub.docker.com/r/flaresolverr/flaresolverr"
---

# flaresolverr-cli — Cloudflare Bypass Proxy from the Terminal

Drive a FlareSolverr instance from the command line. FlareSolverr is a proxy server that launches a headless Chrome browser to solve Cloudflare and DDoS-GUARD JavaScript challenges, returning the unblocked HTML, cookies, and user-agent to your client.

The CLI wraps all four API endpoints: service info, health check, the three `/v1` session commands (create/list/destroy), and both challenge-solving request commands (`request.get` and `request.post`). Every command supports `--json`, `--dry-run`, and `--timeout`.

## Mutation Gate

`health`, `info`, and `sessions list` are read-only discovery. Creating or destroying a session changes FlareSolverr state, and `request get` or `request post` sends traffic to an external target.

> Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.

Use `--dry-run` to review a planned mutation first. Session destruction and any request intended to change target state require an explicit user directive; this skill does not authorize deletion, privilege changes, authentication bypass, or irreversible cleanup.

## When not to use

Use [flaresolverr](../flaresolverr/SKILL.md) for a one-off health check or basic GET/POST when named sessions, cookie-only returns, dry-run planning, and the full command surface are unnecessary. Do not use either skill to bypass authentication, authorization, paywalls, or access controls.

## Setup

1. Start a FlareSolverr instance (Docker):

```bash
docker run -d --name=flaresolverr -p 8191:8191 \
  ghcr.io/flaresolverr/flaresolverr:latest
```

2. Set the server URL:

```bash
export FLARESOLVERR_URL="http://localhost:8191"
```

`--help` and `--dry-run` work without a running server.

## Essential Commands

### health — Server health check

```bash
flaresolverr-cli health                     # check if server is reachable
flaresolverr-cli health --json              # {"status": "ok"}
```

Calls `GET /health`. Returns `ok` when the server is running. Use as a readiness probe or pre-flight check before session/request commands.

### info — Service information

```bash
flaresolverr-cli info                       # version, user-agent, ready message
flaresolverr-cli info --json                # machine-readable
```

Calls `GET /`. Returns the FlareSolverr version, the Chrome user-agent string, and whether the service is ready to accept requests.

### sessions create — Create a persistent browser session

```bash
flaresolverr-cli sessions create                           # auto-generated session ID
flaresolverr-cli sessions create --session my-session      # custom session name
flaresolverr-cli sessions create --proxy socks5://proxy:1080  # with proxy
```

Creates a long-lived headless browser instance. Reuse the returned session ID in subsequent `request get` / `request post` calls for 10-100x faster requests (no browser startup overhead per call).

### sessions list — List active sessions

```bash
flaresolverr-cli sessions list              # all active session IDs
```

Returns the IDs of every active persistent session. Each session holds a browser process — use this to audit resource usage before creating more.

### sessions destroy — Tear down a session

```bash
flaresolverr-cli sessions destroy --session my-session
```

Closes the browser and frees memory. Always destroy sessions when done — each idle session consumes significant RAM.

### request get — Fetch a URL through the solver

```bash
flaresolverr-cli request get --url https://example.com                        # basic
flaresolverr-cli request get --url https://example.com --session my-session    # reuse session
flaresolverr-cli request get --url https://example.com --return-only-cookies   # cookies only
flaresolverr-cli request get --url https://example.com --timeout 120           # 120s timeout
```

Sends `request.get` to the `/v1` endpoint. FlareSolverr launches Chrome (or reuses a session), navigates to the URL, solves any Cloudflare/DDoS-GUARD challenge, and returns the resolved HTML, cookies, and user-agent.

Flags:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--url` | string | required | Target URL |
| `--session` | string | — | Reuse existing session (faster) |
| `--max-timeout` | int | 60000 | Challenge solve timeout (ms) |
| `--return-only-cookies` | flag | false | Omit HTML from response |
| `--proxy` | string | — | Per-request proxy URL |
| `--wait` | int | 0 | Extra wait after solve (seconds) |

### request post — POST through the solver

```bash
flaresolverr-cli request post --url https://example.com/form --data "a=1&b=2"
```

Same as `request get` but sends an `application/x-www-form-urlencoded` POST body. Accepts the same flags plus `--data` (the form-encoded body string).

## Global Flags

All flags work in any position:

```bash
flaresolverr-cli --json health
flaresolverr-cli --dry-run sessions create --session test
flaresolverr-cli --quiet request get --url https://example.com
flaresolverr-cli --timeout 30 request get --url https://example.com
```

| Flag | Effect |
|------|--------|
| `--json` | Output one JSON value to stdout (all diagnostics go to stderr) |
| `--dry-run` | Print the planned API call without making it |
| `--quiet` | Suppress non-essential output |
| `--timeout N` | HTTP request timeout in seconds (default 60) |

## Known Gotchas

- **No authentication** — FlareSolverr has no built-in auth. Expose it only on localhost or behind a reverse proxy with auth.
- **HTTP 200 for errors** — FlareSolverr always returns HTTP 200. Check the JSON `status` field (`"ok"` vs `"error"`) to determine success.
- **Session proxy precedence** — When a `--session` is provided, any `--proxy` flag is ignored. The session's proxy (set at create time) takes precedence.
- **Memory per session** — Each persistent session runs a full Chrome browser (~200-500 MB RAM). Destroy sessions promptly.
- **First request latency** — A stateless request (no `--session`) pays a browser cold-start cost of 3-10 seconds. Persistent sessions amortize this.
- **POST body format** — `--data` must be `application/x-www-form-urlencoded` format (`key=value&key2=value2`). Multipart and JSON bodies are not supported by FlareSolverr.
- **Selenium status limitation** — The `status` field in responses is always 200 (Selenium does not expose the real HTTP status). Trust the response body, not the status code.

## References

- [Related FlareSolverr CLI](../flaresolverr/scripts/flaresolverr) — Stdlib-only reference implementation for the same API.
- [FlareSolverr GitHub](https://github.com/FlareSolverr/FlareSolverr) — Source, API docs, Docker Compose examples.
- [FlareSolverr Docker Hub](https://hub.docker.com/r/flaresolverr/flaresolverr) — Prebuilt images.
