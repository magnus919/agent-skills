# DERP Architecture — Designated Encrypted Relay Protocol

## What DERP Is

DERP (Designated Encrypted Relay Protocol) is Tailscale's fallback relay mechanism.
When two nodes can't connect directly (NAT traversal failure), traffic is relayed
through a DERP server. DERP is end-to-end encrypted — the relay sees encrypted
WireGuard packets, not plaintext.

## When DERP Is Used

Direct connections fail in these scenarios:
- **Symmetric NAT** — Both sides behind symmetric NAT that STUN can't punch through
- **Corporate firewalls** — Outbound-only access, no inbound ports
- **Double NAT** — Carrier-grade NAT (CGNAT) on mobile/LTE connections
- **Cone NAT + Symmetric** — Mixed NAT types that can't negotiate

## DERP vs Direct

| Characteristic | Direct (P2P) | DERP Relay |
|---|---|---|
| Latency | Minimal | Higher (extra hop) |
| Bandwidth | Direct link | Limited by relay |
| CPU usage | Low | Higher (relay overhead) |
| Reliability | Depends on NAT | High (TCP-based) |
| Encryption | WireGuard (E2E) | WireGuard (E2E) |

## DERP Components

### STUN (Session Traversal Utilities for NAT)
- Runs on port 3478 (UDP)
- Determines the node's public IP and port
- Used to establish direct connections before falling back to DERP
- If STUN is blocked, ALL traffic goes through DERP

### DERP Relay
- Runs on port 443 (TCP/WebSocket)
- Relays encrypted WireGuard packets between nodes
- TLS-protected transport
- Each node maintains a persistent WebSocket to its preferred DERP region

## DERP Map

A JSON structure defining available relay regions:
```json
{
  "Regions": {
    "1": {
      "RegionID": 1,
      "RegionCode": "us-east",
      "RegionName": "US East",
      "Nodes": [
        {
          "Name": "derp-1",
          "RegionID": 1,
          "HostName": "derp.example.com",
          "DERPPort": 443,
          "STUNPort": 3478,
          "IPv4": "203.0.113.1",
          "STUNOnly": false
        }
      ]
    }
  }
}
```

## Headscale DERP Modes

### Embedded DERP
Headscale includes a built-in DERP server. Enable in config.yaml:
```yaml
derp:
  server:
    enabled: true
    region_id: 999
    region_code: "headscale"
    region_name: "Headscale Embedded DERP"
    stun_listen_addr: "0.0.0.0:3478"
    private_key_path: /var/lib/headscale/derp_server_key
```

Best for: Small tailnets (<50 nodes), testing, single-region deployments.

### Standalone DERP
Dedicated DERP server for larger deployments or multiple regions:
```yaml
derp:
  urls: ["https://derp1.example.com/derp"]
  paths: []
  auto_update: true
```

Best for: Multi-region deployments, high availability, production.

## DERP Selection

Client selects DERP region automatically:
1. `tailscale status --json` shows `Relay` field per peer
2. `tailscale netcheck` tests latency to all known DERP regions
3. Client connects to lowest-latency region
4. Region switching is automatic if connectivity degrades

## Verifying DERP Usage

```bash
# Check if a peer is using DERP
tailscale status --json | jq '.Peer[] | select(.Relay != null) | {name: .DNSName, relay: .Relay}'

# Test DERP latency
tailscale netcheck --json | jq '.Region'

# Ping a peer and see the path
tailscale ping --verbose 100.x.y.z
```

If ping output says `via <hostname>:443 (derp)` instead of `via <ip>:0 (direct)`,
traffic is going through DERP.
