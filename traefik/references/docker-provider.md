# Docker Provider Reference

Traefik's Docker provider automatically discovers containers and generates routing configuration from container labels. This is the most common way to use Traefik in development and production.

## Enabling the Docker Provider

```yaml
# Static config (traefik.yml)
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false    # Secure: only expose labeled containers
    network: "proxy"           # Default network
    defaultRule: "Host(`{{ normalize .Name }}`)"
    watch: true
```

## Docker Compose — Mounting the Socket

```yaml
services:
  traefik:
    image: traefik:v3.7
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock   # Required
      - ./traefik.yml:/etc/traefik/traefik.yml       # Static config
      - ./letsencrypt:/letsencrypt                    # ACME storage
    networks:
      - proxy
```

## All Docker Labels Reference

Labels follow the pattern: `traefik.<protocol>.<resource-type>.<name>.<option>=<value>`

### General Labels

| Label | Description |
|-------|-------------|
| `traefik.enable=true` | Explicitly enable this container (required when `exposedByDefault=false`) |
| `traefik.docker.network=mynetwork` | Override the default Docker network for this container |
| `traefik.docker.allowNonRunning=true` | Enable discovery of non-running containers |

### HTTP Router Labels

Prefix: `traefik.http.routers.<name>.`

| Label | Description |
|-------|-------------|
| `rule=Host(\`example.com\`)` | Router matching rule (REQUIRED — or use `defaultRule`) |
| `entrypoints=web,websecure` | EntryPoints to attach this router to |
| `middlewares=auth,ratelimit` | Comma-separated list of middleware names |
| `service=my-service` | Target service for this router (auto-assigned if omitted) |
| `tls=true` | Enable TLS |
| `tls.certresolver=letsencrypt` | Certificate resolver for automatic cert |
| `tls.domains[0].main=example.com` | Define domain for TLS certificate |
| `tls.domains[0].sans=www.example.com` | SANs for the certificate |
| `tls.options=default@file` | TLS options to apply |
| `priority=42` | Router priority (higher = matched first) |
| `ruleSyntax=v3` | Rule syntax version (v3 or v2, default: v3) |
| `observability.metrics=true` | Enable metrics for this router |
| `observability.accesslogs=true` | Enable access logs for this router |
| `observability.tracing=true` | Enable tracing for this router |

### HTTP Service Labels

Prefix: `traefik.http.services.<name>.`

| Label | Description |
|-------|-------------|
| `loadbalancer.server.port=8080` | Backend port (REQUIRED when container exposes multiple ports) |
| `loadbalancer.server.scheme=https` | Backend scheme (default: http) |
| `loadbalancer.passhostheader=true` | Forward Host header to backend |
| `loadbalancer.strategy=wrr` | Strategy: wrr, p2c, hrw, leasttime |
| `loadbalancer.sticky.cookie.name=sticky` | Enable sticky sessions via cookie |
| `loadbalancer.sticky.cookie.httponly=true` | Set HttpOnly flag on sticky cookie |
| `loadbalancer.sticky.cookie.secure=true` | Set Secure flag on sticky cookie |
| `loadbalancer.sticky.cookie.samesite=none` | SameSite attribute: none/lax/strict |
| `loadbalancer.sticky.cookie.maxage=86400` | Cookie max age in seconds |
| `loadbalancer.healthcheck.path=/health` | Health check endpoint path |
| `loadbalancer.healthcheck.interval=10s` | Health check interval |
| `loadbalancer.healthcheck.timeout=3s` | Health check timeout |
| `loadbalancer.healthcheck.hostname=example.com` | Host header for health check |
| `loadbalancer.healthcheck.scheme=https` | Scheme for health check |
| `loadbalancer.healthcheck.method=GET` | HTTP method for health check |
| `loadbalancer.healthcheck.headers.X-Custom=v` | Custom headers for health check |
| `loadbalancer.healthcheck.followredirects=true` | Follow redirects during health checks |
| `loadbalancer.passivehealthcheck.maxfailedattempts=3` | Failures before considered unhealthy |
| `loadbalancer.passivehealthcheck.failurewindow=3s` | Time window for failure counting |
| `loadbalancer.serverstransport=custom@file` | Reference to a ServersTransport |
| `loadbalancer.responseforwarding.flushinterval=150ms` | Flush interval for streaming |

### HTTP Middleware Labels

Prefix: `traefik.http.middlewares.<name>.`

Middleware types and their label syntax:

