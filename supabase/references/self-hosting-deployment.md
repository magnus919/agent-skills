# Self-hosting deployment

Read this before installing, exposing, or materially reconfiguring the official self-hosted Docker stack.

## Capacity and prerequisites

Current official guidance for all default components:

| Resource | Minimum | Recommended |
|---|---:|---:|
| RAM | 4 GB | 8 GB+ |
| CPU | 2 cores | 4 cores+ |
| Disk | 40 GB SSD | 80 GB+ SSD |

Logs/Analytics are optional and increase resource use. Removing Realtime, Storage, imgproxy, or Functions can reduce requirements, but only do so when the product does not need them and the Compose dependencies are reconciled.

Require Linux administration, Git, Docker Engine, Docker Compose, networking/DNS/firewall knowledge, and a backup/recovery destination. Check architecture support for every pinned image on the actual host.

## Use the official release set

The deployment source is `supabase/supabase/docker`. Prefer the official setup script for a new supported Linux host after inspecting it:

```sh
curl -fsSL https://supabase.link/setup.sh -o setup.sh
less setup.sh
sh setup.sh
```

The script fetches current Docker configuration, generates legacy and asymmetric keys, writes URLs, and pulls images. For non-interactive automation, review its current help and pass explicit values or update the generated `.env` before startup; defaults such as localhost are not production configuration.

Manual installation should copy the complete `docker/` directory, including helper scripts, volume initialization files, overrides, changelog, and tests. Do not copy only `docker-compose.yml`.

## Pre-start gate

Before first start:

1. `docker compose config --quiet` succeeds.
2. Every placeholder password/key is replaced using official generators.
3. `.env` and secret-bearing files are owner-readable only and excluded from version control/backups with inappropriate access.
4. `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL` (including `/auth/v1`), `SITE_URL`, and allowed redirects match the intended public topology.
5. Dashboard basic-auth credentials are strong and non-default.
6. Host ports do not conflict and are bound/firewalled intentionally.
7. SMTP and external identity providers are configured if the product depends on them.
8. Persistent database, storage, snippets, functions, and `db-config` locations are included in the backup design.
9. The restore target and rollback path exist before production data arrives.

Use the generated project helper:

```sh
sh run.sh config
sh run.sh compose-config >/dev/null
docker compose config --quiet
sh run.sh start
```

`run.sh start` uses `docker compose up -d --wait`. On a fresh database, Postgres and then Auth, Storage, Realtime, and Supavisor may still be applying first-boot migrations when their initial health retries expire. The helper can exit nonzero while containers continue initializing and later become healthy. Do not restart blindly: inspect logs for forward migration progress, wait for the current initialization to settle, and re-check the complete health set. A persistent failure or migration error needs diagnosis.

## Network and TLS

The default publishes:

- Kong HTTP `8000` and HTTPS `8443`.
- Supavisor session `5432` and transaction `6543`.

For production, place a reverse proxy in front of the API gateway, use a valid certificate, and avoid broad direct database exposure. The official Caddy and Nginx overrides are available:

```sh
sh run.sh config add caddy
# or
sh run.sh config add nginx
sh run.sh start
```

An existing proxy is valid when it:

- Proxies to gateway port `8000`.
- Supports WebSocket upgrades for Realtime.
- Sends correct `X-Forwarded-*` headers.
- Uses public HTTPS values in Supabase/Auth URL variables.
- Does not leave duplicate public gateway bindings when proxy and gateway share a protected Docker network.

Self-signed certificates are development-only; OAuth providers and normal clients require publicly trusted certificates.

## Secrets and keys

Use the official scripts:

```sh
sh utils/generate-keys.sh --update-env
sh utils/add-new-auth-keys.sh --update-env
```

The second script configures asymmetric signing/JWKS plus new opaque API keys while retaining legacy compatibility. Do not partially enable this: Auth signing and every token-verifying service must receive compatible keys.

Changing `JWT_SECRET` requires regenerating JWKS. Rotating opaque API keys requires client/server updates but does not itself invalidate user sessions. Regenerating the asymmetric key pair invalidates sessions signed by the old key and needs a maintenance/communication plan.

Use `utils/db-passwd.sh` for an existing deployment's database password rotation, then recreate services. Do not edit only `.env`; database roles and service configuration must agree.

## Start and smoke-test

```sh
sh run.sh status
sh tests/test-container-logs.sh
sh tests/test-self-hosted.sh http://localhost:8000
```

The official smoke test exercises container health, Studio authentication, Auth lifecycle, REST/GraphQL, Storage including integrity and signed URLs, Realtime, and Functions. Run it from the deployment directory with its `.env`. Treat generated test records as scoped test data; inspect cleanup if the test aborts.

Also verify from outside the host through the real proxy/DNS/TLS boundary. A loopback pass does not prove firewall, certificate, redirect, or WebSocket behavior.

## Optional overrides

Manage official overrides through `run.sh config add/remove`, which updates `COMPOSE_FILE`. Examples include logs, Caddy, Nginx, Envoy, and S3-compatible storage. Always inspect the resolved model after changing overrides:

```sh
sh run.sh config
sh run.sh compose-config
```

Relative Compose files and environment interpolation are part of the deployment contract. A variable in `env_file` is container runtime input; `${VAR}` interpolation in Compose is resolved earlier from the Compose environment/`.env`.

## Production hardening

- Restrict Studio and database administration to trusted networks/users.
- Protect Docker socket access; optional Vector logging reads it.
- Use least-privilege database roles where supported and review Studio/postgres-meta access.
- Rate-limit/monitor public Auth, Storage, REST, Realtime, and Functions routes at the gateway/proxy as appropriate.
- Configure SMTP and abuse controls; self-hosting does not inherit platform protections.
- Back up database data, logical dumps, Storage bytes, Functions/source/config, `.env`/key material securely, and the `db-config` volume's pgsodium root key.
- Alert on external availability, service health, database capacity/connections, backup freshness, and restore-test age.
