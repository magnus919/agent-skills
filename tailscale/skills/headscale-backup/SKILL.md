---
name: headscale-backup
description: Manage Headscale backups, restores, or migrations with a verified SQLite
  snapshot and explicit recovery paths before upgrades, host moves, or disaster recovery;
  do not use for server deployment, routine node management, or PostgreSQL backups.
metadata:
  category: devops
---

# headscale-backup

## Overview

Headscale state is stored in SQLite (its database), `config.yaml`, `policy.json`, and TLS certificates. Regular backups are critical before upgrades, as database corruption or misconfiguration can result in complete loss of node registration and routing state. This skill provides three scripts covering the full lifecycle: backup, restore, and migration.

Before creating an archive or restoring files, confirm the target, scope, and rollback path.
Read-only discovery and `--dry-run` previews may proceed without confirmation.

## Backup Contents

A complete backup tarball includes:

- **SQLite DB** — Full node state, users, routes, pre-auth keys, API keys
- **`config.yaml`** — Headscale server configuration
- **`policy.json`** — ACL policy file (if present)
- **Certs and keys** — TLS certificate and key, Headscale node private key, and configured DERP server private key
- **DERP map** — DERP configuration file (if customized)

## Backup Methods

- **`sqlite3 .backup`** (recommended) — Safe for live databases; uses SQLite online backup API. This is what `hs-backup.sh` uses.
- **File copy (`cp`)** — Requires stopping headscale first to avoid WAL corruption.

`hs-backup.sh` reads the database path and optional policy, TLS, node-key, DERP key, and DERP map paths
from `config.yaml`. It supports `database.sqlite.path`, `database.path`, and the legacy
`database_path` setting. PostgreSQL configurations are rejected. TLS certificates and keys
are included only when configured explicitly (or found in the configured standard
`/etc/headscale` locations); the helper does not scan unrelated Let's Encrypt certificates.
The resulting archive contains a manifest with SHA-256 checksums, file modes, and restore
destinations. Restore verifies every declared asset before it asks to overwrite files. It
preserves the recorded destinations by default. Root overrides that would move any asset
are rejected because the config or service may still point at archived paths. A migration
to different paths requires a separate planned config update and validation before restore.

## Restore

Before the first restore write, confirm the target host and mapped paths, the set of files
to replace, and the rollback archive or recovery route. A dry run is read-only and can be
used without confirmation.

1. Stop headscale service
2. Preview the mapped restore paths with `hs-restore.sh --backup <archive> --dry-run --json`
3. Restore files from backup tarball with `hs-restore.sh --backup <archive>`
4. Start headscale service
5. Verify with a health check or `headscale nodes list`

The wrapper stops and restarts an active systemd or SysV service around a restore. For
isolated tests only, set `HEADSCALE_SKIP_SERVICE_CONTROL=1`; this is intended for disposable
fixtures and does not make a production restore safe to run while Headscale is active.
Restored files keep the ownership of an existing destination; for a new file, the helper
uses the destination directory's owner and group. On a new host, prepare directories with
the ownership expected by the Headscale service before restoring. If a restore fails after
stopping the service, the helper leaves it stopped to avoid running with mixed state.

## Migration

1. Backup on source host (or use an existing backup)
2. `rsync` or `scp` the backup tarball to the target host
3. Set up headscale on the target (same version)
4. Restore from backup on target
5. Update DNS to point to the new server
6. Verify clients reconnect

## Version Compatibility

Source and target headscale versions **should match exactly**. Restoring a database from a different headscale version may cause schema migration failures or data corruption. Check versions with `headscale version` before migrating.

## Automated Backups (Cron)

Set up a daily cron job:

```bash
0 2 * * * /path/to/hs-backup.sh --auto --output-dir /backups/headscale/
```

## Gotchas

- **SQLite WAL mode**: `sqlite3 .backup` is safe; `cp` of the database file while headscale is running will produce a corrupt copy.
- **Version mismatch**: Restoring to a different headscale version may break schema migrations.
- **Node keys**: If node keys change, all nodes must re-authenticate.
- **API keys**: API keys are stored hashed in the database; restoring a DB backup does not recover the original key secrets — regenerate them with `headscale apikeys create`.
- **Pre-auth keys**: Pre-auth keys are restored along with the database, but if they've expired they won't work.

## Environment

- `HEADSCALE_URL` — Headscale server URL
- `HEADSCALE_API_KEY` — API key for health checks and validation

`HEADSCALE_CONFIG`, `HEADSCALE_DATA_DIR`, `HEADSCALE_CERTS_DIR`,
`HEADSCALE_CONFIG_DIR`, and `HEADSCALE_SERVICE` override the corresponding script defaults.
For migration, `HEADSCALE_REMOTE_RESTORE_SCRIPT` names the verified restore helper path
installed on the destination host; the default uses the same path as the local script.

## Trigger Conditions

- "backup headscale"
- "restore headscale"
- "migrate headscale"
- "headscale backup"

## When not to use

Do not use this skill for deploying or configuring a Headscale server — load `headscale-deploy` instead, or `headscale-node-lifecycle` for node management. It covers backup, restore, and migration of an existing installation only.
