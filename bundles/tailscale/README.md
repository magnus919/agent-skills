# Tailscale / Headscale — Self-Hosted Mesh VPN Bundle

A comprehensive bundle of 7 sub-skills covering the entire self-hosted Tailscale ecosystem using Headscale as the open-source control server. Deploy, configure, and maintain your own WireGuard-based mesh VPN.

## Why Install This Bundle

When your agent loads this bundle, it becomes a **Tailscale/Headscale infrastructure engineer** who can handle the full lifecycle:

- **Deploy Headscale** — install and configure the control server
- **Author tailnet policies** — ACL rules, tag-based access control, user groups
- **Manage node lifecycle** — auth keys, registration, tagging, decommissioning
- **Configure clients** — install and connect Tailscale to your Headscale server
- **Set up routing** — subnet routers and exit nodes
- **Deploy DERP relays** — reliable peer-to-peer connectivity across NATs
- **Backup and migrate** — regular backup and restoration of the control server

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Bundle umbrella — trigger-based auto-loading for 7 sub-skills |
| `skills/` | 7 sub-skills: headscale-deploy, tailnet-policy, headscale-node-lifecycle, tailscale-client, headscale-routing, headscale-derp, headscale-backup |
| `scripts/` | 23 shared scripts with `--json` and `--dry-run` support |
| `references/` | 8 reference documents |
| `templates/` | 6 templates for policy files and configs |

## Quick Start

1. **Deploy Headscale** first — install the control server
2. **Configure tailnet policy** — set up ACLs before opening to users
3. **Manage nodes** — register and tag machines on your tailnet
4. **Install clients** — connect machines to your headscale server

## Triggers

Load this when you hear "Tailscale," "Headscale," "tailnet," "mesh VPN," "WireGuard mesh," or "self-hosted VPN infrastructure."

## Requirements

Bash, Python 3.8+, jq, curl. Access to a Headscale server or the `headscale` CLI. Tailscale client on target machines.
