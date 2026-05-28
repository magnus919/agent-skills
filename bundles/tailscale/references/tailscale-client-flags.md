# Client Flags Reference — Tailscale CLI for Headscale

## `tailscale up` — Connect to a tailnet

All flags are used with `tailscale up` and are idempotent — running `tailscale up`
again with different flags updates the configuration.

| Flag | Purpose | Used With Headscale? |
|---|---|---|
| `--login-server <URL>` | Point client at self-hosted Headscale | **Required** |
| `--authkey <key>` | Non-interactive auth with pre-auth key | Yes |
| `--advertise-tags tag:<name>` | Tag this node as a service (not user-owned) | Yes |
| `--advertise-routes <cidr>` | Advertise subnet routes (e.g. 192.168.1.0/24) | Yes |
| `--accept-routes` | Accept advertised routes from subnet routers | Yes |
| `--accept-dns` | Accept MagicDNS configuration | Yes (default) |
| `--advertise-exit-node` | Make this node an exit node | Yes |
| `--exit-node <IP>` | Route traffic through this exit node | Yes |
| `--exit-node-allow-lan-access` | Allow LAN access while using exit node | Yes |
| `--shields-up` | Block all incoming connections | Yes |
| `--snat-subnet-routes` | SNAT traffic from subnet routes (default: on) | Yes |
| `--netfilter-mode <mode>` | off/noflush/on (iptables management) | Yes |
| `--accept-risk <risk>` | Accept known risks (e.g. `all`) | Yes |
| `--reset` | Reset all configuration to defaults | Yes |
| `--hostname <name>` | Override machine hostname in tailnet | Yes |
| `--operator <user>` | Allow non-root user to run tailscale commands | Yes |

## `tailscale status` — Show tailnet status

```
tailscale status              # Human-readable table
tailscale status --json       # Machine-readable JSON
tailscale status --peers      # Show all peers (not just current)
tailscale status --active     # Show only active peers
tailscale status --self       # Show only this node
tailscale status --watch      # Watch for changes
```

## `tailscale ping` — Test connectivity to a peer

```
tailscale ping <hostname-or-ip>           # Basic ping
tailscale ping --verbose <host>            # Show DERP vs direct
tailscale ping -c 3 <host>                 # Count (number of pings)
tailscale ping --timeout 10s <host>        # Timeout
tailscale ping --c 3 --verbose 100.x.y.z  # Standard diagnostic
```

Exit codes: 0 = reached, 1 = not reached, 2 = error.

## `tailscale netcheck` — NAT traversal diagnostics

```
tailscale netcheck             # Human-readable report
tailscale netcheck --json     # Machine-readable
```

Reports: NAT type, DERP latency per region, IPv4/IPv6 capability, captive portal detection.

## `tailscale version` — Show version info

```
tailscale version              # Client version
tailscale version --daemon     # tailscaled version
tailscale version --json       # Structured output
```

## `tailscale ssh` — SSH into tailnet nodes

```
tailscale ssh <user>@<host>    # SSH via tailnet (uses Tailscale SSH if configured)
```

Requires Tailscale SSH to be configured in the policy file.

## `tailscale serve` — Expose local services (NOT in Headscale)

```
tailscale serve --bg 3000     # Run as background service
```

**Note:** `tailscale serve` and `tailscale funnel` are not supported in Headscale.

## `tailscale file` — File sharing (Taildrop/Taildrive)

```
tailscale file get <url>       # Receive a file
tailscale file send <path>     # Send a file
tailscale file cp <path> <target>:<path>  # Copy file (Taildrive)
```

## `tailscale cert` — Get TLS certificate

```
tailscale cert <domain>        # Get cert for MagicDNS name
```

## Other Useful Commands

```
tailscale down                 # Disconnect from tailnet
tailscale logout               # Log out (re-authenticate on next up)
tailscale set --<flag>         # Change single setting without full re-auth
tailscale debug                # Debug commands (bugreport, metrics, etc.)
tailscale bugreport            # Generate diagnostic bundle
tailscale whois <IP>           # Look up who owns a tailnet IP
```
