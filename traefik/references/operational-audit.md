# Traefik Operational Audit

Full-stack audit methodology for evaluating a running Traefik deployment. Covers what to check, which commands to run, and how to classify findings.

## Audit Flow

Run these phases in order. Each builds on the previous. **Shortcut:** Start with Phase 4 — `/api/rawdata` returns the complete runtime state (routers, middlewares, services, TCP middlewares) in one JSON blob. Cross-reference what's actually running against what the static/dynamic config claims, then work backward through phases to trace discrepancies. A full audit takes ~15 minutes starting from rawdata vs ~40 minutes starting from static config — and catches runtime-only issues like duplicate middleware applications that static config review misses.

### Phase 1 — Surface Inventory

Identify what's running and where config lives.

```bash
# What's running
ssh $HOST "docker ps --filter name=traefik --format '{{.Names}} {{.Image}} {{.Status}}'"

# Compose file location
ssh $HOST "docker compose ls --format json | python3 -c \"import json,sys; [print(p['Name'], p['ConfigFiles']) for p in json.load(sys.stdin) if 'traefik' in p['Name'].lower()]\""

# Restart policy and mounts
ssh $HOST "docker inspect traefik --format '{{json .HostConfig.RestartPolicy}}'"
ssh $HOST "docker inspect traefik --format '{{json .Mounts}}' | python3 -m json.tool"
```

### Phase 2 — Static Configuration

Pull the full static config from the running container.

```bash
ssh $HOST "docker exec traefik cat /etc/traefik/traefik.yml"
```

Key things to check:
- `exposedByDefault: false` (should be false)
- `api.insecure: true` — if true, check whether port 8080 is mapped in compose. Even if not mapped, prefer `false` unless debugging
- `api.dashboard: true` — check whether auth middleware is applied to the dashboard router
- `log.level` — should be `info` or `warn` in production, not `debug`
- `certificatesResolvers` — DNS-01 preferred for homelab/internal services
- Entrypoint-level middlewares — apply baseline protection (security headers, rate limiting) to all routers
- `forwardedHeaders.trustedIPs` — should include LAN and any upstream proxy ranges

### Phase 3 — Dynamic Configuration

List all files loaded by the file provider and pull their contents.

```bash
# List dynamic config files
ssh $HOST "docker exec traefik ls /etc/traefik/dynamic/"

# Pull all dynamic configs
ssh $HOST "docker exec traefik sh -c 'for f in /etc/traefik/dynamic/*.yml /etc/traefik/dynamic/*.yaml; do echo \"--- \$f ---\"; cat \$f; done'"
```

Key things to check:
- **Extension-less files are silently ignored** — `providers.file.directory` only watches `.yml`, `.yaml`, and `.toml`. A file named `default` (no extension) is dead config. Check for these: `ls /etc/traefik/dynamic/ | grep -v '\\.'`. If found, either delete or rename with an extension.
- **Naming collisions across files** — if two files define the same middleware name (e.g., `default` as a chain in `config.yml` and `default` as bare headers in another file), the last file alphabetically wins and silently overwrites the earlier definition. This can replace a middleware chain with a single middleware. Cross-reference middleware names across all dynamic files.
- Duplicate router names across files — undefined behavior
- Middleware definitions — chains, forwardAuth, rate limiting, security headers
- Backend URLs — hardcoded IPs are single points of failure
- Inconsistent indentation — doesn't affect functionality but signals maintenance debt

### Phase 4 — Runtime State via API

Query the API for the actual running router/middleware/service state. **Prefer `/api/rawdata`** — it returns a single JSON blob with all routers, middlewares, services, and TCP middlewares. This is the single most useful endpoint for auditing and resolves ambiguity from static/dynamic config review.

```bash
# Complete runtime state (routers, middlewares, services, TCP middlewares)
ssh $HOST "docker exec traefik wget -qO- http://localhost:8080/api/rawdata | python3 -m json.tool"

# Inspect a specific router's effective middlewares
ssh $HOST "docker exec traefik wget -qO- http://localhost:8080/api/http/routers/NAME@file | python3 -m json.tool"

# List all middlewares and their usedBy routers
ssh $HOST "docker exec traefik wget -qO- http://localhost:8080/api/rawdata | python3 -c \"
import json, sys
data = json.load(sys.stdin)
for name, mw in data.get('middlewares', {}).items():
    used = mw.get('usedBy', [])
    print(f'{name} → used by: {used[:5]}{\"...\" if len(used) > 5 else \"\"}'  if used else f'{name} → unused')
\""
```

**Duplicate middleware detection:** Look for router middleware arrays like `["default@file","default@file"]`. This means the same middleware is applied both at the entrypoint level (static config) AND via Docker labels or file config on the specific router — the chain executes twice. This wastes cycles and, for rate limiting, doubles the effective limits. The fix: remove the explicit declaration from the service/router config; the entrypoint already provides it.

### Phase 5 — Logs

Check for errors, warnings, and patterns.

```bash
# Recent logs
ssh $HOST "docker logs traefik --tail 50"

# Filter errors and warnings
ssh $HOST "docker logs traefik --since 24h 2>&1 | grep -E 'level\":\"(error|warn)'"
```

Key patterns to recognize:
- `maxResponseBodySize is not configured` — forwardAuth middleware missing size limit; DoS vector
- `context deadline exceeded` on health checks — timeout too short or endpoint doesn't respond
- `server misbehaving` on DNS lookups — container DNS misconfiguration
- `context canceled` on forwardAuth calls — usually client-side disconnect, not a server issue (check container uptime before investigating)
- `Error calling http://oauth:4181` — forwardAuth backend unreachable; check container health

