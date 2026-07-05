# Observability Reference

Traefik provides comprehensive observability: metrics, access logs, tracing, and health checks.

## Metrics

Configure metrics collection in static configuration:

```yaml
metrics:
  addInternals: false         # Include metrics for Traefik's own services

  # --- Prometheus (most common) ---
  prometheus:
    buckets:
      - 0.1
      - 0.3
      - 1.2
      - 5.0                    # Request latency buckets (seconds)
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    entryPoint: "metrics"       # Dedicated entryPoint for metrics scraping
    manualRouting: false        # Set true to create your own router
    headerLabels:               # Additional labels from request headers
      X-Custom: "custom_label"

  # --- Datadog ---
  datadog:
    address: "localhost:8125"
    pushInterval: 10s
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    prefix: "traefik"

  # --- StatsD ---
  statsD:
    address: "localhost:8125"
    pushInterval: 10s
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    prefix: "traefik"

  # --- InfluxDB v2 ---
  influxDB2:
    address: "http://localhost:8086"
    token: "my-token"
    pushInterval: 10s
    org: "my-org"
    bucket: "traefik"
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    additionalLabels: {}

  # --- OpenTelemetry ---
  otlp:
    grpc:
      endpoint: "localhost:4317"
      insecure: true
    http:
      endpoint: "localhost:4318"
    pushInterval: 10s
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    explicitBoundaries:
      - 0.0
```

### Prometheus Scraping Setup

```yaml
# Static config — dedicated entryPoint for metrics
entryPoints:
  metrics:
    address: ":9100"

metrics:
  prometheus:
    entryPoint: "metrics"
    addRoutersLabels: true
    addServicesLabels: true
```

```bash
# Verify Prometheus metrics
curl http://localhost:9100/metrics | grep traefik
```

### Key Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `traefik_http_requests_total` | Counter | Total request count |
| `traefik_http_request_duration_seconds` | Histogram | Request duration |
| `traefik_http_requests_in_flight` | Gauge | Current in-flight requests |
| `traefik_backend_server_up` | Gauge | Backend server health (0/1) |
| `traefik_config_reloads_total` | Counter | Config reload count |
| `traefik_config_last_reload_success` | Gauge | Last reload success (0/1) |
| `traefik_tls_certs_not_after` | Gauge | TLS cert expiry timestamp |
| `traefik_entrypoint_open_connections` | Gauge | Open connections per entryPoint |
| `traefik_entrypoint_request_duration_seconds` | Histogram | Per-entryPoint request duration |

## Access Logs

Traefik can log every request (similar to Apache/Nginx access logs). Configure in static config:

```yaml
accessLog:
  filePath: "/var/log/traefik/access.log"   # File path (stdout if empty)
  format: "common"                          # common or json
  bufferingSize: 0                          # Buffer N lines (0=unbuffered)
  addInternals: false                       # Log Traefik's internal requests

  filters:
    statusCodes:
      - "200-299"
      - "400-499"
      - "500-599"                           # Only log these status code ranges
    retryAttempts: true                     # Only log requests that were retried
    minDuration: "10s"                      # Only log requests over this duration

  fields:
    defaultMode: "keep"                     # keep, drop, redact
    names:
      ClientHost: "keep"
      ClientPort: "drop"                    # Per-field override — drop client port
      RequestHost: "keep"
      RequestPath: "keep"
      RequestMethod: "keep"
      RequestProtocol: "keep"
      ResponseStatus: "keep"
      Duration: "keep"
      RetryAttempts: "keep"

    headers:
      defaultMode: "drop"                   # By default, don't log headers
      names:
        Authorization: "redact"             # Redact auth header values
        User-Agent: "keep"                  # But keep user-agent
        Referer: "keep"
```

### Access Log Fields

