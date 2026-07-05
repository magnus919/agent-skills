# Middleware Catalog

Middleware modifies requests before they reach services or modifies responses before they reach clients. Middleware attaches to routers (applied to matching requests) or services (applied to requests handled by that service). Router middlewares execute before service middlewares.

## Path Modifiers

### AddPrefix

Adds a path prefix before forwarding to the backend.

```yaml
http:
  middlewares:
    api-prefix:
      addPrefix:
        prefix: "/api/v2"
```

**Example:** Request to `/users` becomes `/api/v2/users` to the backend.

### StripPrefix

Removes matching path prefixes before forwarding.

```yaml
http:
  middlewares:
    strip-api:
      stripPrefix:
        prefixes:
          - "/api"
          - "/v1"
        forceSlash: false    # If true, ensures trailing slash after stripping
```

**Example:** `/api/users` → `/users`, `/v1/products` → `/products`

### StripPrefixRegex

Removes path portions matching a regex.

```yaml
http:
  middlewares:
    strip-version:
      stripPrefixRegex:
        regex:
          - "/[a-z]+/[0-9]+"
```

### ReplacePath

Replaces the entire path with a fixed value.

```yaml
http:
  middlewares:
    replace:
      replacePath:
        path: "/fallback"
```

### ReplacePathRegex

Replaces path portions using regex capture groups.

```yaml
http:
  middlewares:
    rewrite-api:
      replacePathRegex:
        regex: "^/api/v1/(.*)"
        replacement: "/v2/$1"
```

## Redirects

### RedirectScheme

Redirects requests based on the scheme.

```yaml
http:
  middlewares:
    https-redirect:
      redirectScheme:
        scheme: https
        port: "443"
        permanent: true
```

### RedirectRegex

Redirects using regex matching and replacement on the entire URL.

```yaml
http:
  middlewares:
    domain-redirect:
      redirectRegex:
        regex: "^http://old-domain.com/(.*)"
        replacement: "https://new-domain.com/$1"
        permanent: true
```

## Security & Authentication

### BasicAuth

HTTP Basic Authentication with bcrypt passwords.

```yaml
http:
  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$2y$05$..."         # bcrypt hash
          - "user:$apr1$..."           # Apache MD5
        usersFile: "/etc/traefik/auth/.htpasswd"  # Alternative to inline users
        realm: "Traefik"               # Realm sent in WWW-Authenticate header
        headerField: "X-WebAuth-User"  # Inject authenticated user into this header
        removeHeader: true             # Remove Authorization header before backend
```

Generate password hashes:

```bash
# bcrypt (recommended)
htpasswd -nbB admin "password" | sed -e 's/\$/\$\$/g'

# Or use the usersFile with htpasswd
htpasswd -nbB admin "password" >> /etc/traefik/auth/.htpasswd
```

### DigestAuth

HTTP Digest Authentication.

```yaml
http:
  middlewares:
    digest-auth:
      digestAuth:
        users:
          - "user:realm:hash"
        usersFile: "/etc/traefik/auth/.htdigest"
        realm: "Traefik"
        removeHeader: true
        headerField: "X-WebAuth-User"
```

### ForwardAuth

Delegates authentication to an external service.

```yaml
http:
  middlewares:
    ext-auth:
      forwardAuth:
        address: "http://auth-service:8080/verify"  # REQUIRED
        trustForwardHeader: true       # Trust X-Forwarded-* headers
        tls:
          ca: "/etc/traefik/certs/ca.pem"
          cert: "/etc/traefik/certs/cert.pem"
          key: "/etc/traefik/certs/key.pem"
          insecureSkipVerify: false
        tls.caOptional: false          # Client cert not required
        authResponseHeaders:
          X-Auth-User: "X-Auth-User"   # Map response headers to request headers
          X-Auth-Token: "X-Auth-Token"
        authResponseHeadersRegex: "^X-Auth-"  # Regex matching response headers to forward
        authRequestHeaders:
          X-My-Header: "X-Forwarded-Proto"    # Map request headers to forward auth
        authSetHeaders:
          X-Forwarded-User: "{!header.X-Auth-User!}"  # Set headers from auth response
        addAuthCookiesToResponse:
          - "session_token"            # Remove auth cookies from backend response
        maxClientConnectDuration: 30s  # Max time for auth request
        maxBodySize: 0                 # Max body size to forward (0=unlimited)
```

### IPAllowList

Restricts allowed client IPs.

```yaml
http:
  middlewares:
    ip-whitelist:
      ipAllowList:
        sourceRange:
          - "10.0.0.0/8"
          - "192.168.0.0/16"
          - "203.0.113.0/24"
        ipStrategy:
          depth: 1                     # X-Forwarded-For depth to check
          excludedIPs: []              # IPs to exclude from X-Forwarded-For chain
```

### InFlightReq

Limits simultaneous connections.

```yaml
http:
  middlewares:
    concurrency-limit:
      inFlightReq:
        amount: 100                    # Max simultaneous requests
        sourceCriterion:
          requestHost: true            # Track by host
          requestRemoteAddr: true      # Track by remote address
          ipStrategy:
            depth: 1
            excludedIPs: []
```

