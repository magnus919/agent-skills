# Traefik v3 — Reverse Proxy & Load Balancer

Deploy, configure, secure, and maintain Traefik v3 reverse proxy. Covers Docker provider, routing, TLS/ACME, middlewares, observability, and production deployment.

## Why Install This Skill

When your agent loads this skill, it becomes a **Traefik infrastructure engineer** who can:

- **Deploy Traefik** — production-ready Docker Compose setup with Let's Encrypt
- **Configure routing** — HTTP/TCP/UDP routers with Docker labels or file-based config
- **Set up TLS** — ACME with HTTP-01, DNS-01, and TLS-ALPN-01 challenges
- **Use all 25+ middlewares** — rate limiting, authentication, redirects, headers, circuit breakers
- **Monitor and observe** — Prometheus/OpenTelemetry metrics, access logs, dashboard
- **Harden deployment** — security best practices, production patterns

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Quick-start deployment, core concepts, reference index |
| `templates/` | Production-ready Docker Compose template |
| `scripts/` | Health check script with JSON output |
| `references/` | 10 reference files: static config, dynamic config, all providers, routing, TLS/ACME, middlewares, observability, production, TCP/UDP, troubleshooting |

## Triggers

Load this when setting up or debugging a Traefik instance for reverse proxy, load balancing, or TLS termination.

## Requirements

Docker for containerized deployment. Standard Linux server for native installation.
