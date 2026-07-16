# Troubleshooting

Read this when the local CLI stack or self-hosted deployment fails. Diagnose one layer at a time; do not restart or delete state before reading current evidence.

## Layered sequence

1. **Recent change:** inspect the diff in application migrations, `config.toml`, Compose, `.env.example` merge, gateway templates, image tags, proxy, DNS, and certificates.
2. **Resolved model:** `supabase --version`, `docker compose config --quiet`, active `COMPOSE_FILE`, services, ports, volumes, and interpolated non-secret settings.
3. **Container state:** `docker compose ps --format json`; inspect exit, health, restart count, and OOM state.
4. **Bounded logs:** `docker compose logs --tail=100 SERVICE`; use the official `tests/test-container-logs.sh` for the self-hosted stack.
5. **Internal health:** database, gateway, and failing service from inside the Compose network.
6. **Gateway route:** use the expected API key role and inspect status plus body.
7. **External boundary:** DNS, TLS, proxy headers, WebSocket upgrade, firewall, and callback URLs.
8. **Application semantics:** migration history, grants, RLS, user claims, Storage policy, Realtime publication, and Function code.

After two genuinely different approaches fail, report the evidence and ask before escalating to destructive recovery or security-boundary changes.

## CLI local stack

### `supabase start` fails

- Confirm Docker-compatible runtime is running and accessible.
- Check host RAM allocation and port conflicts.
- Verify the project was initialized and the command runs from the correct root.
- Read the failing container logs and CLI version before upgrading/restarting.
- Preserve uncommitted schema/data before `supabase stop --no-backup`.

### `db diff` reports no changes

If declarative schemas are configured, `db diff` reads `supabase/schemas/`, not ad hoc Studio/SQL changes. Apply the change to schema files. If the project uses imperative migrations, confirm the local database differs from migration history and pass scope explicitly.

### `db reset` fails

The first failing migration and SQL error are the root evidence. Fix the migration or ordering/dependency issue and replay from scratch. Do not patch only the resulting database; the migration chain is the deliverable.

### Local/remote migration mismatch

Run `supabase migration list`. Determine whether SQL is missing, remote schema drifted, or history alone is wrong. Use `db pull` for real schema drift. Use `migration repair` only after proving the actual SQL state; bookkeeping changes can hide defects.

## Self-hosted containers

### Service remains `created`, unhealthy, or restarting

On first boot, Postgres and service-owned migrations can outlast the initial healthcheck retry window. `run.sh start` may exit nonzero even though containers are still making forward progress and later become healthy. Read the migration logs and re-check health before restarting; distinguish slow initialization from a persistent error.

- Run `docker compose config --quiet` and `ps` first.
- Read its logs and dependency health; `depends_on` readiness works only where the official health conditions are present.
- Check database credentials, URL values, and mounted file permissions.
- Check host memory/OOM and disk/inode pressure.
- For Kong entrypoint errors, verify LF line endings; CRLF checkouts break shell entrypoints.
- For rootless Docker/Podman logging, verify `DOCKER_SOCKET_LOCATION` and current Compose interpolation support.

Do not delete volumes to clear a health failure.

### Auth/OAuth links point to the wrong place

Current self-hosted `API_EXTERNAL_URL` includes `/auth/v1`. Confirm `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL`, `SITE_URL`, additional redirects, proxy scheme/host, and provider-console callback. Recreate services after environment changes.

### REST root returns `403` with public key

Current self-hosted gateway restricts `/rest/v1/` OpenAPI root to administrative keys. Test an intended table route with the publishable key and expected RLS role before diagnosing PostgREST as unavailable.

### RLS returns no rows or permits too much

- Confirm RLS is enabled on the exact table.
- Inspect grants and policies for the current role/operation.
- Test `auth.uid()`/claims and anonymous `null` behavior.
- Check `USING` versus `WITH CHECK`.
- Ensure the test is not using service role.
- Re-query after writes; an unauthorized update can be a zero-row no-op.

### Realtime connects but emits no changes

Check table publication, RLS visibility, user session/key, committed database change, Realtime logs, and proxy WebSocket forwarding. An HTTP 200 on a route is not subscription proof.

### Storage metadata works but objects are missing

Database restore recovers metadata/policies, not object bytes. Check the filesystem/S3 backend, `GLOBAL_S3_BUCKET`, credentials, endpoint/path style, volume mount, and separate object restore. Verify object checksum through the public/signed path.

### Functions ignore code or environment changes

Restart Functions for mounted code changes. Recreate for environment or secret changes. Verify the mounted path, gateway invocation, global JWT-verification setting, and Function logs.

## Upgrade and recovery failures

### Postgres 17 will not start

Never attach Postgres 17 to an old Postgres 15 data directory. For an actual upgrade, use the official script and preserved rollback data. A leftover `db-config` volume can break a genuinely fresh deployment, but deleting it also deletes custom config and the pgsodium key; only remove it after proving there is no data/Vault recovery value.

### Upgrade runs out of space

Stop and preserve state. The Postgres upgrade requires the source, copied destination, cached binaries, and staging space. Roll back, add capacity or move `TMPDIR`, revalidate `2x database size + 5 GB`, then retry.

### Restore fails across versions

Inventory Postgres version, extensions, service-internal tables/columns, and unsupported settings. Use `supabase db dump` rather than raw `pg_dump` for Supabase-aware filtering. A diagnostic non-transactional attempt may reveal all mismatches, but the final accepted restore must use error-stop and transactional behavior, followed by service-level checks.

## Evidence to report

Report target/environment, CLI or Docker release/commit, exact failing layer, command and exit status, redacted status/log excerpts, recent relevant change, what was verified, and the safest next step. Never include `.env`, keys, passwords, JWTs, email-provider secrets, or complete credential-bearing URLs.