### RateLimit

Limits request frequency (per-source-IP by default).

```yaml
http:
  middlewares:
    ratelimit:
      rateLimit:
        average: 100                   # Average requests per second (REQUIRED)
        burst: 200                     # Burst size (default: average)
        period: 1s                     # Evaluation period (default: 1s)
        sourceCriterion:
          requestHost: true
          requestRemoteAddr: true
          ipStrategy:
            depth: 1
            excludedIPs: []
        # For Redis-backed distributed rate limiting:
        # Requires Traefik Enterprise or Hub
```

### Distributed RateLimit

Redis-backed rate limiting (requires Traefik Enterprise or Hub).

```yaml
# Distributed rate limiting is a Traefik Hub/Enterprise feature
# Not available in Traefik Proxy OSS
http:
  middlewares:
    dist-ratelimit:
      distributedRateLimit:
        average: 100
        burst: 200
        period: 1s
        sourceCriterion:
          requestRemoteAddr: true
```

### Headers

Modifies request and response headers, and sets security-related headers.

```yaml
http:
  middlewares:
    sec-headers:
      headers:
        # --- Custom Header Modifications ---
        customRequestHeaders:          # Add/override request headers
          X-Scope: "internal"
          X-Forwarded-Proto: "https"
        customResponseHeaders:         # Add/override response headers
          X-Custom: "value"

        # --- CORS Headers ---
        accessControlAllowCredentials: true
        accessControlAllowMethods:
          - "GET"
          - "POST"
          - "PUT"
          - "DELETE"
          - "OPTIONS"
        accessControlAllowOriginList:
          - "https://app.example.com"
          - "https://admin.example.com"
        accessControlAllowOriginListRegex:
          - "^https://[a-z]+\\.example\\.com$"
        accessControlExposeHeaders:
          - "X-Custom-Header"
        accessControlMaxAge: 100
        accessControlAllowHeaders:
          - "Content-Type"
          - "Authorization"
        addVaryHeader: true

        # --- Security Headers ---
        # These set the corresponding HTTP security headers
        hostsProxyHeaders:
          - "X-Forwarded-Host"
        sslRedirect: true              # Redirect HTTP to HTTPS
        sslTemporaryRedirect: true    # Use 302 instead of 301 for SSL redirect
        sslHost: "app.example.com"     # Host in the Location header for SSL redirect
        sslProxyHeaders:
          X-Forwarded-Proto: "https"
        sslForceHost: true             # Force SSL Host header
        stsSeconds: 315360000          # HSTS max-age (seconds)
        stsIncludeSubdomains: true     # HSTS includeSubDomains
        stsPreload: true               # HSTS preload
        forceSTSHeader: true           # Force STS header even for non-TLS
        frameDeny: true                # X-Frame-Options: DENY
        customFrameOptionsValue: ""    # Custom X-Frame-Options value (overrides frameDeny)
        contentTypeNosniff: true       # X-Content-Type-Options: nosniff
        browserXssFilter: true         # X-XSS-Protection: 1; mode=block
        customBrowserXSSValue: ""      # Custom X-XSS-Protection value
        contentSecurityPolicy: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        contentSecurityPolicyReportOnly: ""
        publicKey: ""                  # HPKP public key (deprecated, avoid)
        referrerPolicy: "strict-origin-when-cross-origin"
        permissionsPolicy: "camera=(), microphone=(), geolocation=()"  # Feature-Policy equivalent
        isDevelopment: false           # Disables Host header checking for dev

        # --- Request/Response Modification ---
        allowedHosts:
          - "example.com"
          - "api.example.com"          # Reject if Host not in this list
        customBrowserXSSValue: ""
        sslProxyHeaders:
          X-Forwarded-Proto: "https"   # Trust this header for SSL detection
```

## Request Lifecycle

### Retry

Retries requests on connection failures.

```yaml
http:
  middlewares:
    retry:
      retry:
        attempts: 3                    # Number of retry attempts (REQUIRED)
        initialInterval: 100ms         # Initial backoff interval
```

- Retries only on network errors, not HTTP status codes
- Requests with body are NOT retried (safety measure for non-idempotent POSTs)

### CircuitBreaker

Prevents requests to unhealthy services.

```yaml
http:
  middlewares:
    cb:
      circuitBreaker:
        expression: "NetworkErrorRatio() > 0.5"  # REQURIED
        checkPeriod: 100ms
        fallbackDuration: 300s         # Time in half-open state before full recovery
        recoveryDuration: 10s          # Time before attempting recovery
```

Available expressions:
- `NetworkErrorRatio()` — ratio of network errors (connection refused, timeout, DNS failure)
- `ResponseCodeRatio(min, max, divisorMin, divisorMax)` — ratio of status codes in range
- `LatencyAtQuantileMS(quantile)` — latency at given quantile (e.g., 50.0 for median)
- `Count40x() / Count50x() / CountGateway()` — HTTP status code counters
- Combine with `&&`, `||`, comparison operators

