# Traefik Bouncer Integration

The CrowdSec Traefik bouncer is a community plugin (`maxlerebourg/crowdsec-bouncer-traefik-plugin`) that integrates CrowdSec decisions into Traefik as a middleware.

## Overview

Two modes of operation:
1. **Stream mode** (recommended) — CrowdSec pushes decisions to Traefik in real-time
2. **Live mode** — Traefik queries CrowdSec LAPI on each request

## Prerequisites

- CrowdSec Security Engine running with LAPI accessible to Traefik
- A bouncer API key created: `sudo cscli bouncers add traefik-bouncer`
- Traefik v2.x or v3.x

## Static Configuration (traefik.yaml)

### 1. Enable the plugin

```yaml
experimental:
  plugins:
    bouncer:
      moduleName: github.com/maxlerebourg/crowdsec-bouncer-traefik-plugin
      version: v1.6.0
```

### 2. Enable access logs

```yaml
accessLog:
  filePath: "/logs/traefik.log"
  format: json
  filters:
    statusCodes:
      - "200-299"
      - "400-599"
  bufferingSize: 0
  fields:
    headers:
      defaultMode: drop
      names:
        User-Agent: keep
```

### 3. Configure forwarded headers (for Cloudflare etc.)

```yaml
entryPoints:
  https:
    address: :443
    forwardedHeaders:
      trustedIPs:
        - 103.21.244.0/22      # Cloudflare IPv4 ranges
        # ... add all Cloudflare IPs
        - 2400:cb00::/32       # Cloudflare IPv6 ranges
```

## Dynamic Configuration (middleware)

### Stream Mode (recommended — API key in file)

```yaml
middlewares:
  crowdsec:
    plugin:
      bouncer:
        enabled: true
        crowdsecMode: stream
        crowdsecLapiScheme: http
        crowdsecLapiHost: crowdsec:8080
        crowdsecLapiPath: /
        crowdsecLapiKeyFile: /etc/traefik/crowdsec/BOUNCER_KEY_traefik
        forwardedHeadersTrustedIPs:
          - 10.0.0.0/8
          - 172.16.0.0/12
          - 192.168.0.0/16
        clientTrustedIPs:
          - 10.0.0.0/8
          - 172.16.0.0/12
          - 192.168.0.0/16
```

### With AppSec WAF

```yaml
middlewares:
  crowdsec:
    plugin:
      bouncer:
        enabled: true
        crowdsecMode: stream
        crowdsecLapiScheme: http
        crowdsecLapiHost: crowdsec:8080
        crowdsecLapiKeyFile: /etc/traefik/crowdsec/BOUNCER_KEY_traefik
        crowdsecAppsecEnabled: true
        crowdsecAppsecHost: crowdsec:7422
        crowdsecAppsecFailureBlock: true
        crowdsecAppsecUnreachableBlock: true
        crowdsecAppsecBodyLimit: 10485760
```

## Applying the Middleware

### Per-router (via labels)

```yaml
labels:
  - traefik.http.routers.myservice.middlewares=crowdsec@file
```

### Entrypoint-wide (default for all routes)

```yaml
entryPoints:
  https:
    http:
      middlewares:
        - crowdsec@file
```

## Kubernetes Deployment

For Kubernetes, mount the bouncer key from a Secret:

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: crowdsec-bouncer
spec:
  plugin:
    bouncer:
      enabled: true
      crowdsecMode: stream
      crowdsecLapiScheme: http
      crowdsecLapiHost: crowdsec-service.crowdsec.svc.cluster.local:8080
      crowdsecLapiPath: /
      crowdsecLapiKeyFile: /etc/traefik/crowdsec/BOUNCER_KEY_traefik
      crowdsecAppsecEnabled: true
      crowdsecAppsecHost: crowdsec-appsec-service.crowdsec.svc.cluster.local:7422
```

## Troubleshooting

- **403 on all requests:** Bouncer key is wrong or LAPI is unreachable
- **IPs not being banned:** Check `forwardedHeadersTrustedIPs` — the real client IP must be trusted
- **Cloudflare users:** Set `forwardedHeadersCustomName: X-Real-Ip` if using CF-Connecting-IP
- **Plugin not found:** Verify `experimental.plugins` in static config and plugin version
- **Stream mode not updating decisions:** Check that CrowdSec LAPI is reachable from Traefik on port 8080
