# API & Dashboard Reference

Traefik exposes a REST API for querying configuration, health, and routing state. The dashboard is a web UI built on top of the API.

## API Configuration

```yaml
# Static config
api:
  insecure: false              # Expose on Traefik's default entryPoint (not recommended)
  dashboard: true              # Enable the dashboard UI
  debug: false                 # Enable /debug/pprof endpoints
  disableDashboardAd: false    # Remove the "Powered by Traefik" ad
```

## Securing the API/Dashboard

**NEVER use `api.insecure: true` in production.** Instead, create a router with authentication:

```yaml
# Method 1: File provider
http:
  routers:
    dashboard:
      rule: "Host(`traefik.example.com`) && (PathPrefix(`/api`) || PathPrefix(`/dashboard`))"
      service: "api@internal"                    # Built-in API service
      middlewares:
        - "dashboard-auth"
        - "dashboard-headers"
      tls:
        certResolver: "letsencrypt"

  middlewares:
    dashboard-auth:
      basicAuth:
        users:
          - "admin:$2y$05$..."                   # bcrypt hash
    dashboard-headers:
      headers:
        customResponseHeaders:
          X-Robots-Tag: "noindex,nofollow,nocache"
```

Or with Docker labels:

```yaml
services:
  traefik:
    image: traefik:v3.2
    labels:
      - "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.tls=true"
      - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
      - "traefik.http.routers.dashboard.middlewares=dashboard-auth"
      - "traefik.http.middlewares.dashboard-auth.basicauth.users=admin:$$2y$$05$$..."
```

## API Endpoints

All API endpoints are available under the configured base path (default `/`). Requires `api.dashboard: true` in static config.

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/http/routers` | GET | List all HTTP routers |
| `/api/http/routers/{name}` | GET | Get router details |
| `/api/http/services` | GET | List all HTTP services |
| `/api/http/services/{name}` | GET | Get service details |
| `/api/http/middlewares` | GET | List all HTTP middlewares |
| `/api/http/middlewares/{name}` | GET | Get middleware details |
| `/api/http/rules` | GET | List all HTTP rules |
| `/api/tcp/routers` | GET | List all TCP routers |
| `/api/tcp/services` | GET | List all TCP services |
| `/api/tcp/middlewares` | GET | List all TCP middlewares |
| `/api/tcp/routers/{name}` | GET | Get TCP router details |
| `/api/udp/routers` | GET | List all UDP routers |
| `/api/udp/services` | GET | List all UDP services |
| `/api/version` | GET | Traefik version info |
| `/api/overview` | GET | Aggregated overview counts |

### Debug Endpoints (require `api.debug: true`)

| Endpoint | Description |
|----------|-------------|
| `/api/providers/{provider}` | View provider-specific configuration |
| `/debug/pprof/` | Go pprof profiling data |
| `/debug/pprof/cmdline` | Command line |
| `/debug/pprof/profile` | CPU profile |
| `/debug/pprof/trace` | Execution trace |
| `/debug/pprof/heap` | Heap profile |
| `/debug/pprof/goroutine` | Goroutine dump |
| `/debug/pprof/threadcreate` | Thread creation profile |
| `/debug/pprof/block` | Blocking profile |
| `/debug/pprof/mutex` | Mutex profile |

### Raw Configuration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rawconfig` | GET | Full current configuration (static + dynamic) |
| `/api/rawconfig/http/services` | GET | HTTP services config |
| `/api/rawconfig/http/routers` | GET | HTTP routers config |
| `/api/rawconfig/tcp/routers` | GET | TCP routers config |

### Health Check

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ping` | GET, HEAD | Health check (requires `ping` config) |
| `/api/http/health` | GET | API health check |

## Ping Configuration

Separate from the API, the ping endpoint provides a simple health check:

```yaml
# Static config
ping:
  entryPoint: "web"              # EntryPoint for ping
  manualRouting: false           # Set true if creating your own router for ping
  terminatingStatusCode: 503     # Status code to return during shutdown
```

With `ping.entryPoint` set, Traefik auto-creates a router for `/ping`. Set `manualRouting: true` to create your own:

```yaml
http:
  routers:
    ping:
      rule: "Path(`/ping`)"
      entryPoints: ["web"]
      service: "ping@internal"
```

## API Usage Examples

```bash
# Get all HTTP routers
curl -s https://traefik.example.com/api/http/routers | jq .

# Get specific router
curl -s https://traefik.example.com/api/http/routers/my-router | jq .

# Check version
curl -s https://traefik.example.com/api/version

# Get overview counts
curl -s https://traefik.example.com/api/overview | jq .

# Health check
curl -s -o /dev/null -w "%{http_code}" https://traefik.example.com/ping

# Get raw configuration (debug mode required)
curl -s https://traefik.example.com/api/rawconfig | jq '.http.routers'
```

## Dashboard Security Checklist

1. **Never** use `api.insecure: true` in production
2. Always put authentication (BasicAuth, ForwardAuth, OIDC) in front of the dashboard
3. Restrict access by IP when possible (IPAllowList middleware)
4. Use a dedicated hostname for the dashboard (separate from your app domains)
5. Enable TLS on the dashboard route
6. Set the `X-Robots-Tag: noindex` header to prevent search indexing
7. Consider putting the dashboard on a private network/vpn-only entryPoint
8. Monitor dashboard access logs