Examples:

```yaml
expression: "NetworkErrorRatio() > 0.5"          # 50%+ network errors
expression: "ResponseCodeRatio(500, 599, 0, 600) > 0.2"  # 20%+ 5xx
expression: "LatencyAtQuantileMS(50.0) > 5000"   # Median latency > 5s
expression: "NetworkErrorRatio() > 0.1 || ResponseCodeRatio(500, 599, 0, 600) > 0.2"
```

### Buffering

Buffers request/response bodies before forwarding.

```yaml
http:
  middlewares:
    buf:
      buffering:
        maxRequestBodyBytes: 10485760    # 10MB max request body in memory
        memRequestBodyBytes: 2097152     # 2MB in-memory limit before spilling to disk
        maxResponseBodyBytes: 10485760   # 10MB max response body in memory
        memResponseBodyBytes: 2097152    # 2MB in-memory limit before spilling to disk
        retryExpression: "IsNetworkError() && Attempts() < 3"  # Retry conditions
```

### Errors

Defines custom error pages for specific status codes.

```yaml
http:
  middlewares:
    err-pages:
      errors:
        status:
          - "500-599"
          - "400-404"
        service: "error-service@file"   # Service that serves error pages
        query: "/error-pages/{status}.html"  # Query to the error service
```

**How it works:** When a backend returns a status matching the range, the client's request is re-routed to the error service. The error service receives a modified request with the path specified in `query`.

### Compress

Compresses responses using gzip.

```yaml
http:
  middlewares:
    gzip:
      compress:
        excludedContentTypes:           # Don't compress these
          - "text/event-stream"
          - "image/png"
          - "image/jpeg"
        minResponseBodyBytes: 1024      # Minimum size to compress
        defaultEncoding: "gzip"         # or "deflate", "zstd" (v3)
```

### ContentType

Prevents Traefik from auto-detecting Content-Type from response body.

```yaml
http:
  middlewares:
    no-sniff:
      contentType: {}
```

- Just setting this middleware prevents Go's `http.DetectContentType()` from running
- Forces backend to set explicit Content-Type

## Authentication & Protocol

### PassTLSClientCert

Passes the TLS client certificate to the backend via headers.

```yaml
http:
  middlewares:
    pass-cert:
      passTLSClientCert:
        pem: true                             # Pass PEM-encoded cert
        info:
          notAfter: true                      # Include expiry date
          notBefore: true                     # Include issue date
          sans: true                          # Include Subject Alternative Names
          subject:
            commonName: true
            country: true
            domainComponent: true
            locality: true
            organization: true
            organizationalUnit: true
            province: true
            serialNumber: true
          issuer:
            commonName: true
            country: true
            domainComponent: true
            locality: true
            organization: true
            organizationalUnit: true
            province: true
            serialNumber: true
```

### GrpcWeb

Converts gRPC-web requests to gRPC (HTTP/2) for backends.

```yaml
http:
  middlewares:
    grpcweb:
      grpcWeb:
        allowOrigins:
          - "*"
```

### EncodedCharacters

Controls handling of encoded characters in request paths.

```yaml
http:
  middlewares:
    encode-check:
      encodedCharacters:
        allowEncodedSlash: false
        allowEncodedBackSlash: false
        allowEncodedNullCharacter: false
        allowEncodedSemicolon: false
        allowEncodedPercent: false
        allowEncodedQuestionMark: false
        allowEncodedHash: false
```

## Combining Middleware

### Chain

Groups multiple middlewares into a reusable chain.

```yaml
http:
  middlewares:
    standard-chain:
      chain:
        middlewares:
          - "ratelimit"
          - "auth"
          - "sec-headers"

# Reference the chain as a single middleware
http:
  routers:
    app:
      rule: "Host(`app.example.com`)"
      middlewares:
        - "standard-chain"
        - "custom-middleware"          # Chain + additional middleware
```

## Middleware Execution Order

When multiple middlewares are attached to a router, they execute in the order listed. Common ordering patterns:

1. **Rate limiting** — apply limits early before expensive processing
2. **IP allowlist** — block IPs before any processing
3. **Authentication** — verify identity before processing
4. **Headers** — modify headers after identity is established
5. **AddPrefix / StripPrefix** — adjust path before routing
6. **Redirect** — redirect before backend processing
7. **Compress** — compress the response on the way back
8. **Errors** — final error page handling
9. **Retry / CircuitBreaker** — at the service level

## Middleware Scope

Middlewares declared via Docker labels are scoped to that Docker provider. They are NOT accessible from other providers unless qualified with the provider namespace.

```yaml
# Reference a middleware from the "file" provider in a Docker router
labels:
  - "traefik.http.routers.app.middlewares=my-mw@file"

# Reference a middleware from the current provider (Docker)
labels:
  - "traefik.http.routers.app.middlewares=my-mw"
```

When using the File provider, middlewares defined in that file are accessible by name without namespace. To reference Docker-defined middlewares from a File provider router, use the `@docker` suffix.
