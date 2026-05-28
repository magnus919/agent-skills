---
name: tailscale
description: >-
  Self-hosted Tailscale/Headscale ecosystem: deploy and manage a Headscale control server,
  configure tailscale clients, manage ACL policies, node lifecycle, subnet routing, DERP relays,
  and backup/migration. Use when the user mentions Tailscale, Headscale, tailnet, mesh VPN,
  WireGuard mesh, or self-hosted VPN infrastructure.
license: MIT
compatibility: Requires bash, Python 3.8+, jq, curl, and access to a Headscale server or
  the `headscale` CLI. Tailscale client (`tailscale`) must be installed on target machines.
metadata:
  tags: [tailscale, headscale, vpn, wireguard, mesh, networking, homelab]
  spec-version: "1.0"
---

# Tailscale + Headscale Skill Bundle

This umbrella skill covers the self-hosted Tailscale ecosystem using [Headscale](https://headscale.net)
as the open-source control server. It provides 7 sub-skills that are auto-loaded by context.

## Auto-Loading by Context

When the user's message matches a trigger keyword, the corresponding sub-skill's SKILL.md
is loaded. Multiple sub-skills can load together when triggers overlap.

| Trigger Keywords | Sub-Skill(s) Loaded |
|---|---|
| "deploy headscale", "install headscale", "setup headscale server", "headscale config" | `headscale-deploy` |
| "ACL", "policy file", "tailnet policy", "access control", "grant", "tag owners" | `tailnet-policy` |
| "install tailscale", "connect to headscale", "tailscale client", "tailscale up", "tailscale status", "diagnose tailscale", "connectivity" | `tailscale-client` |
| "auth key", "preauthkey", "register node", "approve node", "tag node", "node list", "decommission node" | `headscale-node-lifecycle` |
| "subnet router", "exit node", "advertise route", "approve route" | `headscale-routing` |
| "DERP", "relay", "peer relay", "STUN" | `headscale-derp` |
| "backup headscale", "restore headscale", "migrate headscale", "headscale backup" | `headscale-backup` |
| "Tailscale", "Headscale", "tailnet", "mesh VPN", "WireGuard mesh", "self-hosted VPN" | Loads this umbrella SKILL.md for navigation |

## Sub-Skill Ordering & Dependencies

```
headscale-deploy ─────┬──> tailnet-policy ───> headscale-routing
                       │
                       ├──> headscale-node-lifecycle
                       │
                       ├──> tailscale-client
                       │
                       ├──> headscale-derp
                       │
                       └──> headscale-backup (prerequisite: a running headscale instance)
```

- **headscale-deploy** must be completed first — the others require a running Headscale server
- **tailnet-policy** (configures ACLs) is recommended before opening the tailnet to other users
- **headscale-derp** is optional but recommended for reliability across NATs
- **headscale-backup** should be run regularly on any production deployment

## Root Scripts (Shared Utilities)

These live in `scripts/` at the bundle root and are available to all sub-skills:

- `scripts/headscale-health-check.sh` — Probe Headscale server version, node count, DB integrity
- `scripts/headscale-backup.sh` — Full backup (sqlite + config + policy + certs)
- `scripts/headscale-restore.sh` — Restore from backup archive
- `scripts/tailscale-status-json.sh` — Structured `tailscale status --json` wrapper
- `scripts/test-all.sh` — Smoke test across all sub-skills

## Templates

Templates live in `templates/` and cover common deployment patterns:

- `templates/docker-compose-headscale.yaml` — Headscale + embedded DERP + Traefik TLS
- `templates/headscale-config.yaml` — Annotated full headscale configuration
- `templates/policy-allow-all.json` — Minimal allow-all policy
- `templates/policy-deny-all.json` — Locked-down deny-all policy
- `templates/policy-tagged-segmented.json` — Tag-based access model
- `templates/derp-map.json` — Custom DERP relay map

## Environment Variables

| Variable | Used By | Purpose |
|---|---|---|
| `HEADSCALE_URL` | All | Headscale server URL (e.g. `https://headscale.example.com`) |
| `HEADSCALE_API_KEY` | All | Headscale API key (created via `headscale apikeys create`) |
| `TAILSCALE_AUTHKEY` | tailscale-client | Pre-authenticated key for non-interactive client setup |

## Use the CLI tools

All scripts use `--json`, `--dry-run`, and have informative `--help` output.
Scripts relative to bundle root: `scripts/<tool>` or `skills/<sub-skill>/scripts/<tool>`.

See the individual sub-skill SKILL.md for detailed usage.
