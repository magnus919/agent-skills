# ServersTransport Reference

Defines how Traefik connects to backend servers. Configured in static config and referenced per-service in dynamic config.

## HTTP ServersTransport

Controls the connection between Traefik and HTTP backend services.

```yaml
# Static config
serversTransport:
  insecureSkipVerify: false         # Skip TLS verification to backend
  rootCAs:                          # List of root CA certificate paths
    - /etc/traefik/certs/ca.pem
  maxIdleConnsPerHost: 200          # Max idle connections per backend host
  forwardingTimeouts:
    dialTimeout: 30s                # TCP dial timeout to backend
    responseHeaderTimeout: 0s       # Timeout for backend response headers (0=unlimited)
    idleConnTimeout: 90s            # Idle keep-alive connection timeout
  spiffe:
    ids: []                         # SPIFFE IDs for workload identity
    trustDomain: ""                 # SPIFFE trust domain
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `insecureSkipVerify` | Skip TLS certificate verification for backend connections | `false` |
| `rootCAs` | Paths to PEM-encoded CA certificates for backend TLS verification | `[]` |
| `maxIdleConnsPerHost` | Maximum idle connections kept per backend host | `200` |
| `forwardingTimeouts.dialTimeout` | Maximum time to establish TCP connection to backend | `30s` |
| `forwardingTimeouts.responseHeaderTimeout` | Maximum time to wait for response headers from backend | `0s` (no timeout) |
| `forwardingTimeouts.idleConnTimeout` | Maximum time a keep-alive connection can remain idle | `90s` |
| `spiffe.ids` | Allowed SPIFFE identities for workload identity | `[]` |
| `spiffe.trustDomain` | SPIFFE trust domain for workload identity | `""` |

## TCP ServersTransport

Controls connections for TCP routing (non-HTTP backends).

```yaml
# Static config
tcpServersTransport:
  dialKeepAlive: 30s                # Keep-alive probe interval for TCP connections
  dialTimeout: 30s                   # TCP dial timeout
  terminationDelay: 0s               # Delay before terminating TCP connection on shutdown
  tls:
    insecureSkipVerify: false        # Skip TLS verification
    rootCAs:                         # Root CA certificates for backend TLS
      - /etc/traefik/certs/ca.pem
    spiffe:
      ids: []
      trustDomain: ""
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `dialKeepAlive` | TCP keep-alive probe interval | `30s` |
| `dialTimeout` | TCP dial timeout | `30s` |
| `terminationDelay` | Delay before TCP connection termination on shutdown | `0s` |
| `tls.insecureSkipVerify` | Skip TLS verification for backend | `false` |
| `tls.rootCAs` | Root CA certificate paths | `[]` |
| `tls.spiffe.ids` | Allowed SPIFFE identities | `[]` |
| `tls.spiffe.trustDomain` | SPIFFE trust domain | `""` |

## Per-Service ServersTransport Override

Reference a named serversTransport from a specific service in dynamic config:

```yaml
# Dynamic config (File provider)
http:
  serversTransports:
    mTLS-to-backend:
      insecureSkipVerify: false
      rootCAs:
        - /etc/traefik/certs/internal-ca.pem
      forwardingTimeouts:
        dialTimeout: 10s

  services:
    secure-api:
      loadBalancer:
        servers:
          - url: "https://backend.internal:443"
        serversTransport: "mTLS-to-backend@file"
```

Via Docker labels:

```yaml
labels:
  - "traefik.http.services.api.loadbalancer.serverstransport=mTLS-to-backend@file"
```

## mTLS Between Traefik and Backends

For mutual TLS (backends that require client certificates):

```yaml
# Dynamic config
http:
  serversTransports:
    mtls:
      insecureSkipVerify: false
      rootCAs:
        - /etc/traefik/certs/ca.pem        # CA that signed the backend cert
      # NOTE: serversTransport does NOT support client cert/key fields.
      # For client certificate authentication to backends, configure
      # TLS at the service level or use ForwardAuth.

  services:
    internal-api:
      loadBalancer:
        serversTransport: "mtls@file"
        servers:
          - url: "https://api.internal:8443"
```

## Kubernetes CRD Reference

In Kubernetes, define a `ServersTransport` CRD:

```yaml
apiVersion: traefik.io/v1alpha1
kind: ServersTransport
metadata:
  name: mtls-transport
spec:
  serverName: "api.internal"
  insecureSkipVerify: false
  rootCAs:
    - secret: internal-ca-secret         # Kubernetes Secret reference
  forwardingTimeouts:
    dialTimeout: 30s
    responseHeaderTimeout: 30s
    idleConnTimeout: 90s
```

Reference in an IngressRoute:

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
spec:
  routes:
    - kind: Rule
      match: Host(`app.example.com`)
      services:
        - name: api-service
          port: 8443
          serversTransport: mtls-transport
```

For TCP services, use `ServersTransportTCP`:

```yaml
apiVersion: traefik.io/v1alpha1
kind: ServersTransportTCP
metadata:
  name: tcp-mtls
spec:
  tls:
    insecureSkipVerify: false
    serverName: "db.internal"
    rootCAs:
      - secret: db-ca-secret
```

## Connection Pooling Best Practices

```yaml
# For high-throughput APIs — minimize connection churn
serversTransport:
  maxIdleConnsPerHost: 500
  forwardingTimeouts:
    dialTimeout: 5s                    # Fast fail on unavailable backends
    responseHeaderTimeout: 30s
    idleConnTimeout: 120s              # Longer idle time reduces reconnects

# For latency-sensitive services — tight timeouts
serversTransport:
  maxIdleConnsPerHost: 50
  forwardingTimeouts:
    dialTimeout: 3s
    responseHeaderTimeout: 10s
    idleConnTimeout: 30s
```
