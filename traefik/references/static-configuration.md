# Static Configuration Reference

Traefik's static configuration is set at startup and cannot be changed without restarting. It can be provided via:

1. **YAML file** (`traefik.yml`) — recommended for production
2. **TOML file** (`traefik.toml`) — traditional format
3. **CLI arguments** — `--flag=value` syntax
4. **Environment variables** — `TRAEFIK_<SECTION>_<KEY>` syntax

Traefik loads static config from these locations in order (last wins):
1. `traefik.yml` / `traefik.yaml` in the working directory
2. `$HOME/.traefik/traefik.yml`
3. `/etc/traefik/traefik.yml`
4. CLI flags
5. Environment variables

## Complete YAML Reference

Below is every top-level section with all configurable fields. Placeholder values shown indicate the type expected.

```yaml
## Global Settings
global:
  checkNewVersion: true          # Check for new Traefik versions
  sendAnonymousUsage: true       # Send anonymous usage stats

## Core
core:
  defaultRuleSyntax: v3          # Default rule parser: v2 or v3 (default: v3)

## SPIFFE
spiffe:
  workloadAPIAddr: ""            # SPIRE agent socket path

## Server Transport (HTTP)
serversTransport:
  insecureSkipVerify: false      # Skip TLS verification to backend
  rootCAs:                       # List of root CA certificates
    - /path/to/ca.crt
  maxIdleConnsPerHost: 200       # Max idle connections per host
  forwardingTimeouts:
    dialTimeout: 30s             # TCP dial timeout
    responseHeaderTimeout: 0s    # Timeout for response headers (0=no timeout)
    idleConnTimeout: 90s         # Idle connection timeout
  spiffe:
    ids: []
    trustDomain: ""

## TCP Server Transport
tcpServersTransport:
  dialKeepAlive: 30s
  dialTimeout: 30s
  terminationDelay: 0s           # Delay before terminating TCP connection
  tls:
    insecureSkipVerify: false
    rootCAs: []
    spiffe:
      ids: []
      trustDomain: ""

## EntryPoints — Network listeners
entryPoints:
  web:
    address: ":80"                # Required: [host]:port[/tcp|/udp]
    asDefault: false              # Apply this entryPoint to routers by default
    allowACMEByPass: false        # Allow ACME challenges through custom routers
    reusePort: false              # SO_REUSEPORT for multiple processes
    transport:
      lifeCycle:
        requestAcceptGraceTimeout: 0s
        graceTimeOut: 10s          # Grace period for active requests on shutdown
      respondingTimeouts:
        readTimeout: 60s           # Max time to read entire request
        writeTimeout: 0s           # Max time to write response (0=no timeout)
        idleTimeout: 180s          # Max idle keep-alive time
      keepAliveMaxTime: 0s         # Max keep-alive connection lifetime
      keepAliveMaxRequests: 0      # Max requests per keep-alive connection (0=unlimited)
    proxyProtocol:
      insecure: false              # Trust ALL proxy protocol headers (unsafe)
      trustedIPs: []               # IPs/CIDRs allowed to send proxy protocol
    forwardedHeaders:
      insecure: false              # Trust ALL X-Forwarded-* headers
      trustedIPs: []               # IPs/CIDRs trusted to send forwarded headers
      connection: []               # Connection headers to allow through middleware chain
    http:
      redirections:
        entryPoint:
          to: websecure            # Target entryPoint name or port
          scheme: https            # Target scheme
          permanent: true          # 301 vs 302 redirect
          priority: 9223372036854775806  # Router priority for redirect
      middlewares: []              # Default middlewares prepended to all routers
      tls:
        options: ""                # Default TLS options name
        certResolver: ""           # Default ACME cert resolver
        domains:
          - main: example.com
            sans:
              - www.example.com
      encodeQuerySemicolons: false
      maxHeaderBytes: 1048576      # Max request header size (bytes)
    http2:
      maxConcurrentStreams: 250    # HTTP/2 concurrent streams per connection
    http3:
      advertisedPort: 0            # UDP port to advertise for HTTP/3
    udp:
      timeout: 3s                  # UDP idle timeout

  websecure:
    address: ":443"
    http:
      tls: true                     # Enable TLS on all routers on this entryPoint

## Providers
providers:
  providersThrottleDuration: 2s    # Min time between config reloads

  # --- Docker Provider ---
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: true          # Auto-expose containers (set false for security)
    network: ""                     # Default network for container connections
    defaultRule: "Host(`{{ normalize .Name }}`)"
    useBindPortIP: false
    watch: true
    constraints: ""                 # Filter containers (Label("key","value"))
    allowEmptyServices: false
    httpClientTimeout: 0s
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false

  # --- Docker Swarm Provider ---
  swarm:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: true
    network: ""
    defaultRule: "Host(`{{ normalize .Name }}`)"
    useBindPortIP: false
    watch: true
    constraints: ""
    allowEmptyServices: false
    refreshSeconds: 15s
    httpClientTimeout: 0s

  # --- File Provider ---
  file:
    directory: "/etc/traefik/dynamic/"  # Watch directory for .yml/.yaml/.toml files
    filename: ""                         # Single file (alternative to directory)
    watch: true
    debugLogGeneratedTemplate: false

  # --- Kubernetes Ingress Provider ---
  kubernetesIngress:
    endpoint: ""                         # In-cluster if empty
    token: ""
    certAuthFilePath: ""
    namespaces: []                       # Restrict to specific namespaces (empty=all)
    labelSelector: ""
    ingressClass: ""
    ingressEndpoint:
      ip: ""
      hostname: ""
      publishedService: ""
    throttleDuration: 0s
    allowEmptyServices: false
    allowExternalNameServices: false
    disableIngressClassLookup: false
    disableClusterScopeResources: false
    nativeLBByDefault: false

  # --- Kubernetes CRD Provider ---
  kubernetesCRD:
    endpoint: ""
    token: ""
    certAuthFilePath: ""
    namespaces: []
    allowCrossNamespace: false
    allowExternalNameServices: false
    labelSelector: ""
    ingressClass: ""
    throttleDuration: 0s
    allowEmptyServices: false
    nativeLBByDefault: false
    disableClusterScopeResources: false

  # --- Kubernetes Gateway API Provider ---
  kubernetesGateway:
    endpoint: ""
    token: ""
    certAuthFilePath: ""
    namespaces: []
    labelSelector: ""
    throttleDuration: 0s
    experimentalChannel: false
    statusAddress:
      ip: ""
      hostname: ""
      service:
        name: ""
        namespace: ""

  # --- REST Provider ---
  rest:
    insecure: false               # Enable REST provider on default entryPoint

  # --- HTTP Provider ---
  http:
    endpoint: "http://..."
    pollInterval: 5s
    pollTimeout: 30s
    headers: {}                   # Request headers to send
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false

  # --- Redis (KV) Provider ---
  redis:
    rootKey: "traefik"
    endpoints: ["127.0.0.1:6379"]
    username: ""
    password: ""
    db: 0
    tls:
      ca: ""
      cert: ""
      key: ""
      insecureSkipVerify: false
    sentinel:
      masterName: ""
      username: ""
      password: ""
      latencyStrategy: false
      randomStrategy: false
      replicaStrategy: false
      useDisconnectedReplicas: false

  # --- Plugin Provider Config ---
  plugin:
    pluginName:
      key: value                  # Arbitrary plugin-specific config

## API & Dashboard
api:
  insecure: false                 # Expose API on Traefik's entryPoint without auth
  dashboard: true                 # Enable dashboard (requires api.insecure or a router)
  debug: false                    # Enable debugging endpoints
  disableDashboardAd: false       # Remove Traefik ad from dashboard

## Ping
ping:
  entryPoint: ""                  # EntryPoint for ping endpoint
  manualRouting: false            # Don't auto-create ping router
  terminatingStatusCode: 503      # Status code when Traefik is shutting down

## Logging
log:
  level: "ERROR"                  # DEBUG, PANIC, FATAL, ERROR, WARN, INFO
  format: "common"                # common or json
  noColor: false
  filePath: ""                    # Log file (stdout if empty)
  maxSize: 100                    # Max megabytes before rotate
  maxAge: 30                      # Max days to retain
  maxBackups: 5                   # Max old log files
  compress: true

## Access Log
accessLog:
  filePath: ""                    # Access log file (stdout if empty)
  format: "common"                # common or json
  bufferingSize: 0                # Buffer size (0=unbuffered)
  addInternals: false             # Log internal services (ping, dashboard, etc.)
  filters:
    statusCodes: []               # Keep logs matching status codes/range
    retryAttempts: false          # Keep logs of retried requests
    minDuration: 0s               # Keep logs for requests over duration
  fields:
    defaultMode: "keep"           # keep, drop
    names:
      ClientHost: "keep"         # Per-field override
      ClientPort: "keep"         # keep, drop, redact
      ...                        # All field names: ClientHost, ClientPort, ClientUsername,
                                 # RequestHost, RequestPath, RequestMethod, RequestProtocol,
                                 # RequestContentSize, RequestLine, ResponseStatus,
                                 # ResponseContentSize, Duration, OriginDuration,
                                 # FrontendName, BackendName, BackendURL, RouterName,
                                 # ServiceName, ServiceURL, StartUTC, StartLocal, DownstreamStatus,
                                 # DownstreamContentSize, DownstreamContentSize, RequestCount,
                                 # RetryAttempts
    headers:
      defaultMode: "drop"         # keep, drop, redact
      names:
        Authorization: "redact"   # Per-header override

## Metrics
metrics:
  addInternals: false
  prometheus:
    buckets: [0.1, 0.3, 1.2, 5.0]  # Latency buckets in seconds
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    entryPoint: "metrics"         # EntryPoint for Prometheus metrics endpoint
    manualRouting: false
    headerLabels: {}              # Additional labels from request headers
  datadog:
    address: "localhost:8125"
    pushInterval: 10s
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    prefix: "traefik"
  statsD:
    address: "localhost:8125"
    pushInterval: 10s
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    prefix: "traefik"
  influxDB2:
    address: "http://localhost:8086"
    token: ""
    pushInterval: 10s
    org: ""
    bucket: ""
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    additionalLabels: {}
  otlp:
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    pushInterval: 10s
    explicitBoundaries: [0.0]      # Custom histogram boundaries
    grpc:
      endpoint: ""
      insecure: false
      headers: {}
      tls:
        ca: ""
        cert: ""
        key: ""
        insecureSkipVerify: false
    http:
      endpoint: ""
      headers: {}
      tls:
        ca: ""
        cert: ""
        key: ""
        insecureSkipVerify: false

## Tracing
tracing:
  serviceName: "traefik"
  sampleRate: 1.0                 # 0.0 to 1.0
  addInternals: false
  globalAttributes: {}            # Key-value pairs added to all spans
  capturedRequestHeaders: []      # Headers to capture in request spans
  capturedResponseHeaders: []     # Headers to capture in response spans
  safeQueryParams: []             # Query params to NOT redact
  otlp:
    grpc:
      endpoint: ""
      insecure: false
      headers: {}
      tls:
        ca: ""
        cert: ""
        key: ""
        insecureSkipVerify: false
    http:
      endpoint: ""
      headers: {}
      tls:
        ca: ""
        cert: ""
        key: ""
        insecureSkipVerify: false

## Certificate Resolvers (ACME / Let's Encrypt)
certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@example.com"    # REQUIRED — ACME registration email
      caServer: "https://acme-v02.api.letsencrypt.org/directory"  # or acme-staging
      storage: "/letsencrypt/acme.json"  # Certificate storage path
      keyType: "RSA4096"            # EC256, EC384, RSA2048, RSA4096, RSA8192
      preferredChain: ""            # Preferred certificate chain
      certificatesDuration: 2160    # Hours before renewal begins (default: 90 days)
      disableCommonName: false      # Disable CN in CSR
      profile: ""                   # Certificate profile
      caCertificates: []            # Custom CA for ACME server verification
      caSystemCertPool: false
      caServerName: ""
      emailAddresses: []
      clientTimeout: 2m
      responseHeaderTimeout: 30s
      certificateTimeout: 30s
      eab:
        kid: ""                     # External Account Binding key ID
        hmacEncoded: ""             # External Account Binding HMAC key
      httpChallenge:
        entryPoint: "web"           # EntryPoint for HTTP-01 (port 80)
        delay: 0
      tlsChallenge: {}              # Enable TLS-ALPN-01 (port 443)
      dnsChallenge:
        provider: ""                # e.g., "cloudflare", "route53", "gcloud"
        delayBeforeCheck: 0s        # Wait before DNS propagation check
        resolvers: []               # Custom DNS resolvers
        disablePropagationCheck: false
        requireAllRNS: false        # Check all recursive nameservers
        disableANSChecks: false     # Skip authoritative NS checks
        propagation:
          delayBeforeChecks: 0s
          disableChecks: false
          requireAllRNS: false
          disableANSChecks: false
    tailscale: {}                   # Enable Tailscale certificate support

## Host Resolver
hostResolver:
  cnameFlattening: false
  resolvConfig: ""
  resolvDepth: 5

## Experimental Features
experimental:
  plugins:
    pluginName:
      moduleName: "github.com/example/plugin"
      version: "v0.1.0"
      settings: {}                  # Plugin-specific config
  localPlugins:
    pluginName:
      moduleName: "path/to/plugin"  # Local plugin module path
      settings: {}
  kubernetesGateway: false          # Enable K8s Gateway API provider
  fastProxy:
    # FastProxy settings (HTTP/2 multiplexing optimization)
```
