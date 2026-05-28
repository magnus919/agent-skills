---
name: headscale-derp
description: Configure and manage DERP relay servers for Tailscale/Headscale — embedded and standalone DERP deployment, latency testing, and connectivity diagnostics. Use when direct peer connections fail, traffic is routed through DERP relays, or setting up custom relay regions.
category: devops
---

# headscale-derp Skill

## Overview

**DERP** = **D**esignated **E**ncrypted **R**elay **P**rotocol. DERP is Tailscale's TURN-like fallback mechanism used when direct peer-to-peer NAT traversal fails. Traffic through DERP is fully encrypted (WireGuard inside TLS), but it routes through a relay server rather than directly between peers, so it introduces additional latency.

Common scenarios where DERP is used:

- **Symmetric NAT** — Both peers behind symmetric NAT gateways
- **Corporate firewalls** — Restrictive egress policies that block UDP/STUN
- **Double NAT** — Carrier-grade NAT on both sides
- **Blocked STUN** — UDP port 3478 is filtered

## DERP in Headscale

Headscale includes an **embedded DERP server** that is enabled by default in the `config.yaml`:

```yaml
derp:
  server:
    enabled: true
    region_id: 999
    region_code: "headscale"
    region_name: "Headscale Embedded DERP"
    stun_listen_addr: "0.0.0.0:3478"
    private_key_path: "/var/lib/headscale/derp_server_private.key"
```

The embedded server runs a STUN endpoint on port 3478 and relays on port 443 (or whatever port Headscale listens on). It's suitable for small tailnets (under ~50 nodes).

### Key config options

| Option | Default | Description |
|--------|---------|-------------|
| `derp.server.enabled` | `true` | Enable the embedded DERP server |
| `derp.server.region_id` | `999` | Numeric region identifier (must be unique across all regions) |
| `derp.urls` | `[]` | Additional DERP map URLs (for standalone servers) |
| `derp.paths` | `[]` | Local DERP map JSON file paths |
| `derp.auto_update` | `true` | Automatically fetch Tailscale's default DERP map |
| `derp.stun_listen_addr` | `0.0.0.0:3478` | STUN listener address |

## DERP Map

A DERP map is a JSON structure that defines relay regions and nodes. Example:

```json
{
  "Regions": {
    "900": {
      "RegionID": 900,
      "RegionCode": "us-nyc",
      "RegionName": "New York",
      "Nodes": [
        {
          "Name": "900a",
          "RegionID": 900,
          "HostName": "derp-nyc.example.com",
          "DERPPort": 443,
          "STUNPort": 3478,
          "STUNOnly": false
        }
      ]
    }
  }
}
```

The DERP map can be served via HTTPS URL (put in `derp.urls`) or as a local JSON file (put in `derp.paths`).

## Connectivity Testing

Run `tailscale netcheck` to see which DERP regions are reachable and their latency:

```
$ tailscale netcheck
Report:
    * UDP: true
    * IPv4: yes
    * IPv6: no
    * MappingVariesByDestIP: true
    * HairPinning: false
    * PortMapping: UPnP
    * Nearest DERP: Dallas
    * DERP latency:
        - dallas: 18ms (dallas)
        - us-west: 35ms (us-west)
        - new-york-city: 5ms (new-york-city)
        - london: 85ms (london)
```

## Standalone DERP

For larger tailnets or dedicated relay capacity, run a standalone DERP server using the official `tailscale/derper` Docker image:

```bash
docker run -d \
  --name=derper \
  --restart=always \
  -p 3478:3478/udp \
  -p 443:443 \
  -v /etc/letsencrypt:/certs \
  -v /var/lib/derper:/var/lib/derper \
  tailscale/derper \
  --hostname=derp.example.com
```

## TLS Certificates

DERP requires TLS. Recommended approaches:

1. **Let's Encrypt (auto)** — `tailscale/derper` supports automatic certificate issuance via Let's Encrypt. It listens on port 80 for the ACME HTTP-01 challenge.
2. **Manual certs** — Pass `--cert=/path/to/cert.pem --key=/path/to/key.pem` to the `derper` binary.
3. **Reverse proxy** — Terminate TLS at a reverse proxy (nginx, Caddy, Traefik) and forward to the local DERP port.

## Region Selection

Tailscale clients automatically select the DERP region with the lowest latency. The selection algorithm:

1. Sends STUN requests to all configured DERP regions
2. Measures round-trip time for each
3. Picks the region with the lowest latency
4. Falls back to the next-closest region if connectivity fails

## Gotchas

- **DERP is encrypted but slower** — All DERP traffic is WireGuard-inside-TLS, adding ~5-15ms overhead. Direct connections are always preferred.
- **Embedded DERP works for small tailnets** — The embedded server in Headscale uses the same Headscale process for relaying. Under heavy relay traffic, it can impact Headscale control-plane performance. For >50 nodes doing active relay, deploy a standalone DERP.
- **All traffic routes through DERP if STUN is blocked** — If UDP port 3478 is blocked anywhere in the network path, Tailscale cannot establish direct peer-to-peer connections and will route ALL traffic through the nearest DERP relay.
- **Port 3478 (STUN) and 443 (DERP) must be open** — STUN uses UDP for NAT traversal probing; DERP uses TCP/TLS for relay traffic. Both must be reachable from clients.
- **Multiple regions improve resilience** — Deploy DERP relays in at least two geographically diverse locations so clients have a fallback.
- **DERP map caching** — Clients cache the DERP map. If you add a new region, it can take up to 5 minutes for clients to pick it up. Use `tailscale netcheck` to force a refresh.

## Trigger Conditions

This skill is activated by keywords: `DERP`, `relay`, `peer relay`, `STUN`, `direct connection failed`