| Field Name | Description |
|-----------|-------------|
| `ClientHost` | Client IP address |
| `ClientPort` | Client port |
| `ClientUsername` | Authenticated username |
| `RequestHost` | Requested host |
| `RequestPath` | Request path |
| `RequestMethod` | HTTP method |
| `RequestProtocol` | HTTP protocol version |
| `RequestContentSize` | Request body size |
| `RequestLine` | Full request line |
| `ResponseStatus` | HTTP status code |
| `ResponseContentSize` | Response body size |
| `Duration` | Request duration |
| `OriginDuration` | Duration at origin |
| `RouterName` | Router that matched |
| `ServiceName` | Service that handled request |
| `ServiceURL` | Backend URL that handled request |
| `DownstreamStatus` | Downstream connection status |
| `StartUTC` | Request start time (UTC) |
| `StartLocal` | Request start time (local) |
| `RetryAttempts` | Number of retry attempts |
| `FrontendName` | (deprecated) Legacy router name |

### Common Log Format

```
<ClientHost> - <ClientUsername> [<StartUTC>] "<RequestLine>" <ResponseStatus> <ResponseContentSize> "<RequestRefererHeader>" "<RequestUserAgentHeader>" <Duration> <RequestCount>
```

Real example:
```
192.168.1.100 - - [05/Jul/2026:10:15:30 +0000] "GET /api/users HTTP/2" 200 1234 "-" "curl/8.0" 0.045 1
```

### JSON Log Format

```json
{
  "ClientHost": "192.168.1.100",
  "ClientPort": 54321,
  "StartUTC": "2026-07-05T10:15:30Z",
  "RequestMethod": "GET",
  "RequestPath": "/api/users",
  "RequestProtocol": "HTTP/2.0",
  "ResponseStatus": 200,
  "ResponseContentSize": 1234,
  "Duration": 45000000,
  "RouterName": "api-router",
  "ServiceName": "api-backend",
  "ServiceURL": "http://10.0.0.5:3000",
  "RetryAttempts": 0
}
```

## Tracing

Traefik supports OpenTelemetry tracing:

```yaml
tracing:
  serviceName: "traefik"
  sampleRate: 0.1                           # Sample 10% of requests (0.0 to 1.0)
  addInternals: false
  globalAttributes:
    environment: "production"

  # OpenTelemetry Protocol (OTLP)
  otlp:
    grpc:
      endpoint: "localhost:4317"
      insecure: true
    http:
      endpoint: "localhost:4318"

  # Headers to capture in spans
  capturedRequestHeaders:
    - "User-Agent"
    - "X-Request-Id"
  capturedResponseHeaders:
    - "Content-Type"
  safeQueryParams:                           # Query params NOT redacted
    - "id"
    - "page"
```

Tracing verbosity:
- **minimal** (default): One server span, one client span per request
- **detailed**: Additional spans for each middleware

```yaml
entryPoints:
  websecure:
    address: ":443"
    observability:
      tracing: true
      traceVerbosity: detailed              # Or: minimal
```

## Health Check (Ping)

```yaml
ping:
  entryPoint: "web"                         # EntryPoint for /ping
  manualRouting: false
  terminatingStatusCode: 503                # Return this during graceful shutdown
```

The ping endpoint returns:
- `200 OK` — Traefik is healthy and accepting requests
- `503 Service Unavailable` — Traefik is shutting down (graceful termination)

```bash
# Health check
curl -s -o /dev/null -w "%{http_code}" http://localhost:80/ping

# With Docker healthcheck
healthcheck:
  test: ["CMD", "wget", "-q", "-O-", "http://localhost:80/ping"]
  interval: 30s
  timeout: 3s
  retries: 3
```

## Per-Router Observability Control

Router-level overrides for observability:

```yaml
http:
  routers:
    internal-only:
      rule: "Host(`internal.example.com`)"
      service: "internal-backend"
      observability:
        metrics: false                       # Don't emit metrics for this router
        accessLogs: true                     # Do log this router
        tracing: false                       # Don't trace this router
```
