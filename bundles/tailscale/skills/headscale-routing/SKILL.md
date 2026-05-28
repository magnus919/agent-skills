---
name: headscale-routing
description: Configure subnet routers and exit nodes in a Headscale tailnet to extend mesh access to non-Tailscale devices and route internet traffic. Use when setting up subnet routing for LAN devices or configuring exit nodes for privacy.
category: devops
---

# headscale-routing

## Overview

Subnet routers extend a tailnet to non-Tailscale devices (printers, NAS boxes, IoT
devices) by advertising the local LAN subnet routes through a gateway node. Exit
nodes route all non-tailnet internet traffic through a home server, providing
privacy on untrusted networks (coffee shop Wi-Fi, hotel networks, etc.).

Headscale manages route approval centrally — routes must be advertised by the
gateway node and then approved on the Headscale server before they become active.

## Subnet Router Setup

1. On the gateway node, advertise the LAN subnet:
   ```bash
   tailscale up --advertise-routes=192.168.1.0/24
   ```
2. On the Headscale server, approve the route:
   ```bash
   headscale routes approve -r <route-id>
   ```
3. On client nodes that need to reach the subnet, enable route acceptance:
   ```bash
   tailscale up --accept-routes
   ```

## Exit Node Setup

1. On the exit node, advertise it as an exit node:
   ```bash
   tailscale up --advertise-exit-node
   ```
2. On the Headscale server, approve the exit node route.
3. On the client, select the exit node:
   ```bash
   tailscale set --exit-node=<node-name>
   ```

## Auto-Approvers

Configure Headscale ACL policy to auto-approve routes from trusted nodes:

```json
{
  "autoApprovers": {
    "routes": {
      "192.168.0.0/16": ["tag:gateway"]
    },
    "exitNode": ["tag:gateway"]
  }
}
```

Nodes carrying `tag:gateway` will have their advertised routes or exit-node status
approved automatically without manual intervention.

## Via Filtering

Use `grants.via` in ACL policies to restrict cross-subnet access:

```json
{
  "grants": [
    {
      "src": ["tag:monitoring"],
      "dst": ["tag:servers"],
      "app": ["prometheus"],
      "via": ["192.168.10.0/24"]
    }
  ]
}
```

This ensures traffic from monitoring nodes to servers is routed through the
specified subnet, enabling firewall policies on the gateway to inspect or filter
traffic.

## SNAT on Subnet Routers

By default, Headscale enables Source NAT (SNAT) on subnet router traffic. This
means traffic originating from tailnet clients destined for the advertised subnet
appears to come from the gateway node's IP. To disable SNAT:

```bash
tailscale up --advertise-routes=192.168.1.0/24 --snat-subnet-routes=false
```

Disable SNAT when the downstream network needs to see the original client IP for
logging, ACLs, or per-device firewall rules.

## List / Approve / Reject Routes on Headscale

```bash
# List all routes with status
headscale routes list

# Approve a specific route
headscale routes approve -r <route-id>

# Approve all routes from a node
headscale routes approve --all -n <node-name>

# Reject a route
headscale routes reject -r <route-id>
```

## Gotchas

- **Stable gateway required**: Subnet routes need a gateway node that stays online.
  If the gateway goes down, the route becomes unavailable.
- **`--accept-routes` on clients**: Clients will NOT use advertised subnet routes
  unless they themselves run with `--accept-routes` or have it in their up flags.
- **IPv4-only by default**: Tailscale subnet routing is IPv4-only unless you
  explicitly configure dual-stack (IPv4 + IPv6).
- **Overlapping subnets**: If two nodes advertise overlapping subnets, routing
  behavior is undefined. Use distinct, non-overlapping CIDRs.
- **Headscale API required for scripting**: The `headscale routes` CLI commands
  above require shell access to the Headscale server. For remote management, use
  the Headscale REST API with `$HEADSCALE_URL` and `$HEADSCALE_API_KEY`.

## Environment

| Variable            | Description                          |
|---------------------|--------------------------------------|
| `HEADSCALE_URL`     | Headscale server URL                 |
| `HEADSCALE_API_KEY` | API key from `headscale apikeys create` |

## Trigger Conditions

- "subnet router"
- "exit node"
- "advertise route"
- "approve route"
- "route traffic"
- "subnet routing"
- "exit node setup"

## Scripts

Refer to individual script help (`--help`) for usage details:

| Script                  | Description                                       |
|-------------------------|---------------------------------------------------|
| `hs-advertise-routes.sh`| Advertise subnet routes on a Tailscale node       |
| `hs-approve-routes.sh`  | List and approve/reject routes on Headscale       |
| `hs-list-routes.sh`     | List all routes with detailed status              |
