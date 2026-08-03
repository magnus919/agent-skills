# Extensions

> **Last Updated:** 2026-08-03

This reference covers inventorying, installing, and upgrading PostgreSQL
extensions, with attention to the upgrade and security gotchas that bite
operators.

## Inventory first

```sql
-- Installed extensions and versions
SELECT extname, extversion FROM pg_extension ORDER BY extname;

-- Available on this installation (name, default version, requires)
SELECT name, default_version, installed_version FROM pg_available_extensions
ORDER BY name;
```

The `pgdiag` `extensions` check reports the installed set.

## Installing an extension

- An extension install is a mutation: it changes the shared catalog and, for
  many extensions, the database schema and behavior. Confirm the target and
  rollback path before running `CREATE EXTENSION`.
- Some extensions must be loaded at server start via
  `shared_preload_libraries` (e.g., `pg_stat_statements`, `timescaledb`,
  `citus`) — a restart is required and a misconfigured library can prevent
  startup.
- Trusted extensions (`pg_available_extensions.trusted = true`) can be
  installed by non-superusers into their own databases; anything else needs
  superuser.
- Extension *choice* and lifecycle policy are infrastructure decisions;
  shared-library availability and packaging are platform concerns that route
  to `platform-engineering`.

## Operating notes for common extensions

| Extension | Operational notes |
|---|---|
| `pg_stat_statements` | Best aggregate query evidence; needs `shared_preload_libraries` + restart; `pg_stat_statements_reset()` to reset |
| `postgis` | Large library; major-version upgrades need a reinstall or upgrade script per database |
| `pgvector` | Indexes are not binary-compatible across major versions — rebuild after a major upgrade |
| `pgcrypto`, `uuid-ossp` | Stable and small; rarely the source of upgrade pain |
| `hstore`, `citext` | Plain catalog extensions; safe through `pg_upgrade` with the `--no-...` flags checked |

## Upgrading extensions

- `ALTER EXTENSION name UPDATE TO 'newversion';` upgrades an installed
  extension when the extension's script provides the path.
- A major PostgreSQL upgrade commonly requires new extension binaries: run
  `pg_upgrade` and then install/re-install the extension versions matching the
  new server, or upgrade each database's extension before decommissioning the
  old cluster.
- Check each extension's release notes for the target version span *before*
  the upgrade window; PostGIS and pgvector in particular publish explicit
  major-upgrade procedures.

## Hard boundaries

- Never install an extension into production without a human directive, a
  named rollback (drop or version pin), and a verified backup path.
- Never load an extension via `shared_preload_libraries` without a restart
  plan and a check that the library exists on disk.
- Never assume an extension survives a major upgrade; verify per extension.
