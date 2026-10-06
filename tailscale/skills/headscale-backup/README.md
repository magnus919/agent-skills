# Headscale Backup

Create a verified backup of Headscale state and restore it to the right paths during a recovery or migration.

## Why Install This Skill

Headscale keeps its node and user state in a SQLite database, alongside configuration and key files. Copying a live database can miss transactions stored in its WAL files. This skill takes an online SQLite snapshot and records checksums and restore paths for every included asset, including a configured DERP server private key.

After installing it, your agent can preview backup and restore actions, create a portable archive, verify its contents, and restore files to the paths recorded in the archive. The restore helper validates the archive before it writes files and manages an active Headscale service during the restore. Existing destination ownership is preserved; for new files, ownership comes from the destination directory, so prepare target directories for the Headscale service before a cross-host restore.

## What You Get

| File | Purpose |
|---|---|
| `scripts/hs-backup.sh` | Create and verify a manifest-backed archive |
| `scripts/hs-restore.sh` | Preview or restore verified assets with service control |
| `scripts/hs-migrate.sh` | Guide a host-to-host migration |
| `scripts/hs-archive.py` | Build archives, check SQLite integrity and validate restores |
| `evals/evals.json` | Representative backup, restore, and migration scenarios |
| `SKILL.md` | Operational guidance and recovery steps |

## Quick Start

Preview the assets that would be included:

```sh
scripts/hs-backup.sh --dry-run --json
```

Preview a restore before approving its target paths:

```sh
scripts/hs-restore.sh --backup /backups/headscale/headscale-20261006.tar.gz --dry-run --json
```

Create a backup after reviewing the paths:

```sh
scripts/hs-backup.sh --auto --output-dir /backups/headscale
```

## Triggers

- Back up Headscale before an upgrade.
- Restore Headscale after data loss or a failed migration.
- Move Headscale to a new host.
- Check that a backup archive has valid checksums and mapped recovery paths.

## Requirements

- Python 3.10 or newer
- `sqlite3` command-line utility for online database snapshots and integrity checks
- Read access to Headscale configuration, SQLite database, policy, and configured key files
- Write access to the backup directory; restore also needs write access to target paths and permission to control the Headscale service
- SQLite-backed Headscale; PostgreSQL configurations are rejected
- Restore uses the absolute destinations in the archive. Root overrides that would move files are rejected until the Headscale config and service paths have been separately updated and validated.
