# PostgreSQL Operations — Source Index

> **Last Updated:** 2026-08-03

This index tracks the authoritative sources behind the PostgreSQL operational
skill and the refresh procedure for keeping it current.

## Canonical sources

| Topic | Source |
|---|---|
| Core documentation (current release) | https://www.postgresql.org/docs/current/ |
| Configuration reference | https://www.postgresql.org/docs/current/runtime-config.html |
| Server administration (backup, replication, upgrades) | https://www.postgresql.org/docs/current/admin.html |
| System catalogs and statistics views | https://www.postgresql.org/docs/current/catalogs.html and .../monitoring-stats.html |
| `pg_upgrade` | https://www.postgresql.org/docs/current/pgupgrade.html |
| `pg_basebackup` | https://www.postgresql.org/docs/current/app-pgbasebackup.html |
| Streaming replication | https://www.postgresql.org/docs/current/warm-standby.html and .../streaming-replication.html |
| Continuous archiving and PITR | https://www.postgresql.org/docs/current/continuous-archiving.html |
| `pg_stat_archiver` and statistics views | https://www.postgresql.org/docs/current/monitoring-stats.html |

## Version observations (as of this refresh)

- `pg_stat_replication` exposes `sent_lsn`/`write_lsn`/`flush_lsn`/`replay_lsn`
  and the `*_lag` columns on PostgreSQL 10 and later. Pre-10 servers expose
  `*_location` columns instead; this skill targets PostgreSQL 10+.
- `pg_backup_start()`/`pg_backup_stop()` replaced `pg_start_backup()`/
  `pg_stop_backup()` in PostgreSQL 15. `pg_basebackup` remains the supported
  base-backup path on every supported release.
- Recovery configuration moved from `recovery.conf` to `recovery.signal`/
  `standby.signal` in PostgreSQL 12. `recovery_target_*` parameters are set in
  `postgresql.conf` (or via `ALTER SYSTEM`) and take effect at start time.
- `VACUUM` progress is observable through `pg_stat_progress_vacuum`
  (PostgreSQL 9.6+) and `pg_stat_progress_cluster` (12+).
- `pg_promote()` (PostgreSQL 12+) promotes a standby without shelling out.

## Refresh procedure

1. Re-check the sources above for a new minor or major release.
2. Update the version observations that changed (column renames, renamed
   functions, moved configuration files).
3. Re-run the bundled diagnostic script against a test instance and confirm
   every check still parses: `scripts/pgdiag --psql /path/to/psql --json`.
4. Re-verify the SKILL.md keyword sweep from the validation contract and the
   routing links to `backend-engineering`, `data-architect`, and
   `data-engineering`.

## Related skill sources

- `data-engineering` owns cross-engine methodology: backup strategy, migration
  patterns, and analytical SQL. Its references are the source for engine-spanning
  decisions; this skill covers PostgreSQL operation itself.
- `data-architect` owns schema and data modeling; index *choice* at design time
  lives there, while index *operation and measurement* live in
  `02-indexes-and-query-plans.md`.
