# Routing Reference — Subnet Routers & Exit Nodes

## Subnet Routers

A subnet router extends the tailnet to devices that can't run the Tailscale client
(printers, NAS devices, IoT, etc.).

### Setup

1. **On the gateway node** (the machine that can reach the target subnet):
```bash
tailscale up --login-server https://headscale.example.com --advertise-routes=192.168.1.0/24 --accept-routes
```

2. **Approve the route in Headscale**:
```bash
headscale routes list                     # Find route ID
headscale routes enable <route-id>        # Approve
```

3. **On client nodes** that need access:
```bash
tailscale up --login-server https://headscale.example.com --accept-routes
```

### Auto-Approval

Configure headscale policy to auto-approve routes:
```json
{
  "autoApprovers": {
    "routes": {
      "192.168.0.0/16": ["alice@"],
      "10.0.0.0/8": ["autogroup:admin"]
    }
  }
}
```

### Route Filtering (Grants Via)

Restrict cross-subnet access to specific ports:
```json
{
  "grants": [
    {
      "src": ["autogroup:member"],
      "dst": ["tag:gateway"],
      "ip": ["*"],
      "via": ["192.168.1.0/24:80,443"]
    }
  ]
}
```

### SNAT (Source NAT)

By default, subnet router traffic appears to originate from the router's own IP.
Disable `--snat-subnet-routes=false` if the subnet needs to see the origina-tailing
client's tailnet IP (requires proper routing back).

## Exit Nodes

An exit node routes all internet traffic from other tailnet clients through the
exit node's internet connection.

### Setup

1. **On the exit node** (the machine that will provide internet access):
```bash
tailscale up --advertise-exit-node
```

2. **Approve in Headscale**:
```bash
headscale routes list                     # Find the exit node route
headscale routes enable <route-id>
```

3. **On client devices**:
```bash
# Use a specific exit node
tailscale up --exit-node=100.x.y.z

# Or, to use an exit node while still accessing local LAN
tailscale up --exit-node=100.x.y.z --exit-node-allow-lan-access
```

### Auto-Approval for Exit Nodes

```json
{
  "autoApprovers": {
    "exitNode": ["tag:gateway", "alice@"]
  }
}
```

## Route Management Commands

### Headscale server side:
```bash
headscale routes list                               # All routes
headscale routes list --node <node-id>              # Routes for one node
headscale routes enable <route-id>                  # Approve/Enable
headscale routes disable <route-id>                 # Disable
headscale routes delete <route-id>                  # Remove route
```

### Client side:
```bash
tailscale up --advertise-routes=10.0.0.0/24          # Advertise subnet
tailscale up --advertise-routes=10.0.0.0/24,192.168.1.0/24  # Multiple subnets
tailscale up --advertise-exit-node                   # Advertise as exit node
tailscale up --accept-routes                         # Accept all advertised routes
tailscale up --exit-node=100.x.y.z                   # Use an exit node
tailscale up --exit-node-allow-lan-access            # Allow LAN with exit node
```

## Diagnostics

```bash
# Check if routes are accepted
tailscale status --json | jq '.Peer[].Routes'

# Check which exit node is active
tailscale status | grep -E '^100\.'

# Check subnet router status
tailscale status --self --json | jq '.Self.Routes'
```
