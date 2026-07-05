# HTTP Routing Reference

HTTP routers match incoming requests against rules and forward them to services through optional middleware chains.

## Rule Matchers

Rules are defined using backtick-delimited values. Multiple matchers combine with `&&` (AND), `||` (OR), `!` (NOT), and parentheses.

### Host and HostRegexp

```yaml
# Exact host match
rule: "Host(`example.com`)"

# Wildcard (single-level, v3 syntax only)
rule: "Host(`*.example.com`)"     # matches foo.example.com, NOT foo.bar.example.com

# Catch-all
rule: "Host(`*`)"                 # matches every request

# Regex-based match
rule: "HostRegexp(`^.+\\.example\\.com$`)"
```

Rules for `Host` and `HostRegexp`:
- Wildcard `*.example.com` matches exactly one subdomain label
- A bare `*` is a catch-all (not a subdomain wildcard)
- Host matchers are case-insensitive
- Non-ASCII domains must use punycode encoding
- If no `Host` header exists, Traefik checks the request URL's host

### Path, PathPrefix, and PathRegexp

```yaml
# Exact path
rule: "Path(`/api/v1/users`)"

# Path prefix
rule: "PathPrefix(`/api`)"

# Regex path
rule: "PathRegexp(`^/api/v[0-9]+/users$`)"
```

- Paths always start with `/`, except for `PathRegexp`
- `Path` matches exact path only
- `PathPrefix` matches any path starting with the prefix

### Header and HeaderRegexp

```yaml
rule: "Header(`Content-Type`, `application/json`)"
rule: "Header(`X-Api-Key`, `secret`)"

# Case-insensitive regex match
rule: "HeaderRegexp(`Content-Type`, `(?i)^application/(json|yaml)$`)"
```

### Method

```yaml
rule: "Method(`GET`)"
rule: "Method(`GET`, `POST`, `PUT`)"
```

### Query and QueryRegexp

```yaml
rule: "Query(`page`, `1`)"
rule: "QueryRegexp(`version`, `^v\\d+$`)"
```

### ClientIP

```yaml
rule: "ClientIP(`10.0.0.0/24`)"
rule: "ClientIP(`192.168.1.100`)"
```

- Matches the actual client IP, NOT the `X-Forwarded-For` header
- Supports IPv4, IPv6, and CIDR notation

### Combined Rules

```yaml
# Complex expressions with logical operators
rule: "Host(`api.example.com`) && PathPrefix(`/v2`)"
rule: "Host(`app.example.com`) && (Method(`GET`) || Method(`POST`))"
rule: "!(Host(`internal.example.com`)) && PathPrefix(`/public`)"
rule: "Host(`example.com`) && Header(`X-Region`, `us-east`)"
```

## Router Configuration

```yaml
# Dynamic config (File provider YAML)
http:
  routers:
    api:
      rule: "Host(`api.example.com`) && PathPrefix(`/v1`)"
      entryPoints:
        - "websecure"
      middlewares:
        - "auth"
        - "ratelimit"
      service: "api-backend"
      tls:
        certResolver: "letsencrypt"
        options: "mytlsoptions@file"
        domains:
          - main: "api.example.com"
      priority: 100
      ruleSyntax: "v3"        # v3 or v2 (default: v3)
      observability:
        metrics: true
        accessLogs: true
        tracing: true
```

## Priority

Routers are sorted by priority (highest first). By default, priority equals the **length of the rule string**. Longer rules get higher priority.

```yaml
# Explicit priority overrides the default
http:
  routers:
    specific:
      rule: "Host(`foobar.example.com`)"
      priority: 100            # Will be matched before the generic one below
    generic:
      rule: "HostRegexp(`[a-z]+\\.example\\.com`)"
      priority: 10
```

Priority rules:
- Explicit `priority: 0` is IGNORED (uses default length-based sorting)
- Negative priorities are supported
- Max user priority: `MaxInt32 - 1000` for 32-bit, `MaxInt64 - 1000` for 64-bit
- Positive priority = higher number wins
- When routers from DIFFERENT providers have the same priority, `providers.precedence` decides

## Multi-Layer Routing

Traefik v3 supports multi-layer routing — splitting the request flow across two routers at different layers. The first router matches and middleware-runs at one `entryPoint`, then the second router at another entryPoint handles the same request for deeper routing.

```yaml
# Layer 1: External entry point handles TLS and auth
http:
  entryPoints:
    websecure:
      address: ":443"
      http:
        tls: true
        middlewares:
          - "ratelimit@file"
          - "ipallowlist@file"

  routers:
    router1:                    # On websecure: TLS termination, rate limit,
      rule: "Host(`api.example.com`)"
      entryPoints: ["websecure"]
      middlewares: ["cors", "auth"]
      service: "router2@internal"  # Passes to router2 on internal entrypoint

    router2:                    # On internal: no TLS, deeper path routing
      rule: "PathPrefix(`/api/v2`)"
      entryPoints: ["internal"]
      service: "v2-backend"

    router3:
      rule: "PathPrefix(`/api/v1`)"
      entryPoints: ["internal"]
      service: "v1-backend"
```

## Rules Syntax: v3 vs v2

The v3 rule syntax is the default. Key changes from v2:

- **Wildcard support** in `Host()` matcher — `Host(`*.example.com`)` works natively (was `HostRegexp` only)
- **Deprecated** `ruleSyntax` option per-router — use the `core.defaultRuleSyntax` global option to override

## Notes

- Single quotes `'` are NOT accepted in rule values — use backticks `` ` `` or escaped double quotes `\"`
- Regex values use Go's `regexp` package syntax
- The character `@` is not allowed in router names
- Routers can reference services from other providers using the `@provider` suffix (e.g., `api@internal` for the Traefik API service)
