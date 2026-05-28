---
name: headscale-deploy
description: Deploy, configure, and maintain a self-hosted Headscale control server on Linux or Docker. Use when setting up a new Headscale instance, troubleshooting deployment issues, or configuring server settings.
license: MIT
compatibility: linux, docker
metadata:
  tags:
    - headscale
    - tailscale
    - wireguard
    - vpn
    - deployment
    - devops
  spec-version: 1.0
---

# headscale-deploy

## Overview

Headscale is an open-source, self-hosted implementation of the Tailscale control server. It allows you to run your own coordination plane for WireGuard-based mesh networking, giving you full control over your tailnet without relying on Tailscale's SaaS infrastructure. The Tailscale client connects to Headscale transparently — no client modifications needed.

Use this skill to deploy Headscale from scratch, configure server settings, manage DERP relay infrastructure, and diagnose deployment issues.

## Prerequisites

- **Linux server** (x86_64 or aarch64) or **Docker host** with compose support
- **DNS record** pointing to the server (A/AAAA record for `server_url`)
- **Ports 80/443** accessible from the internet (or your tailnet's ingress point)
- **Port 3478/udp** for STUN (optional, needed for NAT traversal)
- Root or sudo access on the target machine

## Deployment Methods

### Docker Compose (Recommended)

The fastest and most maintainable approach. Use `install-headscale.sh` with `--docker` flag to generate a compose file and systemd drop-in, or create manually:

```yaml
version: "3.9"
services:
  headscale:
    image: headscale/headscale:latest
    container_name: headscale
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "3478:3478/udp"
    volumes:
      - ./data:/var/lib/headscale
      - ./config:/etc/headscale
    command: headscale serve
```

### Binary Install

Direct binary installation on the host for lightweight or container-free environments. The `install-headscale.sh` script handles:

1. Detecting platform (linux/amd64, linux/arm64)
2. Downloading the release tarball from GitHub
3. Installing the binary to `/usr/local/bin`
4. Creating the `headscale` system user
5. Writing a systemd unit file
6. Creating default config at `/etc/headscale/config.yaml`

## Configuration

Key `config.yaml` options:

| Option | Description | Example |
|---|---|---|
| `server_url` | Public URL of your Headscale instance | `https://headscale.example.com:443` |
| `listen_addr` | Local bind address | `0.0.0.0:8080` |
| `metrics_listen_addr` | Prometheus metrics endpoint | `127.0.0.1:9090` |
| `dns_config.base_domain` | MagicDNS domain suffix | `example.com` |
| `dns_config.magic_dns` | Enable MagicDNS | `true` |
| `derp.server.enabled` | Enable embedded DERP relay | `false` |
| `derp.server.region_id` | Numeric region ID | `999` |
| `derp.server.region_name` | Human-readable region name | `"my-headscale"` |
| `derp.urls` | External DERP map URLs | `[]` |
| `db_type` | Database backend: `sqlite3` or `postgres` | `sqlite3` |
| `tls_letsencrypt_hostname` | Auto TLS via Let's Encrypt | `""` |
| `tls_cert_path` / `tls_key_path` | Manual TLS cert paths | `""` |

## Verification

After deployment, verify the instance is healthy:

```bash
# Quick health check
curl -s https://headscale.example.com/health

# Comprehensive diagnostics
headscale-health-check.sh --json

# Check registered nodes
headscale nodes list

# Verify API access
headscale apikeys list
```

## Gotchas

- **SQLite vs PostgreSQL**: SQLite is fine for small tailnets (<100 nodes). For larger deployments or high-availability, use PostgreSQL. Plan your choice upfront — migration is non-trivial.
- **TLS certificate management**: Let's Encrypt auto-provisioning is convenient but requires port 80 to be accessible for the HTTP-01 challenge. Use a reverse proxy (Caddy, Nginx, Traefik) for more flexibility.
- **Port conflicts**: If port 8080 or 3478 is already in use, change `listen_addr` in config. Ensure no other service binds port 3478/udp for STUN.
- **DERP configuration**: The embedded DERP relay works for small deployments. For production, set up dedicated DERP nodes to avoid single-region bottlenecks.
- **Configuration reload**: Headscale does not hot-reload config. Restart the service after config changes: `systemctl restart headscale` or `docker compose restart`.
- **Database backups**: Always back up `/var/lib/headscale/db.sqlite3` (or your PostgreSQL DB) regularly.

## Trigger Conditions

Use this skill when the user says any of:
- "deploy headscale"
- "install headscale"
- "setup headscale server"
- "headscale config"
- "headscale configuration"
- "headscale deployment"
- "headscale health"
- "headscale derp"
- "self-hosted tailscale"
- "tailscale control server"
