# TCP & UDP Routing Reference

Traefik can route non-HTTP traffic including databases (PostgreSQL, MySQL), messaging (RabbitMQ, Kafka), and DNS. TCP and UDP routing are configured similarly to HTTP routing but with dedicated router/service types.

## TCP Routing

TCP routers match connections based on SNI (Server Name Indication) or other criteria, and forward to TCP services.

### TCP Router Configuration

```yaml
# Dynamic config (File provider)
tcp:
  routers:
    postgres:
      rule: "HostSNI(`db.example.com`)"     # SNI-based matching
      entryPoints:
        - "postgres"                         # Must be a TCP entryPoint
      service: "postgres-backend"
      tls:
        certResolver: "letsencrypt"          # TLS termination
        options: "default@file"
        passthrough: false                   # true = forward TLS without termination
      priority: 0

    mysql-tls-passthrough:
      rule: "HostSNI(`mysql.example.com`)"
      entryPoints:
        - "mysql"
      service: "mysql-backend"
      tls:
        passthrough: true                    # TLS passthrough (no termination)
```

### TCP Rule Matchers

| Matcher | Description | Example |
|---------|-------------|---------|
| `HostSNI(domain)` | Match SNI value exactly | `` HostSNI(`db.example.com`) `` |
| `HostSNIRegexp(regex)` | Match SNI with regex | `` HostSNIRegexp(`^db\..*\.example\.com$`) `` |
| `HostSNI(`*`)` | Match all connections (catch-all) | `` HostSNI(`*`) `` |

### TCP Service Configuration

```yaml
tcp:
  services:
    postgres-backend:
      loadBalancer:
        servers:
          - address: "10.0.0.1:5432"
          - address: "10.0.0.2:5432"
        sticky: false
        strategy: "wrr"
        terminationDelay: 5s                 # Delay before terminating connection
        proxyProtocol:
          version: 1                         # Enable PROXY protocol to backend
```

TCP service options:

| Option | Description | Default |
|--------|-------------|---------|
| `servers[].address` | Backend address (`host:port`) | Required |
| `servers[].weight` | Load balancing weight | 1 |
| `sticky` | Enable sticky connections | false |
| `strategy` | LB strategy: `wrr` | wrr |
| `terminationDelay` | Connection termination delay | 0s |
| `proxyProtocol.version` | PROXY protocol version | 0 (disabled) |

### TCP Middleware

TCP middlewares are limited — only two built-in types:

```yaml
tcp:
  routers:
    secured-tcp:
      rule: "HostSNI(`app.example.com`)"
      entryPoints: ["secure-tcp"]
      middlewares:
        - "tcp-allowlist"
        - "tcp-inflight"
      service: "tcp-backend"
      tls: {}

  middlewares:
    tcp-allowlist:
      ipAllowList:
        sourceRange:
          - "10.0.0.0/8"
          - "192.168.0.0/16"

    tcp-inflight:
      inFlightConn:
        amount: 50
```

Available TCP middleware:
- `ipAllowList` — Restrict source IPs (same syntax as HTTP version)
- `inFlightConn` — Limit concurrent connections

## UDP Routing

UDP routers handle connectionless UDP traffic. Note that UDP has different semantics — there are no connections, only packets.

### UDP Router Configuration

```yaml
udp:
  routers:
    dns-server:
      entryPoints:
        - "dns-udp"                       # Must be a UDP entryPoint
      service: "dns-backend"

    syslog:
      entryPoints:
        - "syslog-udp"
      service: "syslog-backend"
```

### UDP Service Configuration

```yaml
udp:
  services:
    dns-backend:
      loadBalancer:
        servers:
          - address: "10.0.0.3:53"
          - address: "10.0.0.4:53"
        timeout: 2s                        # UDP session timeout
```

### UDP EntryPoint Configuration

```yaml
entryPoints:
  dns-udp:
    address: ":53/udp"                     # /udp suffix required
    udp:
      timeout: 3s                          # Default UDP timeout
```

## Docker Labels for TCP/UDP

TCP router via Docker labels:

```yaml
labels:
  # TCP router
  - "traefik.tcp.routers.postgres.rule=HostSNI(`db.example.com`)"
  - "traefik.tcp.routers.postgres.entrypoints=postgres"
  - "traefik.tcp.routers.postgres.tls=true"
  - "traefik.tcp.routers.postgres.service=postgres-svc"
  - "traefik.tcp.services.postgres-svc.loadbalancer.server.port=5432"
```

UDP router via Docker labels:

```yaml
labels:
  - "traefik.udp.routers.dns.entrypoints=dns-udp"
  - "traefik.udp.routers.dns.service=dns-svc"
  - "traefik.udp.services.dns-svc.loadbalancer.server.port=53"
```

## Complete Example — PostgreSQL over TCP with TLS

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.2
    command:
      - "--entrypoints.postgres.address=:5432"
      - "--providers.docker=true"
    ports:
      - "5432:5432"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - proxy

  postgres:
    image: postgres:16
    labels:
      - "traefik.tcp.routers.pg.rule=HostSNI(`db.example.com`)"
      - "traefik.tcp.routers.pg.entrypoints=postgres"
      - "traefik.tcp.routers.pg.tls=true"
      - "traefik.tcp.routers.pg.tls.certresolver=letsencrypt"
      - "traefik.tcp.services.pg.loadbalancer.server.port=5432"
    networks:
      - proxy
    environment:
      POSTGRES_PASSWORD: secret
```

## Key Differences: TCP/UDP vs HTTP

| Feature | HTTP | TCP | UDP |
|---------|------|-----|-----|
| EntryPoint protocol | /tcp (default) | /tcp (default) | /udp (explicit) |
| Router match | Host, Path, Header, etc. | HostSNI, HostSNIRegexp | entryPoint only |
| Middleware types | 25+ | 2 (ipAllowList, inFlightConn) | 0 |
| TLS termination | Yes | Yes | No |
| TLS passthrough | N/A | Yes | N/A |
| Sticky sessions | Cookie-based | Connection-based | N/A |
| Health checks | Active + Passive | Passive only | None |
| Service auto-creation | Yes (Docker) | No (must declare service) | No (must declare service) |
