---
name: traefik
description: Deploy, configure, and troubleshoot Traefik v3 reverse proxy — covers
  all providers, routing, TLS/ACME, middlewares, and production patterns with YAML
  examples. Load when setting up or debugging a Traefik instance.
license: MIT
compatibility: Compatible with any agent supporting the Agent Skills format (Hermes
  Agent, Claude Code, GitHub Copilot, OpenCode, Cursor, etc.)
metadata:
  source: https://doc.traefik.io/traefik/
  version: 0.1.0
---

# Traefik Agent Skill

Comprehensive reference for deploying, configuring, and maintaining **Traefik v3** as a reverse proxy and load balancer. This skill covers every major feature of Traefik Proxy OSS with production-ready YAML configuration examples.

## Quick Start — Minimal Docker Deployment

A production-ready Docker Compose template is available at `templates/docker-compose.yml`. For a quick test:

### One-Line Health Check

```bash
bash scripts/traefik-healthcheck.sh           # Text output
bash scripts/traefik-healthcheck.sh --json    # JSON output for agents
```

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.7
    command:
      # Static configuration via CLI args
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--api.dashboard=true"
      - "--api.insecure=false"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    labels:
      # Dashboard router
      - "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$10$$..."
```

## Core Concepts

Traefik has two configuration layers:
- **Static configuration** — set at startup via YAML file, CLI args, or env vars. Defines entryPoints, providers, API, metrics, TLS resolvers.
- **Dynamic (routing) configuration** — changes at runtime. Defined via providers (Docker labels, File provider YAML, Kubernetes CRDs).

The request flow: `EntryPoint → Router → (Middlewares) → Service → Backend`

## Reference Files

| Topic | Load When | File |
|-------|-----------|------|
| **Static Config** | Setting up Traefik for the first time, adding entryPoints, providers, or global settings | `references/static-configuration.md` |
| **Docker Provider** | Labeling containers for routing, configuring multiple networks, port detection | `references/docker-provider.md` |
| **HTTP Routing** | Writing Host/Path matchers, understanding priority, rule syntax | `references/http-routing.md` |
| **Middleware Catalog** | Adding auth, rate limiting, header manipulation, path rewriting, error pages | `references/middleware-catalog.md` |
| **TLS & ACME** | Configuring Let's Encrypt, wildcard certs, DNS-01/HTTP-01 challenges, mTLS | `references/tls-acme.md` |
| **TCP & UDP Routing** | Routing non-HTTP traffic, SNI matching, TLS termination for TCP | `references/tcp-routing.md` |
| **API & Dashboard** | Securing the dashboard, API endpoints, debugging routes | `references/api-dashboard.md` |
| **Observability** | Prometheus/OTel metrics, access logs, tracing, health checks | `references/observability.md` |
| **v2→v3 Migration** | Breaking changes, rule syntax update, deprecated options | `references/migration-v2-to-v3.md` |
| **Production Patterns** | Docker Compose template, security hardening, HA, monitoring | `references/production-deployment.md` |
| **Servers Transport** | Backend connection config, mTLS to backends, connection pooling, SPIFFE | `references/servers-transport.md` |
| **Kubernetes Providers** | Deploying Traefik in K8s — Ingress, CRD (IngressRoute), Gateway API | `references/kubernetes-providers.md` |
| **Other Providers** | ECS, Nomad, Consul Catalog, KV stores, File, HTTP, REST providers | `references/other-providers.md` |
| **Community Patterns** | Production wisdom — middleware ordering, performance tuning, CDN real-IP, CrowdSec, Authelia, troubleshooting | `references/community-patterns.md` |
| **Operational Audit** | Full-stack audit methodology — surface inventory, config review, runtime state, log analysis, classification framework | `references/operational-audit.md` |
| **Plugins & Extending** | Yaegi and WASM plugins, plugin configuration, FastProxy | `references/plugins-extend.md` |

## Common Pitfalls

- **Traefik connecting to wrong port:** By default uses the first exposed port. Always set `traefik.http.services.<name>.loadbalancer.server.port=XXXX`
- **Labels are case-insensitive** but resource names should be consistent within a compose file
- **`@` character** is NOT allowed in router, service, or middleware names
- **Dashboard not showing routes:** Ensure API is enabled (`api.dashboard: true`) and you're using `service=api@internal`
- **ACME certificates not generating:** Check that the ACME challenge entryPoint is reachable from the internet (port 80 for HTTP-01, port 443 for TLS-ALPN-01)
- **Docker networking:** If containers are on multiple networks, set `traefik.docker.network=<name>` to pick the correct one
- **exposedByDefault=false** means NO container gets routes unless it has `traefik.enable=true` label
- **Middleware order matters:** The order in the `middlewares` list is the order of execution
- **File provider path:** When using `providers.file.directory`, Traefik watches for `.yml`/`.yaml`/`.toml` files and merges them alphabetically
- **Log level:** Use `DEBUG` only for troubleshooting — it's extremely verbose in production
- **Single quotes in rules** are NOT accepted — use backticks ` or escaped double quotes `\"`
- **`traefik healthcheck` requires ping entryPoint:** The `traefik healthcheck` CLI command (and `docker exec traefik traefik healthcheck`) returns "please enable `ping` to use health check" unless a `ping` entryPoint is configured in static config. To validate config syntax without ping, use `python3 -c "import yaml; yaml.safe_load(open('config.yml'))"` for YAML files, or check the runtime API at `http://localhost:8080/api/rawdata` (if insecure API is enabled) for live config state.
- **Named Docker volumes require `docker cp`:** When Traefik's config lives on a named Docker volume (not a bind mount), you cannot edit files directly on the host. Use `docker cp <src> traefik:/etc/traefik/<dest>` to push files into the container and `docker cp traefik:/etc/traefik/<src> <dest>` to pull. Static config changes (traefik.yml) require a container restart; dynamic config changes (dynamic/*.yml) are picked up live via the file provider watcher.
- **Entrypoint-level middleware + router-level declaration = double execution:** When an entryPoint applies a middleware (e.g., `http.middlewares: [default@file]`) and a router ALSO declares the same middleware, the middleware executes twice. Symptoms: doubled rate-limit counts, wasted CPU on duplicate compression, confusing debug logs. **Diagnose:** query the runtime API (`/api/rawdata`) and check the router's `middlewares` array for duplicates. **Fix:** remove the middleware from router-level declarations — the entryPoint already covers it. Services that need EXACTLY the entryPoint middleware (no additions) can omit the `middlewares` field entirely.
- **YAML parse error drops entire file provider:** When a single file in `providers.file.directory` has a YAML parse error, Traefik discards the ENTIRE provider's configuration — every middleware, router, and service from all files in that directory disappears. The tell: a burst of `"middleware X does not exist"` errors at the same timestamp across every router. Python's `yaml.safe_load()` is not a sufficient validator — Traefik's parser can reject files that pass Python's parser (e.g., subtle indentation differences, trailing whitespace, or template-variable-like strings). **Recovery:** immediately restore the last-known-good file from backup (`docker cp /tmp/backup.yml traefik:/etc/traefik/dynamic/config.yml`). **Prevention:** always snapshot configs before editing, deploy dynamic config changes incrementally (one logical change → verify with smoke test → then next change), and keep a backup of every file you touch.
- **Rate limiting breaks SPA page loads (429 Too Many Requests):** Modern SPAs fire 50–100+ JS chunk requests on initial page load. A rate limit of 400 req/s will 429 these requests, producing a black browser window. **Diagnose:** `docker logs traefik | grep "429" | grep "/assets/"` — if you see many 429s on JS/CSS assets within a single second, the rate limit is too low. **Fix:** raise limits. 1000 avg / 1500 burst (rate limit) and 100 concurrent (inFlightReq) are reasonable for homelab deployments with heavy web UIs. Note that entrypoint-applied middleware cannot be overridden per-service — if different services need different limits, you must either raise the global limit or move middleware from entrypoint to per-router application.

## When NOT to Use This Skill

- For Traefik Hub, Traefik Enterprise, or Traefik Mesh — these are separate products with different APIs
- For developing Traefik plugins (Yaegi or WASM) — this skill covers *using* configured plugins, not writing them. See https://plugins.traefik.io/create for plugin development.
