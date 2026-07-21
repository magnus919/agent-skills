# CSP / SPA Debugging — Entrypoint Header Overwrite

Debugging guide for the failure mode where an entrypoint-level `headers` middleware
silently breaks cross-origin SPAs by overwriting router-level
Content-Security-Policy headers.

## The Mechanism

Traefik middleware execution order on the response path is the **reverse** of the
request path:

```
Request:  entrypoint middlewares → router middlewares → service middlewares → backend
Response: backend → service middlewares → router middlewares → entrypoint middlewares
```

Entrypoint-level middlewares run **last on the response path**. The `headers`
middleware documentation states:

> "Custom headers will overwrite existing headers if they have identical names."
> — [Traefik Headers middleware docs](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/headers/)

Therefore, when an entrypoint applies a chain containing `contentSecurityPolicy`
(e.g., a `default@file` security-headers chain on `websecure`), it overwrites any
router-level CSP on the response. **Router-level CSP overrides are impossible**
when the entrypoint also sets CSP.

## The Failure

If the entrypoint CSP is generic — typically `default-src 'self'` with no
`connect-src` directive — the browser enforces it and blocks every cross-origin
`fetch`/`XHR` the SPA makes. The SPA's own page and static assets load normally
(they are same-origin), but all API calls to a different origin silently fail.

**The backend logs show zero requests from the SPA.** This is the key tell that
distinguishes this failure from backend issues, network problems, or CORS
misconfiguration on the backend.

## Diagnostic Flow

```
SPA page loads (200) but API calls fail silently
│
├─ 1. Check CSP on the SPA page:
│     curl -D- -o /dev/null https://your-spa.example.com/ | grep -i content-security-policy
│
│   If you see `default-src 'self'` with no `connect-src` → this is the problem.
│   The browser blocks all cross-origin requests.
│
├─ 2. Confirm zero requests reach the backend:
│     Check backend logs for the complete absence of requests from the SPA.
│     (Not 403s, not CORS errors — nothing at all.)
│
├─ 3. Identify the source of the CSP:
│     Check whether the CSP comes from the backend or from Traefik.
│     curl -D- -o /dev/null https://your-backend-api.example.com/ | grep -i content-security-policy
│
│   If the backend emits its own (different) CSP but the SPA page shows a
│   generic one, the entrypoint middleware is overwriting it.
│
└─ 4. Check the entrypoint middleware chain:
      Look at the entrypoint's `http.middlewares` list in static config,
      then trace the chain to find `contentSecurityPolicy` in a headers middleware.
```

## The Fix

Remove `contentSecurityPolicy` from the entrypoint-level default middleware chain.
Let each service emit its own tailored CSP. Many applications (GoToSocial,
Mastodon, Nextcloud, etc.) ship their own CSP headers that are specific to their
needs.

A proxy-wide `default-src 'self'` is actively harmful for any SPA that
communicates with a different origin. The proxy should not impose a CSP that
overrides what the application itself intends.

Other security headers (HSTS, X-Content-Type-Options, X-Frame-Options,
Referrer-Policy) are safe to keep in the entrypoint chain — they do not interfere
with cross-origin API calls.

## CORS Preflight Interception

The `headers` middleware also intercepts CORS preflight requests when CORS headers
are configured:

> "If CORS headers are set, then the middleware does not pass preflight requests
> to any service, instead the response will be generated and sent back to the
> client directly."
> — [Traefik Headers middleware docs](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/headers/)

This is useful when a backend does not handle `OPTIONS` preflight requests (returns
405). Adding a `headers` middleware with `accessControlAllowMethods` and
`accessControlAllowOriginList` to the router handles preflights at the proxy level.

Example:

```yaml
http:
  middlewares:
    cors-preflight:
      headers:
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
          - PATCH
          - OPTIONS
        accessControlAllowOriginList:
          - "*"
        accessControlAllowHeaders:
          - "*"
        accessControlMaxAge: 120
        addVaryHeader: true
```

## Related but Distinct Failures

| Failure | Symptom | Cause |
|---------|---------|-------|
| **CSP overwrite (this guide)** | SPA loads, zero API requests reach backend | Entrypoint `headers` middleware overwrites router CSP |
| **Rate limiting** | SPA loads, 429 errors on asset/API requests | Entrypoint rate limit too low for SPA burst |
| **Double middleware execution** | Doubled rate-limit counts, duplicate compression | Same middleware declared at both entrypoint and router level |

## Sources

- [Traefik Headers middleware](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/headers/) — header overwrite behavior, CORS preflight interception
- [Traefik Middleware overview](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/overview/) — router vs. service middleware execution order
- [Traefik Entrypoints](https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/) — entrypoint-level `http.middlewares` configuration
- [MDN Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy) — `default-src`, `connect-src`, browser enforcement
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) — preflight request mechanics
- [unrolled/secure](https://github.com/unrolled/secure#available-options) — the library Traefik uses for security headers
