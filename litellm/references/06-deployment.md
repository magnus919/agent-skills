# LiteLLM Deployment: Docker, Compose, Kubernetes, Scaling, Upgrades

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/deploy ,
> https://docs.litellm.ai/docs/proxy/prod ,
> https://docs.litellm.ai/docs/proxy/docker_quick_start ,
> https://docs.litellm.ai/docs/proxy/docker_image_security

This reference covers running the proxy in production: images and pinning, the two
data stores and what breaks without them, Compose/Kubernetes/Helm patterns,
multi-instance mechanics, migrations, and upgrade/rollback practice. Scope: the
LiteLLM-specific layer; cluster fundamentals belong to `kubernetes` /
`docker-compose`.

## Images and pinning

```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml \
  -e DATABASE_URL=... -e LITELLM_MASTER_KEY=sk-... -e LITELLM_SALT_KEY=sk-... \
  -p 4000:4000 ghcr.io/berriai/litellm:v1.97.0 --config /app/config.yaml
```

- Registries: `ghcr.io/berriai/litellm` (Helm default) mirrored at
  `docker.litellm.ai/berriai/litellm`. Variants include `-database` (bundled Prisma
  toolchain) and `-non_root`.
- Tag policy since 1.84.0: plain semver (`vX.Y.Z`), immutable and cosign-signed.
  The `-stable`/`-nightly` suffix scheme is gone; `main-latest` is deprecated —
  never ship it. Pin tag or digest; verify signatures:
  `cosign verify --key https://raw.githubusercontent.com/BerriAI/litellm/<commit>/cosign.pub ghcr.io/berriai/litellm:<tag>`.
- Support policy: only the four most recent stable minor lines receive updates.

## Core environment

```bash
DATABASE_URL="postgresql://.../litellm"   # keys, teams, spend, budgets, UI state
LITELLM_MASTER_KEY="sk-..."               # admin credential + UI password
LITELLM_SALT_KEY="sk-..."                 # encrypts DB-stored provider credentials
STORE_MODEL_IN_DB="True"                  # manage models via UI/API (DB overlay)
DISABLE_SCHEMA_UPDATE="true"              # pods never migrate; a migration job does
```

`LITELLM_SALT_KEY` must be set once and **never rotated** after models are added —
stored credentials become unreadable, with no migration path.

## Data stores and what breaks without them

| Store | Used for | Without it |
|---|---|---|
| PostgreSQL | Keys, teams, users, spend logs, budgets, config-in-DB, UI state | No virtual keys/spend/budgets; master-key-only auth; budgets fail open |
| Redis >=7 | Cross-instance rate-limit counters, router cooldowns/usage, response cache, auth cache | Per-instance state only; "works on pod 1, fails on pod 2" bugs |

## Docker Compose quickstart

The one-line bootstrap (`curl -sSL https://docs.litellm.ai/docker-compose.yml |
docker compose -f - up -d`) starts gateway + Postgres; log into `/ui` as `admin`
with the master key. For anything beyond evaluation, write your own compose file
with: pinned image tag, Postgres healthcheck plus
`depends_on: {condition: service_healthy}` to avoid the Prisma cold-start race, env
files outside git, and a named volume for Postgres data.

## Kubernetes / Helm

Two official charts:

1. **Monolithic** `litellm-helm`:
   `helm install litellm oci://ghcr.io/berriai/litellm-helm -f values.yaml`.
   Supports HPA or KEDA (mutually exclusive), PDBs, ServiceMonitor, graceful drain,
   and a migrations Job hook. Chart versions track LiteLLM releases.
2. **Microservices** chart (from v1.89.0): gateway (:4000) + backend (:4001) +
   ui (:3000) scaled independently; requires external Postgres/Redis; pin chart
   versions that resolve to existing component image tags.

Both charts run migrations via Job with `DISABLE_SCHEMA_UPDATE=true` on pods.
Probes: use `/health/liveliness` for liveness and `/health/readiness` for readiness;
readiness reports 503 while the DB is unreachable, which is exactly what you want
traffic to avoid. Raw-manifest equivalents are documented upstream; Terraform
modules exist for AWS (ECS Fargate/Aurora/ElastiCache/ALB) and GCP
(Cloud Run/Cloud SQL/Memorystore).

## Multi-instance mechanics

- Stateless gateway replicas share Postgres + Redis and run the same master key;
  cooldowns and rate-limit counters live in Redis
  (`router_settings.redis_host/port/password`). Config-in-DB sync across pods is
  polling (`proxy_config_reload_interval_seconds`, default 30).
- Background jobs register per worker process; without coordination they run on
  every pod. Split traffic from jobs with `LITELLM_JOB_ROLE=serving` on serving
  pods plus one dedicated `LITELLM_JOB_ROLE=worker` replica so budget resets and
  cleanups execute once. Stagger jobs after rollouts with
  `scheduled_job_stagger.window_seconds`.
- Connection math: Prisma pool is per worker — size it
  `MAX_DB_CONNECTIONS / (instances x workers)` (default pool 10). A default Helm
  `maxReplicas=100` can demand ~1000 connections; derive maxReplicas from DB
  capacity instead.
- Spend writes batch (`proxy_batch_write_at`); at high RPS enable the Redis
  transaction buffer and watch its queue gauges.

## Workers, sizing, runtime hygiene

- One Uvicorn worker per pod on Kubernetes (`--num_workers 1`) so CPU-based HPA
  reads cleanly; on VMs size workers to vCPUs. Memory floor ~4Gi per worker (the
  Prisma engine high-water mark ratchets); recycle long-running workers with
  `--max_requests_before_restart`. Autoscale on CPU (~60% target); leave memory
  targets unset because of the ratchet.
- `LITELLM_MODE=PRODUCTION` disables `.env` loading; JSON logs via
  `json_logs: true`; keep `LITELLM_LOG=ERROR` in prod.
- Non-root / read-only rootfs is fully supported: non-root image variant or
  `runAsNonRoot` + `readOnlyRootFilesystem` with writable emptyDirs for UI assets,
  migration dir, and cache paths (documented in the production checklist).
- Graceful degradation options: `allow_requests_on_db_unavailable` (requests
  proceed during DB outages; use deliberately) and the drain endpoint for K8s
  preStop hooks (keep the port cluster-internal).

## Migrations and upgrades

- `prisma migrate deploy` runs at startup by default (no shadow DB, no drift
  detection). In orchestrated deployments prefer a dedicated migration job (Helm
  PreSync/ArgoCD hook) with `DISABLE_SCHEMA_UPDATE=true` on all serving pods.
  Migration files ship in the `litellm-proxy-extras` package, so older cores keep
  their own migrations during rolling upgrades.
- Upgrade path: read release notes for the full version span (breaking commits are
  marked with `!`), take a DB backup before migrating, rehearse on a scratch
  instance with real config, then roll serving pods forward keeping the jobs
  deployment in lockstep. Rollback = previous pinned image + previous config
  record; do not assume cross-version config compatibility without re-validation.
- Behavioral changes recent enough to bite upgrades: `/metrics` auth default flipped
  in 1.85.0; team-key budget hierarchy churned across 1.94.0–1.95.0; deprecated
  flags (`USE_PRISMA_MIGRATE`, `set_verbose`) were removed.

## Verification at the delivery boundary

- Pods pass `/health/liveliness` and `/health/readiness`; readiness failing means
  fix the DB first, not the probes.
- `scripts/litellm-health --check models --key <key>` lists expected aliases through
  the service route (not just inside the cluster).
- One representative request returns tokens; `x-litellm-version` matches the pinned
  tag you intended to deploy.
