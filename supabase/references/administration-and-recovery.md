# Administration and recovery

Read this for routine operations, backups, restores, version updates, Postgres upgrades, key rotation, capacity, or incident recovery.

## Routine evidence

Collect without printing secrets:

```sh
sh run.sh config
docker compose config --quiet
docker compose ps --format json
docker compose logs --tail=100 SERVICE
docker compose exec db psql -U postgres -d postgres -c 'select version();'
```

Track disk usage, memory pressure/OOM events, Postgres connections, database size/growth, replication health, API latency/errors, certificate expiry, SMTP failures, backup freshness, and restore-test age. Bound logs and redact headers, tokens, SQL parameters, and connection strings.

## Backup scope

A recoverable self-hosted deployment includes more than Postgres:

1. **Database:** logical dump for portability plus a consistent physical/data-volume strategy appropriate to recovery objectives.
2. **pgsodium root key:** stored in the `db-config` named volume. Losing it can make Vault secrets unrecoverable.
3. **Storage object bytes:** filesystem path or external S3-compatible backend; database dumps contain metadata/policies, not bytes.
4. **Deployment configuration:** Compose files, overrides, Functions, snippets, proxy configuration, and a securely protected `.env`/key record.
5. **External dependencies:** DNS, certificates, SMTP, OAuth/SAML/SMS provider settings, firewall rules, and object-store policy.

Do not call a backup complete until it restores into a separate target and representative Auth, REST/RLS, Storage, Realtime, and Functions flows pass.

## Logical dump and restore

For Supabase-aware migration/restore, prefer `supabase db dump` over raw `pg_dump`; it filters managed internals and reserved roles:

```sh
supabase db dump --db-url "$SOURCE_DB_URL" -f roles.sql --role-only
supabase db dump --db-url "$SOURCE_DB_URL" -f schema.sql
supabase db dump --db-url "$SOURCE_DB_URL" -f data.sql --use-copy --data-only
```

Restore into a new/test self-hosted instance with error-stop and a transaction after confirming version/extensions:

```sh
psql --single-transaction --variable ON_ERROR_STOP=1 \
  --file roles.sql \
  --file schema.sql \
  --command 'SET session_replication_role = replica' \
  --file data.sql \
  --dbname "$TARGET_DB_URL"
```

The database restore includes schema, data, roles, policies, functions, triggers, and Auth users. It does not migrate API/JWT keys, provider/SMTP settings, Functions source, Storage object bytes, DNS, or certificates. Existing platform-issued user tokens generally become invalid when signing material changes.

Run a test restore first. Reconcile source/target Postgres and service versions, extensions, internal schema changes, and role ownership. Do not weaken the final restore by ignoring errors; use a diagnostic attempt only to inventory mismatches, fix the dump/target, then rerun transactionally.

## Updating the self-hosted release set

Supabase publishes tested Docker configuration releases; service tags may intentionally lag independent upstream images.

1. Back up and prove recovery for the affected data.
2. Read `docker/CHANGELOG.md`, `docker/versions.md`, release notes, and linked breaking changes.
3. Diff the whole current `docker/` configuration against the new release: Compose, `.env.example`, gateway templates, init SQL, utilities, and overrides.
4. Merge new environment variables without replacing existing secrets.
5. Resolve with `docker compose config --quiet` and inspect image tags/volumes/ports.
6. Pull images.
7. Recreate only a safe independent service when the change is isolated; otherwise follow release instructions for full stop/start and expected downtime.
8. Run official and external-boundary smoke tests.
9. Retain the previous configuration, images where practical, and database recovery path until verification is complete.

Do not update one service to `latest` because it has a newer release. Compatibility with the pinned set is not guaranteed.

## Postgres 15 to 17

Postgres 17 is current default for fresh deployments. Existing Postgres 15 data must use the official upgrade workflow; never start the Postgres 17 image on its data directory.

Before upgrade:

- Independent backup outside the directory being transformed.
- Copy of the data directory.
- Separate export of `/etc/postgresql-custom/pgsodium_root.key` from the `db-config` volume.
- Optional logical dump.
- At least `2x database size + 5 GB` free disk, plus adequate `/tmp`/`TMPDIR` space.
- Inventory incompatible extensions (`timescaledb`, `plv8`, `plcoffee`, `plls` in current official guidance).
- Running/healthy starting stack and planned downtime.

Run the current `utils/upgrade-pg17.sh` as documented. It performs `pg_upgrade --check`, migrates, reconciles extensions, preserves the original directory, and starts the new stack. Verify Postgres version, extensions, Vault data, migrations, API/service behavior, and application flows before deleting any backup. Keep the original data and key until the rollback window closes.

## Key and password rotation

- Opaque API key rotation: `utils/rotate-new-api-keys.sh --update-env`, recreate, update applications, verify both key roles.
- Asymmetric signing-key regeneration: `utils/add-new-auth-keys.sh --update-env`; expect old ES256 sessions to fail.
- Legacy JWT secret change: regenerate dependent JWKS and coordinate every verifier/client.
- Database password: use `utils/db-passwd.sh` so roles and `.env` remain consistent, then recreate.

Never expose new values in ticket bodies, process output, shell history, or health reports. Verify by role/behavior, not by printing credentials.

## Destructive controls

Require separate explicit confirmation and current recovery evidence before:

- `reset.sh`, `docker compose down -v`, or deleting data/storage paths.
- `supabase db reset --linked`.
- Dropping extensions/replication slots for upgrades.
- Migration-history repair.
- Deleting pre-upgrade backups or the pgsodium root key.
- Replacing signing keys that invalidate sessions.

A command's built-in confirmation prompt is not a substitute for validating the exact target and rollback path.
