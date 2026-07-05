# v2 to v3 Migration Reference

This covers the key changes when migrating from Traefik v2 to v3. Full details: https://doc.traefik.io/traefik/migrate/v2-to-v3/

## Quick Summary of Breaking Changes

| Change | v2 | v3 |
|--------|-----|-----|
| Default rule syntax | v2 | v3 |
| TLS min version default | TLS 1.0 | TLS 1.2 |
| `Path` matcher wildcards | Supported | Removed (use `PathRegexp` or `PathPrefix`) |
| `insecure` field renamed | N/A | `tls.insecureSkipVerify` on serversTransport |
| X-Forwarded-For behavior | Always appended | Configurable via `forwardedHeaders` |
| Tracing providers | Jaeger, Zipkin, Datadog, Elastic | OpenTelemetry (OTLP) only |
| Content-Type handling | Auto-detected | Must use `ContentType` middleware |
| IPWhiteList renamed | `IPWhiteList` | `IPAllowList` |
| Provider removals | Marathon, Rancher v1, InfluxDB v1, Pilot | Removed entirely |
| `tls.caOptional` | Available | Removed from all providers |
| Deprecated field removals | Various | Strictly enforced — v3 refuses to start with deprecated fields |

## Pre-Migration Audit Checklist

Before upgrading, run through these checks:

- [ ] **Rule syntax audit** — Search config files for `HostRegexp` with wildcard patterns (`.+\.`); replace with `Host(`*.`)`
- [ ] **Path wildcard audit** — Search for curly-brace path patterns like `/api/{version:...}`; these need `PathRegexp` replacements
- [ ] **TLS compatibility check** — Verify clients support TLS 1.2+ (default changed from TLS 1.0)
- [ ] **ServersTransport rename** — Replace all `insecure: true` with `insecureSkipVerify: true`
- [ ] **Tracing migration** — If using Jaeger/Zipkin/Datadog/Elastic APM, migrate to OpenTelemetry
- [ ] **ContentType audit** — If you relied on Traefik auto-detecting Content-Type, add the `ContentType` middleware
- [ ] **IPWhiteList → IPAllowList** — Rename any `ipWhiteList` config blocks to `ipAllowList`
- [ ] **Remove deprecated providers** — If using Marathon, Rancher, InfluxDB v1 metrics, or Pilot, find alternatives
- [ ] **Default certificate** — If you relied on SNI fallback, configure a default certificate explicitly
- [ ] **Test in staging** — Run a v3 instance alongside v2 with `core.defaultRuleSyntax: v2` for gradual migration

## Rule Syntax Changes

The v3 rule syntax is the default. If you have v2 rules, they'll get a deprecation warning.

### Host Wildcard

```yaml
# v2 — required HostRegexp for wildcards
rule: "HostRegexp(`.+\\.example\\.com`)"

# v3 — native wildcard support (preferred)
rule: "Host(`*.example.com`)"     # matches foo.example.com, NOT foo.bar.example.com
```

### Path Wildcards Removed

```yaml
# v2 — Path supported wildcards
rule: "Path(`/api/{version: v[0-9]+}/users`)"

# v3 — Path no longer supports wildcards, use PathRegexp
rule: "PathRegexp(`/api/v[0-9]+/users`)"
```

### Migrating Rules

To use v2 syntax during migration, set per-router:

```yaml
http:
  routers:
    legacy-router:
      rule: "HostRegexp(`.+\\.example\\.com`)"
      ruleSyntax: "v2"              # Per-router override
```

Or globally in static config:

```yaml
core:
  defaultRuleSyntax: "v2"
```

## TLS Changes

```yaml
# v3 default TLS security is higher
tls:
  options:
    default:
      # minVersion default changed from VersionTLS10 to VersionTLS12
      minVersion: VersionTLS12
```

### TLS Certificate Fallback

In v3, when no TLS certificate matches the requested SNI, Traefik returns a certificate error instead of falling back to a default certificate. Configure a default certificate explicitly:

```yaml
tls:
  stores:
    default:
      defaultCertificate:
        certFile: "/certs/default.pem"
        keyFile: "/certs/default-key.pem"
```

## Tracing Changes (OTLP Only)

v3 removed direct support for Jaeger, Zipkin, Datadog APM, and Elastic APM tracing. All tracing now goes through OpenTelemetry (OTLP):

```yaml
# v3 — OTLP only
tracing:
  serviceName: "traefik"
  sampleRate: 1.0
  otlp:
    grpc:
      endpoint: "localhost:4317"
      insecure: true
    http:
      endpoint: "localhost:4318"
```

Migrate from Jaeger/Zipkin agents by running an OpenTelemetry Collector as a sidecar that forwards to your existing backend.

## Content-Type Handling

v3 removed automatic Content-Type detection. Responses without an explicit Content-Type header may be handled differently:

```yaml
# v3 — add this middleware to preserve v2 behavior
http:
  middlewares:
    auto-content-type:
      contentType: {}
```

## ServersTransport Changes

The `insecure` field has been renamed for clarity:

```yaml
# v2 — ambiguous
serversTransport:
  insecure: true

# v3 — explicit
serversTransport:
  insecureSkipVerify: true
```

## Docker Provider Changes

```yaml
# v2 — no port spec means ambiguous
traefik.http.services.my-svc.loadbalancer.server.port=80

# v3 — same behavior, but port detection priority updated.
# Always set the port explicitly.
```

## X-Forwarded-For Header

v3 provides more granular control over forwarded headers:

```yaml
entryPoints:
  web:
    address: ":80"
    forwardedHeaders:
      trustedIPs:
        - "10.0.0.0/8"
        - "172.16.0.0/12"
      insecure: false
    # When set to true, Traefik will NOT append client's RemoteAddr to X-Forwarded-For
```

## Provider Removals

The following providers were removed in v3 with no replacement:

| Removed Provider | Alternative |
|-----------------|-------------|
| Marathon | Use File provider or migrate to Kubernetes/Nomad |
| Rancher v1 | Use File provider or Rancher v2's Kubernetes ingress |
| InfluxDB v1 metrics | Use InfluxDB v2 or Prometheus |
| Pilot | Use Traefik Hub or forward auth middlewares |

## Migration Steps

1. **Run the pre-migration audit** — check all 10 items above before changing anything
2. **Update static config** — review all entryPoints, providers, and TLS settings
3. **Update rule syntax** — replace `HostRegexp` wildcards with `Host(*)`, remove wildcards from `Path` matchers
4. **Check TLS defaults** — verify min TLS version compatibility with clients
5. **Update ServersTransport** — rename `insecure` to `insecureSkipVerify`
6. **Migrate tracing** — switch from direct Jaeger/Zipkin to OpenTelemetry
7. **Test with staging** — use `core.defaultRuleSyntax: v2` during migration and test each router
8. **Add default certificate** — if you relied on the TLS fallback behavior
9. **Run a parallel stack** — deploy v3 alongside v2, redirect a subset of traffic, verify all routes work
10. **Cut over** — switch production traffic to v3, keep v2 as rollback target for 48 hours