| Middleware Type | Label Syntax |
|----------------|-------------|
| `addprefix` | `traefik.http.middlewares.my-mw.addprefix.prefix=/api/v2` |
| `basicauth` | `traefik.http.middlewares.my-mw.basicauth.users=user:$$2y$$10$$...` |
| `digestauth` | `traefik.http.middlewares.my-mw.digestauth.users=user:realm:hash` |
| `forwardauth` | `traefik.http.middlewares.my-mw.forwardauth.address=http://auth:8080/verify` |
| `headers` | `traefik.http.middlewares.my-mw.headers.customrequestheaders.X-Scope=internal` |
| `ipallowlist` | `traefik.http.middlewares.my-mw.ipallowlist.sourcerange=10.0.0.0/8` |
| `ratelimit` | `traefik.http.middlewares.my-mw.ratelimit.average=100` |
| `redirectscheme` | `traefik.http.middlewares.my-mw.redirectscheme.scheme=https` |
| `redirectregex` | `traefik.http.middlewares.my-mw.redirectregex.regex=^http://(.*)` |
| `replacepath` | `traefik.http.middlewares.my-mw.replacepath.path=/fallback` |
| `replacepathregex` | `traefik.http.middlewares.my-mw.replacepathregex.regex=^/api/v1/(.*)` |
| `stripprefix` | `traefik.http.middlewares.my-mw.stripprefix.prefixes=/api,/v1` |
| `stripprefixregex` | `traefik.http.middlewares.my-mw.stripprefixregex.regex=/[a-z]+/public` |
| `retry` | `traefik.http.middlewares.my-mw.retry.attempts=3` |
| `compress` | `traefik.http.middlewares.my-mw.compress=true` |
| `circuitbreaker` | `traefik.http.middlewares.my-mw.circuitbreaker.expression=NetworkErrorRatio() > 0.5` |
| `inflightreq` | `traefik.http.middlewares.my-mw.inflightreq.amount=100` |
| `ratelimit` | `traefik.http.middlewares.my-mw.ratelimit.average=100` |
| `chain` | `traefik.http.middlewares.my-mw.chain.middlewares=mw1,mw2,mw3` |
| `errorpages` | `traefik.http.middlewares.my-mw.errorpages.status=500-599` |
| `contenttype` | `traefik.http.middlewares.my-mw.contenttype=true` |
| `grpcweb` | `traefik.http.middlewares.my-mw.grpcweb=true` |

### TCP Router Labels

Prefix: `traefik.tcp.routers.<name>.`

| Label | Description |
|-------|-------------|
| `rule=HostSNI(\`example.com\`)` | SNI matching rule |
| `entrypoints=postgres` | EntryPoints (must be TCP) |
| `service=my-service` | Target TCP service |
| `tls=true` | Enable TLS passthrough or termination |
| `tls.certresolver=letsencrypt` | Cert resolver for TLS termination |
| `tls.options=default@file` | TLS options |
| `tls.passthrough=false` | TLS passthrough (no termination) |

### TCP Service Labels

Prefix: `traefik.tcp.services.<name>.`

| Label | Description |
|-------|-------------|
| `loadbalancer.server.port=5432` | Backend port |
| `loadbalancer.server.address=10.0.0.1` | Backend IP (auto-detected if omitted) |
| `loadbalancer.server.proxyProtocol.version=1` | Enable PROXY protocol to backend |
| `loadbalancer.terminationdelay=5s` | Connection termination delay |
| `loadbalancer.sticky=false` | Enable sticky sessions |
| `loadbalancer.strategy=wrr` | Load balancing strategy |

### UDP Router Labels

Prefix: `traefik.udp.routers.<name>.`

| Label | Description |
|-------|-------------|
| `entrypoints=dns` | EntryPoints (must be UDP) |
| `service=my-service` | Target UDP service |

### UDP Service Labels

Prefix: `traefik.udp.services.<name>.`

| Label | Description |
|-------|-------------|
| `loadbalancer.server.port=53` | Backend UDP port |

## Reference Examples

### Basic Service with Custom Port

```yaml
services:
  app:
    image: myapp:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls=true"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
      - "traefik.http.services.app.loadbalancer.server.port=3000"
    networks:
      - proxy
```

### Multiple Routers for One Container

```yaml
labels:
  - "traefik.enable=true"
  # API router
  - "traefik.http.routers.api.rule=Host(`api.example.com`) && PathPrefix(`/v1`)"
  - "traefik.http.routers.api.service=api-service"
  - "traefik.http.services.api-service.loadbalancer.server.port=8080"
  # Admin router (different port)
  - "traefik.http.routers.admin.rule=Host(`admin.example.com`)"
  - "traefik.http.routers.admin.service=admin-service"
  - "traefik.http.services.admin-service.loadbalancer.server.port=9090"
```

### With Middleware Chain

```yaml
labels:
  - "traefik.enable=true"
  # Middleware declarations
  - "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$10$$..."
  - "traefik.http.middlewares.limit.ratelimit.average=100"
  - "traefik.http.middlewares.limit.ratelimit.burst=200"
  - "traefik.http.middlewares.headers.customrequestheaders.X-Forwarded-Proto=https"
  # Router with middleware chain
  - "traefik.http.routers.app.rule=Host(`app.example.com`)"
  - "traefik.http.routers.app.middlewares=auth,limit,headers"
  - "traefik.http.routers.app.tls=true"
  - "traefik.http.routers.app.tls.certresolver=letsencrypt"
  - "traefik.http.services.app.loadbalancer.server.port=80"
```

### Hashing Passwords for BasicAuth

```bash
# Generate a bcrypt hash for BasicAuth
htpasswd -nbB admin "my-password" | sed -e 's/\$/\$\$/g'
# Output: admin:$$2y$$05$$...
# Note: $$ escaping is required in Docker Compose files
```

### Docker Network Selection

When a container is connected to multiple Docker networks, specify the correct one:

```yaml
networks:
  - proxy       # Network Traefik is on
  - internal    # Network for backend communication

labels:
  - "traefik.docker.network=proxy"
```

### Constraints

Filter which containers Traefik discovers:

```yaml
# Static config
providers:
  docker:
    constraints: "Label(`traefik.enable`, `true`) && !Label(`internal`, `true`)"
```

### Port Detection Rules

Traefik automatically determines the backend port:

1. If a container exposes **one** port, Traefik uses it
2. If it exposes **multiple** ports, Traefik uses the **lowest**
3. Always set `loadbalancer.server.port` to be explicit

### Security Note: Docker Socket

Mounting the Docker socket gives the container root-equivalent access to the host. For production:
- Use [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) for read-only access
- Or expose the socket over SSH/TCP with TLS client certificates
- Run Traefik as a non-root user when possible (use `--users` flag)
