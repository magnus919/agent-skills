# Production Deployment Reference

Production-ready patterns for deploying Traefik with Docker Compose, including security hardening, high availability considerations, and advanced configurations.

## Production Docker Compose Template

```yaml
version: "3.8"

services:
  traefik:
    image: traefik:v3.7
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    networks:
      - proxy
    ports:
      - "80:80"
      - "443:443"
      # Do NOT expose the dashboard port externally — access via router
    environment:
      - CF_DNS_API_TOKEN=${CF_DNS_API_TOKEN}    # DNS challenge env vars
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro   # Read-only socket
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./letsencrypt:/letsencrypt               # ACME certificate storage
    labels:
      # Dashboard
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.tls=true"
      - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
      - "traefik.http.routers.dashboard.middlewares=dashboard-auth"
      - "traefik.http.middlewares.dashboard-auth.basicauth.users=${DASHBOARD_AUTH}"
```

Full static config (`traefik.yml`):

```yaml
global:
  checkNewVersion: false
  sendAnonymousUsage: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false                    # Secure: only expose labeled containers
    network: "proxy"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@example.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"
      # For wildcard certs use dnsChallenge instead:
      # dnsChallenge:
      #   provider: "cloudflare"

api:
  dashboard: false                             # Dashboard disabled in static config
  # We create the dashboard router dynamically
```

## Security Hardening

### Docker Socket Security

**Never mount the Docker socket directly in production without precautions:**

Option 1: Read-only socket mount (minimal)

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

Option 2: Docker Socket Proxy (recommended)

```yaml
services:
  docker-proxy:
    image: tecnativa/docker-socket-proxy
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - CONTAINERS=1                           # Only allow container read access
      - NETWORKS=1
      - SERVICES=1
      - TASKS=1

  traefik:
    image: traefik:v3.7
    environment:
      - DOCKER_HOST=tcp://docker-proxy:2375
    # Do NOT mount the docker socket directly
```

### Container Security

```yaml
services:
  traefik:
    security_opt:
      - no-new-privileges:true      # Prevent privilege escalation
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE            # Allow binding to privileged ports (<1024)
    # For running on port 80/443 as non-root, use:
    # sysctls:
    #   - net.ipv4.ip_unprivileged_port_start=0
    user: "1000:1000"               # Run as non-root user
```

### Headers Security Baseline

```yaml
http:
  middlewares:
    sec-headers:
      headers:
        sslRedirect: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        frameDeny: true
        contentTypeNosniff: true
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        permissionsPolicy: "camera=(), microphone=(), geolocation=()"
        contentSecurityPolicy: "default-src 'self'"
```

### Rate Limiting

```yaml
http:
  middlewares:
    ratelimit:
      rateLimit:
        average: 100
        burst: 200
        sourceCriterion:
          ipStrategy:
            depth: 1

  routers:
    app:
      rule: "Host(`app.example.com`)"
      middlewares:
        - "ratelimit"
```

## Environment Variable Management

Use a `.env` file for sensitive values (never hardcode in docker-compose.yml):

```env
# .env — DO NOT COMMIT
CF_DNS_API_TOKEN=your_cloudflare_token_here
DASHBOARD_AUTH=admin:$2y$05$...
ACME_EMAIL=admin@example.com
```

Reference in docker-compose.yml:

```yaml
services:
  traefik:
    environment:
      - CF_DNS_API_TOKEN=${CF_DNS_API_TOKEN}
```

## Multiple Environments

```yaml
# docker-compose.override.yml — local development overrides
services:
  traefik:
    ports:
      - "8080:8080"                     # Expose dashboard for local dev
    labels:
      - "traefik.http.routers.dashboard.rule=Host(`traefik.localhost`)"
      # No TLS for local
```

```bash
# Dev
docker compose up -d

# Production (excludes override)
docker compose -f docker-compose.yml up -d
```

## High Availability Considerations

Traefik v3 OSS runs as a single instance. For HA:

- **DNS round-robin** — multiple Traefik instances behind DNS
- **Shared ACME storage** — Use a shared filesystem (NFS) or redis KV for ACME storage
- **Layer 4 load balancer** — Put a TCP load balancer (HAProxy, AWS NLB) in front
- **Redis KV provider** — Use Redis as a central configuration store for all instances
- **SO_REUSEPORT** — `reusePort: true` on entryPoints for kernel-level load balancing

```yaml
entryPoints:
  web:
    address: ":80"
    reusePort: true          # Multiple Traefik instances share the port
  websecure:
    address: ":443"
    reusePort: true
```

Note: `reusePort` works on Linux, FreeBSD, OpenBSD, and macOS. There's a known Linux kernel bug that may cause TCP connection issues — test thoroughly.

## File Provider Patterns

For complex configurations that don't fit in Docker labels:

```yaml
# Static config
providers:
  file:
    directory: "/etc/traefik/dynamic/"
    watch: true
```

```yaml
# /etc/traefik/dynamic/tls.yml
tls:
  options:
    default:
      minVersion: VersionTLS12
      sniStrict: false
    mtls:
      minVersion: VersionTLS12
      clientAuth:
        caFiles:
          - "/etc/traefik/certs/ca.pem"
        clientAuthType: RequireAndVerifyClientCert
```

```yaml
# /etc/traefik/dynamic/middlewares.yml
http:
  middlewares:
    global-rate-limit:
      rateLimit:
        average: 100
        burst: 200
```

## Logging Configuration

```yaml
# Static config
log:
  level: "INFO"                 # In production: INFO or WARN
  format: "json"                # JSON for log aggregators
  filePath: "/var/log/traefik/traefik.log"

accessLog:
  format: "json"                # Structured logging
  filePath: "/var/log/traefik/access.log"
  filters:
    statusCodes:
      - "400-599"               # Only log errors and client errors
  fields:
    headers:
      defaultMode: "drop"
      names:
        Authorization: "redact"
```

## TLS Certificate Storage

```yaml
volumes:
  - ./letsencrypt:/letsencrypt
```

**Critical:** The `acme.json` file must have permissions `600`:

```bash
chmod 600 ./letsencrypt/acme.json
```

If deploying via Docker, Traefik creates this file with correct permissions automatically (as long as the directory exists and is writable).

## Monitoring Stack

Combine with Prometheus for a complete monitoring setup:

```yaml
services:
  traefik:
    labels:
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.prometheus.rule=Host(`monitor.example.com`)"
```
