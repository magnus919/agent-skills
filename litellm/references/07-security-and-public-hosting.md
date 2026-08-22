# LiteLLM Security and Public-Facing Hosting

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/security_best_practices ,
> https://docs.litellm.ai/docs/proxy/public_routes ,
> https://docs.litellm.ai/docs/proxy/master_key_rotations ,
> https://docs.litellm.ai/blog/cve-2026-42208-litellm-proxy-sql-injection ,
> https://docs.litellm.ai/blog/security-hardening-april-2026 ,
> https://docs.litellm.ai/blog/security-update-march-2026

This reference covers hardening an internet-reachable proxy: the CVE floor, auth
model, route exposure, secrets and salt-key discipline, supply-chain posture,
privacy defaults, and abuse controls. Scope: LiteLLM-specific security; TLS
termination and network plumbing belong to `traefik`/`kubernetes`.

## Version floor: >=1.83.7

Any internet-reachable proxy must run **litellm >=1.83.7** (and Starlette >=1.0.1):

| Vuln | Type | Auth needed | Fixed |
|---|---|---|---|
| CVE-2026-42208 | Pre-auth SQL injection via crafted Authorization header; read/modify DB incl. keys | None (Critical, CISA KEV, actively exploited 2026) | v1.83.7 |
| CVE-2026-42203 | SSTI in `/prompts/test` → code exec in proxy process | Valid key | v1.83.7 |
| CVE-2026-42271 | Command injection in MCP stdio test endpoints | Valid key (CISA KEV) | v1.83.7 |
| CVE-2026-48710 | Starlette host-header bypass; chained with 42271 → unauthenticated RCE | None | Starlette >=1.0.1 + litellm >=1.83.7 |
| CVE-2026-35030 | OIDC userinfo cache collision → session inheritance (only with `enable_jwt_auth`) | None | v1.83.0 |
| CVE-2026-35029 | `/config/update` missing role check → any key could change runtime config | Any key | v1.83.0 |

Two of these sat in CISA KEV during 2026 with exploitation observed within days of
disclosure — a public proxy below the floor should be treated as compromised until
patched and its provider keys rotated.

## Supply-chain posture

- March 2026 incident: backdoored PyPI wheels `litellm==1.82.7` and `1.82.8`
  (~40 minutes; credential stealer harvesting env vars, SSH keys, cloud/k8s creds).
  Official Docker-image users were unaffected. Clean builds resumed at v1.83.0 via a
  rebuilt CI pipeline.
- Consequences for operators: pin exact versions or digests; prefer the cosign-signed
  official images over unpinned pip installs; verify signatures in CI/admission;
  never `pip install litellm` unversioned on a shared host.
- Images are cosign-signed since v1.83.0 with the pinned-commit public key shown in
  every release body.

## Authentication model

- With Postgres connected, clients authenticate with virtual keys; without one, the
  master key is the only credential. Health probes (`/health/liveliness`,
  `/health/readiness`) are deliberately unauthenticated and low-detail.
- Always set a strong random master key (`sk-` + 32+ random bytes). The quickstart's
  `sk-1234` placeholder is fingerprinted by vulnerability scanners, and the login
  page advertises default credentials unless hidden — never ship it beyond throwaway
  local testing.
- The Admin UI is effectively equivalent to holding the master key: restrict it to
  admin networks, prefer SSO (EE beyond 5 users), or set `DISABLE_ADMIN_UI=True` on
  API-only edges.
- Key-management sharp edges: management-route power follows the key **owner's
  role** (an admin-owned virtual key can manage the proxy); `custom_key_generate`
  policy hooks do not run on updates unless paired with `custom_key_update`.
- Enterprise-only auth extras: SSO/SAML/SCIM beyond 5 users, JWT/OIDC auth,
  audit logs, IP allowlists.

## Route exposure

Routes that must never be publicly exposed: `/key/*`, `/user/*`, `/team/*`,
`/config/*`, `/model/*`, `/spend/*`, `/ui`, `/prompts/test`, `/mcp-rest/*`. Each of
these maps to a real incident class above (config write = takeover; prompt-test SSTI;
MCP test command injection).

