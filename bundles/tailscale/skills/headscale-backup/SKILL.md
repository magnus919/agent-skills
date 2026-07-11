---
name: headscale-backup
description: Backup, restore, and migrate Headscale installations — SQLite database,
  configuration file, policy file, and TLS certificates. Use when backing up a headscale
  server before upgrades, migrating to new hardware, or restoring from a disaster.
metadata:
  category: devops
---

# headscale-backup

## Overview

Headscale state is stored in SQLite (its database), `config.yaml`, `policy.json`, and TLS certificates. Regular backups are critical before upgrades, as database corruption or misconfiguration can result in complete loss of node registration and routing state. This skill provides three scripts covering the full lifecycle: backup, restore, and migration.

## Backup Contents

A complete backup tarball includes:

- **SQLite DB** — Full node state, users, routes, pre-auth keys, API keys
- **`config.yaml`** — Headscale server configuration
- **`policy.json`** — ACL policy file (if present)
- **Certs and keys** — TLS certificate, private key, and node private key (`/var/lib/headscale/`)
- **DERP map** — DERP configuration file (if customized)

## Backup Methods

- **`sqlite3 .backup`** (recommended) — Safe for live databases; uses SQLite online backup API. This is what `hs-backup.sh` uses.
- **File copy (`cp`)** — Requires stopping headscale first to avoid WAL corruption.

## Restore

1. Stop headscale service
2. Restore files from backup tarball
3. Start headscale service
4. Verify with a health check or `headscale nodes list`

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

## Trigger Conditions

- "backup headscale"
- "restore headscale"
- "migrate headscale"
- "headscale backup"
