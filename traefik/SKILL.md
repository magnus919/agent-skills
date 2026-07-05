---
name: traefik
description: >-
  Deploy, configure, and troubleshoot Traefik v3 reverse proxy — covers all
  providers, routing, TLS/ACME, middlewares, and production patterns with
  YAML examples. Load when setting up or debugging a Traefik instance.
license: MIT
version: 0.1.0
compatibility: >-
  Compatible with any agent supporting the Agent Skills format (Hermes Agent,
  Claude Code, GitHub Copilot, OpenCode, Cursor, etc.)
metadata:
  source: https://doc.traefik.io/traefik/
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

## When NOT to Use This Skill

- For Traefik Hub, Traefik Enterprise, or Traefik Mesh — these are separate products with different APIs
- For developing Traefik plugins (Yaegi or WASM) — this skill covers *using* configured plugins, not writing them. See https://plugins.traefik.io/create for plugin development.