Route lockdown settings (`public_routes`, `admin_only_routes`, `allowed_routes`)
are **Enterprise** as of this refresh — do not present them as generally available.
The OSS path is enforcing at the reverse proxy: expose only the LLM route groups you
serve plus health probes, and deny management paths at the edge before they reach the
proxy. Terminate TLS at the LB/reverse proxy; never publish port 4000 raw.

## Secrets, salt key, rotations

- Provider credentials live only as `os.environ/VAR` references in config or in a
  secret manager; nothing secret belongs in `config.yaml` or git.
- `LITELLM_SALT_KEY` encrypts DB-stored provider credentials. Set once, store in a
  secret manager, never rotate after adding models (stored data becomes unreadable).
- Master-key rotation: if a salt key is set, rotate by changing the secret and
  restarting — not via the regenerate flow, which would re-encrypt stored
  credentials under a key the proxy then cannot use. Back up the DB before any
  rotation flow.
- Virtual keys are hashed in the DB (hashing survives master-key rotation); instant
  revocation is block/unblock; grace-period regeneration and scheduled rotation are
  Enterprise.
- Keep Postgres and Redis on private subnets with TLS and least-privilege roles —
  `DATABASE_URL` grants direct read/write to keys, budgets, and spend logs.

## Data privacy defaults

- Self-hosting sends nothing to BerriAI; requests do flow to whichever providers are
  configured — residency comes from provider/region choice and guardrails.
- `store_prompts_in_spend_logs` defaults to false; spend logs carry metadata only.
  Enabling it stores full messages/responses per row. The Admin UI Spend Log toggle
  overrides config values at runtime — audit UI state on managed deployments.
- `turn_off_message_logging: true` keeps content out of callbacks;
  `redact_user_api_key_info: true` redacts identity hashes in traces;
  `overwrite_user_with_key_hash: true` stops caller-controlled `user` fields from
  reaching providers.
- Presidio PII masking (OSS) can mask emails/cards/SSNs pre-dispatch — see
  [04-caching-and-guardrails.md](04-caching-and-guardrails.md).

## Abuse and cost control

Budgets and rate limits are abuse controls as much as finance tools — a stolen
gateway key is stolen provider quota:

- Global budget as circuit breaker; per-key caps sized ~2x expected load with alerts
  at 80%; `upperbound_key_generate_params` so self-service cannot out-cap you;
  end-user budgets via `max_end_user_budget_id`; rate limits on every public-facing
  key (admins exempt — test accordingly).
- Budgets require Postgres and fail open without one (see
  [03-keys-teams-budgets-spend.md](03-keys-teams-budgets-spend.md)).
- Slack/email alerting covers budget crossings, DB failures, hanging requests, and
  outages; Prometheus deployment-state metrics catch cooldown cascades.

## Hardening checklist (condensed)

1. Pinned image/digest >=1.83.7, cosign verified, within the supported four-line window.
2. Strong master key from a secret manager; `sk-1234` nowhere; Admin UI restricted or disabled.
3. Scoped virtual keys per workload with expiry, budgets, rpm/tpm; block/unblock ready.
4. Edge exposes only LLM routes + health probes; management paths denied at the proxy; TLS terminated up front.
5. Postgres/Redis private, TLS, least privilege; DB pool bounded by instance math.
6. Salt key set once; documented master-key rotation flow rehearsed; DB backups before migrations.
7. Prompt-retention posture decided explicitly; message logging off where not needed.
8. Budgets + rate limits + alerting live; deployment-state and spend dashboards wired.

## Verification at the delivery boundary

- From outside the trust boundary: management routes return 403/404, health probes
  answer, and no endpoint echoes configuration details.
- `scripts/litellm-health --check readiness` confirms DB connectivity without leaking
  diagnostics; richer diagnostics stay behind auth.
- A revoked (blocked) key fails immediately; a key over its tiny test budget is
  rejected with the documented error.
