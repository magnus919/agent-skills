---
name: tailscale-client
description: Install, configure, and troubleshoot the official Tailscale client when connected to a Headscale self-hosted control server. Use when connecting a new device, diagnosing connectivity, checking peer status, or troubleshooting DERP relay issues.
category: devops
---

# tailscale-client

## Overview

Tailscale is a WireGuard-based mesh VPN that connects devices into a secure
tailnet. When used with [Headscale](https://github.com/juanfont/headscale), a
self-hosted open-source control server, the official Tailscale client connects
via the `--login-server` flag instead of Tailscale's SaaS control plane.

This skill covers client-side installation, authentication, diagnostics, and
troubleshooting.

### Architecture

```
[Client A] ───── WireGuard ───── [Client B]
      │                               │
      └──────── Headscale URL ────────┘
                  (control/
                 coordination)
```

The Tailscale client (the `tailscaled` daemon) registers with the Headscale
control server, exchanges WireGuard keys, and establishes direct peer-to-peer
encrypted connections. When direct NAT traversal fails, traffic falls back
through DERP (Detour Encrypted Relay Protocol) relays.

## Installation

Install the official Tailscale client on the target device:

| Platform | Command |
|----------|---------|
| **Debian/Ubuntu** | `curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list && sudo apt-get update && sudo apt-get install tailscale` |
| **macOS** | `brew install tailscale` |
| **Windows** | `choco install tailscale` |
| **Fedora/RHEL** | `sudo dnf install dnf-plugins-core && sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo && sudo dnf install tailscale` |
| **Alpine** | `apk add tailscale` |

See `ts-install.sh` for automated detection and installation.

## Connection

After installation, authenticate with your Headscale server:

```bash
sudo tailscale up --login-server=https://headscale.example.com
```

This opens a browser for web-based authentication OR prints an auth URL at the
terminal. For non-interactive (scripted) setups, use a pre-authentication key:

```bash
sudo tailscale up \
  --login-server=https://headscale.example.com \
  --authkey=tskey-auth-xxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

See `ts-up.sh` for a wrapper with env-var defaults.

## Authentication

### Web Auth

The default `tailscale up` flow prints a URL (e.g. `https://headscale.example.com/register/nodekey:xxxxx`).
Visit this URL in a browser (or pass it to the Headscale admin to approve).

### Pre-Auth Keys

Generate on the Headscale server:

```bash
headscale preauthkeys create --user myuser
```

Use the key with `--authkey` as shown above. Keys can be tagged for
service/auth nodes that don't belong to a specific user:

```bash
headscale preauthkeys create --user myuser --tags tag:ci-runner,tag:monitoring
```

Then on the client:

```bash
sudo tailscale up \
  --login-server=https://headscale.example.com \
  --authkey=tskey-auth-xxxxx \
  --advertise-tags=tag:ci-runner
```

## Diagnostics

| Command | Purpose |
|---------|---------|
| `tailscale status --json` | List all peers and their connection state |
| `tailscale ping --verbose -c 3 <peer>` | Test direct vs. relay path to a peer |
| `tailscale netcheck` | Check NAT type and DERP relay connectivity |
| `tailscale version` | Client and daemon version info |
| `tailscale debug` | Low-level debugging (derp-map, metrics, goroutines) |

Run `ts-diagnostics.sh` for a comprehensive connectivity bundle that collects
all of the above into a structured JSON output. Use
`ts-connectivity-report.py` to interpret the diagnostics and produce a
human-readable or structured report.

## Features

| Feature | Headscale Support | Notes |
|---------|-------------------|-------|
| **MagicDNS** | ✅ Supported | `--accept-dns` must be passed to `tailscale up` |
| **Taildrop / Taildrive** | ✅ Supported | File sharing between peers |
| **Tailscale SSH** | ✅ Supported | `--ssh` flag on `tailscale up` |
| **Serve** | ✅ Supported | Expose local services via tailnet |
| **Funnel** | ❌ Not supported | Funnel requires Tailscale's SaaS control plane |
| **Exit Nodes** | ✅ Supported | Advertise with `--advertise-exit-node`, use with `--exit-node` |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `HEADSCALE_URL` | Default `--login-server` URL for `ts-up.sh` |
| `TAILSCALE_AUTHKEY` | Default `--authkey` for `ts-up.sh` |

## Gotchas

- **Port conflicts (8080, 8443)**: Tailscale Serve often uses 8080 or 8443.
  Check for conflicts with `lsof -i :8080`.
- **Subnet overlap**: If the tailnet subnets overlap with local networks,
  routes may not work. Review advertised routes carefully.
- **DERP-only fallback**: When NAT traversal fails, peers connect via DERP
  relays only. Latency increases significantly. Check with
  `ts-diagnostics.sh` or `tailscale status --json` and look for
  `"relay":"..."` instead of `"txBytes"/"rxBytes"` on the direct path.
- **tailscaled not running**: The daemon must be started before `tailscale`
  CLI commands work. On systemd systems: `sudo systemctl start tailscaled`.
  On macOS: open the Tailscale GUI app or run `sudo tailscaled`.
- **DNS resolution**: MagicDNS requires `--accept-dns` on `tailscale up`.
  Without it, nodes are only reachable by their Tailscale IP (100.x.x.x).
- **Key expiry**: Node keys expire by default. Use `--force-reauth` or
  re-run `tailscale up` to re-authenticate. Pre-auth keys can be created
  with `--expiry=false` for non-expiring (long-lived) nodes.

## Trigger Conditions

This skill should be loaded when the user mentions any of the following:

- Installing or setting up Tailscale client on any platform
- Connecting a device to a Headscale server
- Tailscale authentication issues (auth key, web auth, node approval)
- Checking tailscale status, ping, or connectivity
- DERP relay problems or NAT traversal failures
- Tailscale SSH, Serve, MagicDNS, or Taildrop configuration
- Troubleshooting "tailscaled not running" or "no connection"
- Interpreting `tailscale status`, `tailscale ping`, or `tailscale netcheck` output
