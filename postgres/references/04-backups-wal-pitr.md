# Backups: WAL Archiving and Point-in-Time Recovery

> **Last Updated:** 2026-08-03

This reference covers the operational side of backups for PostgreSQL: WAL
archiving readiness, base backups, and point-in-time recovery (PITR). The
cross-engine backup *strategy* (RPO/RTO targets, retention policy, off-site
copies) belongs to `data-engineering`; this skill owns the PostgreSQL
mechanics and their verification.

## The recovery model

A usable recovery point is a **base backup plus the WAL archive that follows
it**: restore the base, then replay archived WAL up to the target time or LSN.
Without continuous archiving you can only recover to the moment of the last
base backup.

## WAL archiving readiness

```sql
-- The three settings that gate archiving (wal_level change needs restart)
SELECT name, setting FROM pg_settings
WHERE name IN ('wal_level', 'archive_mode', 'archive_command', 'archive_timeout');

-- Archiver health: archived_count must grow, failed_count must stay flat
SELECT archived_count, failed_count, last_archived_wal, last_archived_time,
       last_failed_wal, last_failed_time
FROM pg_stat_archiver;
```

The `pgdiag` `wal_archive` check reports the archiver row directly.

Readiness checklist:

- `wal_level = replica` (or higher) and `archive_mode = on`.
- `archive_command` succeeds for every segment; it must be idempotent and
  return zero only on success (a failing command makes the server retry and
  log failures).
- `pg_stat_archiver.failed_count` is not climbing and `last_failed_wal` is
  stale. A rising `failed_count` means archiving is broken *right now*, and
  every segment since then widens the PITR gap.

## Taking a base backup

```bash
# Consistent base backup with WAL included (the supported path)
pg_basebackup -h primary -D /backup/base-2026-08-03 -X stream -c fast -P

# Label and record it
echo "backup of primary at $(date -Is)" > /backup/base-2026-08-03/BACKUP_LABEL
```

- Use `-X stream` (or `-X fetch`) so WAL segments produced during the backup
  are included — a base backup without its WAL is not restorable.
- Record the label and timestamp; a restore target is only as good as the
  backup's metadata.
- Test restore: on a scratch instance, restore the base, point
  `restore_command` at the archive, and verify the server reaches the expected
  recovery point. This is the only evidence that the backup works.

## Restoring to a point in time

1. Restore the base backup to the target data directory.
2. Set `restore_command` (how to fetch archived WAL) and a recovery target —
   `recovery_target_time` (e.g., `'2026-08-03 02:00:00'`),
   `recovery_target_lsn`, or `recovery_target_xid`.
3. Start the server; it replays WAL to the target and stops (or enters
   recovery if `recovery_target_action = promote` on 12+).
4. Verify the data at the boundary (the row/table the incident was about),
   then promote when confident.

Recovery-target kinds: time-based (the `pitr|point.in.time` family — a
wall-clock moment) or position-based (an LSN or timeline marker). Choose the
kind that matches how you know *when things went wrong*; a wall-clock target
is the common case.

## Verification boundaries

| Claim | Minimum evidence |
|---|---|
| Archiving is healthy | `archived_count` increasing and `failed_count` flat over a window |
| A backup exists | Labeled base backup directory with matching WAL |
| Backups support recovery | A full restore-to-time drill on a scratch instance, logged |
| PITR target is reachable | Server reaches the target and the expected rows exist |

## Hard boundaries

- Never claim recoverability from a backup log alone; only a restore drill is
  evidence.
- Never run a restore against the production data directory without an
  explicit human directive; a restore is a mutation.
- Never let `archive_command` return success on failure — silent archiving
  failure widens the recovery gap undetected.
- Never keep only base backups: without WAL there is no point-in-time
  recovery, only point-of-backup recovery.
