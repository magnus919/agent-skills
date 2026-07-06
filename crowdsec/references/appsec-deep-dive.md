# AppSec (WAF) Deep Dive

The AppSec Component turns CrowdSec into a full-fledged Web Application Firewall (WAF). It provides virtual patching, OWASP CRS support, and behavioral detection.

## Architecture

1. A web server / reverse proxy receives an HTTP request
2. The request is forwarded to the AppSec endpoint (port 7422 by default)
3. **In-band rules** are evaluated first:
   - If triggered → return `ban` or `captcha` action (blocking)
   - If not → continue to step 4
4. The web server processes the request normally
5. **Out-of-band rules** evaluate asynchronously:
   - If triggered → emit an event into the Security Engine
   - Events feed into scenarios for longer-term decisions (e.g., extend a ban)

## Key Concepts

### In-band vs Out-of-band

| | In-band | Out-of-band |
|---|---|---|
| **Blocking** | Yes — blocks the current request | No — emits an event for later processing |
| **Performance impact** | Adds latency to each request | Zero (async evaluation) |
| **Use cases** | SQLi, XSS, path traversal, CVE exploitation | Enumeration, scraping, spam, resource scanning |

### Rule Sources

- **`crowdsecurity/appsec-default`** — Default AppSec configuration
- **`crowdsecurity/crs`** — OWASP Core Rule Set (converted from ModSecurity)
- **`crowdsecurity/virtual-patching`** — CrowdSec's curated virtual patches

## Installation

### 1. Install AppSec collections

```bash
sudo cscli collections install crowdsecurity/appsec-virtual-patching
sudo cscli collections install crowdsecurity/appsec-crs
sudo cscli collections install crowdsecurity/appsec-generic-rules
```

### 2. Add AppSec acquisition source

In `/etc/crowdsec/acquis.yaml` or `acquis.d/appsec.yaml`:

```yaml
source: appsec
listen_addr: 0.0.0.0:7422
appsec_config: crowdsecurity/appsec-default
labels:
  type: appsec
```

### 3. Configure the bouncer to forward requests

For Traefik (see `traefik-bouncer.md` for full config):
```yaml
crowdsecAppsecEnabled: true
crowdsecAppsecHost: crowdsec:7422
crowdsecAppsecFailureBlock: true      # Block if AppSec is unreachable
crowdsecAppsecUnreachableBlock: true  # Block if AppSec fails
crowdsecAppsecBodyLimit: 10485760     # Max request body to inspect (10MB)
```

### 4. Restart CrowdSec

```bash
sudo systemctl restart crowdsec
```

## Verification

```bash
# Check AppSec metrics
sudo cscli metrics show appsec

# Test with a blocked request pattern
curl -I http://your-service/.env
# Should return 403
```

## Custom AppSec Rules

AppSec rules are YAML files in `/etc/crowdsec/appsec-rules/`:

```yaml
# /etc/crowdsec/appsec-rules/my-custom-rule.yaml
name: myapp/block-admin-paths
description: Block access to admin paths
rules:
  - and:
    - zones:
      - URI
      match: raw
      expressions:
        - startsWith("/admin")
    - zones:
      - METHOD
      match: raw
      expressions:
        - REQUEST_GET
action: ban
```

## Virtual Patching

Virtual patching rules protect against known CVEs without modifying application code. These are maintained by CrowdSec and updated via `cscli hub update`.

## Gotchas

- Installing rules is not enough — you must **enable the AppSec datasource and restart CrowdSec.**
- The remediation component **must support AppSec forwarding** and be configured with the correct `listen_addr`.
- In-band rules return an action for the **current request** (ban/captcha). Longer-term bans come from scenarios.
- **`crowdsecAppsecBodyLimit`** controls max body size — bodies larger than this are truncated.
- AppSec adds latency to every request — test performance impact before enabling on high-traffic endpoints.
