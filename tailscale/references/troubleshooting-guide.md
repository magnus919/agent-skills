# Tailscale/Headscale Troubleshooting Guide

## Common Issues and Solutions

### 1. "No nodes found" or "No connectivity"

**Possible causes:**
- Headscale service not running
- Firewall blocking port 443 (or custom port)
- DNS not resolving headscale URL
- TLS certificate expired or invalid

**Diagnostics:**
```bash
systemctl status headscale               # Check service status
curl -sI https://headscale.example.com    # Check reachability
tailscale status                          # Check connection state
```

### 2. Direct connections show as DERP relay only

**Possible causes:**
- STUN port (3478) blocked by firewall
- Symmetric NAT on one or both sides
- Corporate firewall blocking UDP
- ISP CGNAT

**Diagnostics:**
```bash
tailscale netcheck           # Check NAT and DERP status
tailscale ping --verbose     # See the path (direct vs derp)
```

**Fix:** Open STUN port 3478/UDP. If not possible, accept DERP routing (still encrypted).

### 3. Auth key expired

Headscale pre-auth keys default to 1-hour expiry.

**Fix:** Create a new key or use `--expiration 0` for no expiration:
```bash
headscale preauthkeys create --user alice --expiration 168h  # 7 days
headscale preauthkeys create --user alice --reusable          # Multi-use
```

### 4. Node shows as "offline"

**Possible causes:**
- Device is shut down or asleep
- Network changed (new WiFi, VPN)
- tailscaled crashed
- Headscale server unreachable

**Fix:**
```bash
systemctl restart tailscaled              # Restart client daemon
tailscale up --login-server https://...    # Re-authenticate
```

### 5. Subnet routes not working

**Possible causes:**
- Route not approved in headscale
- Client not using `--accept-routes`
- Subnet route not reachable from gateway machine

**Check:**
```bash
# On headscale
headscale routes list --node <node-id>

# On gateway
ip route show | grep <subnet>            # Verify route exists locally

# On client
tailscale status --json | jq '.Peer[].Routes'
```

### 6. Duplicate 100.x.y.z IP assignment

Tailscale/Headscale assigns stable IPs based on node identity. If duplicate:
- Likely caused by restoring a backup on a different headscale instance
- Clear node state: `rm -rf /var/lib/tailscale/ && tailscale up ...`

### 7. "Already in use" — port conflict

tailscaled listens on :8080 for MagicDNS and port 41641/UDP for WireGuard.

**Check:**
```bash
lsof -i :8080
lsof -i :41641
```

**Fix:** Change port: `tailscale up --port 41642`
Or disable MagicDNS: `tailscale up --accept-dns=false`

### 8. Certificate errors

Headscale requires valid TLS certificates for production use.

**Check:**
```bash
openssl s_client -connect headscale.example.com:443 2>/dev/null | openssl x509 -noout -subject -dates
```

**Fix:** Use Let's Encrypt via certbot, Traefik, or Caddy as reverse proxy.

### 9. SQLite database corruption

Headscale uses SQLite. Corruption can occur from improper shutdown or filesystem issues.

**Symptoms:** `headscale nodes list` fails, or nodes disappear.

**Fix:** Restore from backup. If no backup, try:
```bash
sqlite3 /var/lib/headscale/db.sqlite ".recover" | sqlite3 /tmp/recovered.db
```

### 10. "MagicDNS not working" / DNS resolution fails

**Check:**
```bash
tailscale status --json | jq '.MagicDNSEnabled'
nslookup <node-name>.<tailnet-name>.ts.net  # Test DNS resolution
```

**Fix:**
- Ensure `--accept-dns` is set on client
- Check `dns_config` in headscale config.yaml
- Verify no local DNS service is blocking port 53

### 11. API key lost or expired

API keys cannot be retrieved after creation. They expire by default in 90 days.

**Fix:** Create a new key and update all scripts:
```bash
headscale apikeys create                  # New API key
headscale apikeys list                    # List existing prefixes
headscale apikeys expire --prefix <pfx>   # Remove old key
```

### 12. Client can't connect after headscale upgrade

**Possible cause:** Protocol mismatch between headscale and client.

**Fix:** Upgrade tailscale client to match headscale version:
```bash
# Debian/Ubuntu
sudo apt update && sudo apt upgrade tailscale

# macOS
brew upgrade tailscale
```

## Quick Diagnostic Pipeline

```bash
# 1. Headscale health
curl -s https://headscale.example.com/version

# 2. Node count
headscale nodes list | wc -l

# 3. Client status
tailscale status --json

# 4. Connectivity test
tailscale ping --c 3 --verbose <peer-ip>

# 5. DERP check
tailscale netcheck --json

# 6. Route check
headscale routes list --json
```
