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
| Deprecated field removals | Various | Strictly enforced removal |

## Rule Syntax Changes

The v3 rule syntax is the default. If you have v2 rules, they'll get a deprecation warning.

### Host Wildcard

```yaml
# v2 — required HostRegexp for wildcards
rule: "HostRegexp(`.+\.example\.com`)"

# v3 — native wildcard support (preferred)
rule: "Host(`*.example.com`)"
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
      rule: "HostRegexp(`.+\.example\.com`)"
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

## TLS Certificate Fallback

In v3, when no TLS certificate matches the requested SNI, Traefik v3 returns a certificate error instead of falling back to a default certificate. Configure a default certificate explicitly:

```yaml
tls:
  stores:
    default:
      defaultCertificate:
        certFile: "/certs/default.pem"
        keyFile: "/certs/default-key.pem"
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

## Migration Steps

1. **Update static config** — review all entryPoints, providers, and TLS settings
2. **Update rule syntax** — replace `HostRegexp` wildcards with `Host(*)`, remove wildcards from `Path` matchers
3. **Check TLS defaults** — verify min TLS version compatibility with clients
4. **Update ServersTransport** — rename `insecure` to `insecureSkipVerify`
5. **Test with staging** — use `core.defaultRuleSyntax: v2` during migration and test each router
6. **Add default certificate** — if you relied on the TLS fallback behavior
7. **Test** — run a staging instance alongside v2, verify all routes work
