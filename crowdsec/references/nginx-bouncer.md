# Nginx Bouncer Configuration

The CrowdSec Nginx bouncer integrates via Lua directives to check incoming requests against CrowdSec decisions.

## Installation

```bash
sudo apt install crowdsec-firewall-bouncer-nginx
```

## Bouncer Configuration

The bouncer YAML config lives at `/etc/crowdsec/bouncers/crowdsec-nginx-bouncer.yaml`:

```yaml
# /etc/crowdsec/bouncers/crowdsec-nginx-bouncer.yaml
api_url: http://127.0.0.1:8080
api_key: "<your-bouncer-api-key>"
mode: stream            # stream (push) or live (pull per request)
update_frequency: 10s   # Decision refresh interval (stream mode)
```

### Modes

- **stream** (recommended): LAPI pushes decisions to the bouncer over a persistent connection. Lower latency, fewer API calls.
- **live**: The bouncer queries LAPI on each request. Higher latency but simpler to debug.

## Nginx Configuration

Add to your Nginx `server {}` block or to `nginx.conf`:

```nginx
# Load the CrowdSec Lua module
lua_package_path "/usr/lib/crowdsec/lua/?.lua;;";

# Shared dictionary for caching decisions (10MB)
lua_shared_dict crowdsec_cache 10m;

# Initialize on worker start
init_by_lua_block {
    local bouncer = require "crowdsec"
    bouncer.init()
}

# Check each request against CrowdSec decisions
access_by_lua_block {
    local bouncer = require "crowdsec"
    if bouncer.check() then
        return ngx.exit(ngx.FORBIDDEN)
    end
}
```

## Cloudflare / CDN

If Nginx is behind Cloudflare or another CDN, the real client IP must be passed to the bouncer. Set the real IP header in Nginx:

```nginx
set_real_ip_from 103.21.244.0/22;
# ... all Cloudflare CIDR ranges
real_ip_header CF-Connecting-IP;
```

Then configure the bouncer to trust the forwarded header:
```yaml
trusted_forwarded_ip_count: 1
trusted_forwarded_header_name: "X-Forwarded-For"
```

## Verification

```bash
# Check bouncer is registered and active
sudo cscli bouncers list

# Test with a manually banned IP
sudo cscli decisions add --ip 203.0.113.99 --duration 5m
curl -I http://your-server/  # From the banned IP → should return 403
sudo cscli decisions delete --ip 203.0.113.99
```

## Troubleshooting

- **403 on all requests:** Check `api_key` matches what `sudo cscli bouncers add <name>` returned
- **Lua errors in Nginx logs:** Verify `lua_package_path` points to the correct install directory
- **IP not being banned:** Check `forwardedHeadersTrustedIPs` if behind a proxy/CDN
- **Bouncer not showing in `cscli bouncers list`:** Restart crowdsec after adding the bouncer