### Phase 6 — Live Verification

Test critical endpoints directly.

```bash
# Dashboard accessibility (should return 401 if auth is configured)
ssh $HOST "curl -sk -o /dev/null -w '%{http_code}' https://traefik.$DOMAIN/dashboard/"

# Health check endpoints for services with health checks configured
ssh $HOST "curl -sv --connect-timeout 5 --max-time 15 http://$BACKEND_IP:$PORT/health 2>&1"

# DNS from inside the container
ssh $HOST "docker exec traefik wget -qO- --timeout=5 https://update.traefik.io 2>&1"
```

## Classification Framework

| Grade | Criteria |
|-------|----------|
| **HIGH** | Security exposure (no auth on sensitive endpoints), active DoS vectors, duplicate router definitions |
| **MEDIUM** | Failing health checks, DNS issues, intermittent errors, stale backups |
| **LOW** | Cosmetic (indentation, stale password files, commented-out features) |

**Rule of thumb for LOW findings:** Ask "does this cause operational harm or security exposure right now?" If no, it's LOW or skip it entirely. A 4-year-old `.htpasswd` file is not a vulnerability — it's a note. Access logs being disabled is a choice, not a bug.

### What to skip

These are NOT problems:
- `tls.yml.old` or backup files outside the `dynamic/` directory (not loaded by file provider)
- `.htpasswd` file age (unless credentials are compromised)
- Inconsistent indentation in YAML (zero functional impact)
- Disabled access logs or tracing (intentional configuration choice)
- `acme.json` modification date within 60 days (LE renews at 30 days before expiry)
- Multiple containers with same labels during rolling deploys (zero-downtime pattern)

## Middleware Audit Scoring

When rating a middleware configuration, score three independent axes. Each axis gets point values for what's present and deductions for what's missing or misconfigured.

### Security (100 pts)

| Check | Points |
|-------|--------|
| TLS configured (ACME or static certs) | +10 |
| HSTS with subdomains + preload | +10 |
| DNS-01 ACME (no port 80 exposed) | +5 |
| `exposedByDefault=false` on Docker provider | +5 |
| Rate limiting at entrypoint covers all services | +10 |
| In-flight request limiting | +5 |
| OAuth/ForwardAuth on sensitive services | +10 |
| Dashboard behind auth (BasicAuth or OAuth) | +5 |
| `forwardedHeaders.trustedIPs` limited to LAN/proxy ranges | +5 |
| IP allowlist for internal-only endpoints | +5 |

| Deduction | Points |
|-----------|--------|
| `api.insecure: true` (host-mapped port 8080) | -15 |
| `api.insecure: true` (container-only, no host mapping) | -8 |
| No CSP configured | -5 |
| No Permissions-Policy configured | -3 |
| No `frameDeny` or `X-Frame-Options` | -3 |
| Access logs disabled | -3 |
| No CrowdSec/fail2ban threat intelligence | -3 |

### Performance (100 pts)

| Check | Points |
|-------|--------|
| HTTP/3 enabled | +10 |
| Compression (gzip + brotli + zstd) | +15 |
| Rate limiting prevents abuse without blocking LAN | +10 |
| In-flight request limiting | +10 |
| Prometheus metrics with custom buckets | +10 |
| JSON structured logging | +5 |
| Health checks on services | +5 |
| CurveP256 preferred over CurveP384 (2-4x faster, equivalent security) | +10 |

| Deduction | Points |
|-----------|--------|
| No `serversTransport` tuning (pool size, timeouts) | -5 |
| No keep-alive tuning | -3 |
| CurveP384 preferred without CurveP256 (slower handshakes) | -5 |
| No passive health checks on most services | -2 |

### Correctness (100 pts)

| Check | Points |
|-------|--------|
| Entrypoint-level middleware applied consistently | +15 |
| Chain order correct (headers → compress → rate-limit → inflightreq) | +15 |
| LAN exclusions on rate-limit and inflightreq | +10 |
| OAuth on appropriate services, not over-applied | +10 |
| Dashboard behind auth | +10 |
| TLS resolver properly configured and referenced | +10 |
| HTTP→HTTPS redirect | +5 |

| Deduction | Points |
|-----------|--------|
| Duplicate middleware in router arrays (`default@file` twice) | -8 |
| Dead config files (extension-less, `.old` in dynamic dir) | -3 |
| Middleware defined but never used (commented out of chain) | -3 |
| Duplicate router definitions across providers | -5 |

## Post-Fix Verification

After applying fixes:
1. Check logs for clean state: `docker logs traefik --since 2m | grep -E 'ERROR|WARN'`
2. Verify auth on protected endpoints: `curl -sk -o /dev/null -w '%{http_code}' $URL` → expect 401
3. Verify no duplicate routers via API
4. For compose label changes, run `docker compose up -d` to re-apply labels (may recreate container)
5. For file provider changes, no restart needed — `watch: true` picks them up

## DNS Debugging Pattern

If the Traefik container shows `server misbehaving` on DNS lookups (127.0.0.11:53):
1. Check Docker daemon DNS config: `cat /etc/docker/daemon.json | python3 -m json.tool`
2. If Tailscale or a VPN is interfering, set explicit DNS: `{"dns": ["1.1.1.1", "8.8.8.8"]}`
3. Restart Docker after daemon.json changes
4. Recreate the Traefik container to pick up new DNS settings (old containers may cache bad DNS)
5. Verify: `docker exec traefik wget -qO- --timeout=5 https://update.traefik.io`
