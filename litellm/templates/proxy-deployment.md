# LiteLLM Proxy Deployment Record

Fill this record for the runtime deployment: how the proxy runs, where its state
lives, and how it is rolled back. Pair it with the config record
(`proxy-config-record.md`), which captures what the proxy serves.

## Deployment identity

- Requested outcome: _[fill: availability, scale, and exposure requirements]_
- Runtime: _[fill: Docker / docker compose / Kubernetes + Helm / raw manifests]_
- Target and scope confirmed with: _[fill: who confirmed, when]_
- Rollback path: _[fill: previous image tag/digest + previous deployment record]_

## Pinned image

- Image and tag: _[fill: ghcr.io/berriai/litellm:vX.Y.Z — never latest/main-latest]_
- Digest: _[fill: sha256:...]_
- Cosign verification: _[fill: command/CI gate used]_
- Version floor check: _[fill: >=1.83.7 confirmed for public deployments]_
- Component images (microservices chart): _[fill: gateway/backend/ui tags]_

## Runtime shape

- Replicas and worker count: _[fill: --num_workers 1 per pod on K8s]_
- CPU/memory per replica: _[fill: ~1 vCPU / 4Gi floor per worker; memory ratchets]_
- Autoscaling: _[fill: HPA CPU target ~60% or KEDA; maxReplicas bounded by DB pool math]_
- Job role split: _[fill: LITELLM_JOB_ROLE=serving pods + dedicated worker replica]_
- Security context: _[fill: runAsNonRoot, readOnlyRootFilesystem, writable emptyDirs]_

## Network and exposure

- Ports: _[fill: 4000 gateway; 4001 backend; 3000 ui if microservices]_
- Bind address: _[fill: explicit --host; default 0.0.0.0 acknowledged]_
- TLS termination: _[fill: LB/reverse proxy; port 4000 never raw]_
- Edge route policy: _[fill: LLM routes + health probes exposed; management paths denied]_
- Admin UI policy: _[fill: restricted network / SSO / DISABLE_ADMIN_UI]_
- Probes: _[fill: liveness /health/liveliness; readiness /health/readiness; thresholds]_

## Environment (references only — values live in the secret manager)

- `DATABASE_URL`: _[fill: secret reference]_
- `LITELLM_MASTER_KEY`: _[fill: secret reference]_
- `LITELLM_SALT_KEY`: _[fill: secret reference; set once, never rotate]_
- `STORE_MODEL_IN_DB`: _[fill: True/False]_
- `DISABLE_SCHEMA_UPDATE`: _[fill: true on pods when a migration job runs]_
- `LITELLM_JOB_ROLE`: _[fill: serving | worker]_
- Provider keys: _[fill: os.environ/ references only — never values]_

## Data stores

- Postgres: _[fill: endpoint, version, private subnet, TLS, least-privilege role]_
- Redis: _[fill: endpoint, >=7.0, private subnet, TLS; required when >1 replica]_
- Backup/restore: _[fill: schedule, last restore test date]_

## Migrations

- Migration strategy: _[fill: startup default vs dedicated job (Helm PreSync/hook)]_
- DB backup taken before last migration: _[fill: date]_

## Verification checklist

- [ ] `litellm-health --check health --check readiness --json` passes via the service route
- [ ] `x-litellm-version` on a live response matches the pinned tag
- [ ] A representative chat request returns tokens through the public edge
- [ ] Management routes return 403/404 from outside the trust boundary
- [ ] Blocked test key fails immediately (revocation path works)

## Changes from the previous record

- _[fill: what changed, why, and the verification that backs it]_
