# PostgreSQL Configuration Operations

> **Last Updated:** 2026-08-03

This reference covers reading, changing, and verifying PostgreSQL configuration
safely. The runtime source of truth is `pg_settings`, not the configuration
file: values shown by `SHOW`/`current_setting()` reflect reloads, `ALTER
SYSTEM` overrides, and command-line `-c` options.

## Reading configuration

```sql
SHOW shared_buffers;
SELECT name, setting, unit, context, pending_restart
FROM pg_settings
WHERE name IN ('shared_buffers', 'max_connections', 'wal_level', 'archive_mode');
```

The `context` column says when a change takes effect:

- `postmaster` — requires a restart (`pending_restart` becomes true).
- `sighup` — takes effect on reload (`pg_ctl reload` or
  `SELECT pg_reload_conf();`).
- `user`/`superuser`/`backend` — settable per-session or per-role.

## Reload versus restart

Requires restart (memory and process-shape parameters):

- `shared_buffers`, `max_connections`, `wal_level`, `max_wal_senders`,
  `max_replication_slots`, `max_prepared_transactions`,
  `shared_preload_libraries`, `huge_pages`, `dynamic_shared_memory_type`.

Reloads safely (most tuning, logging, and vacuum parameters):

- `work_mem`, `maintenance_work_mem`, `effective_cache_size`,
  `random_page_cost`, `seq_page_cost`, `checkpoint_timeout`,
  `max_wal_size`, `archive_command`, `autovacuum` and its workers,
  `log_min_duration_statement`, `log_statement`, `track_io_timing`.

The bundled `pgdiag` `config` check reports the operator-critical values in
one bounded payload:

```bash
scripts/pgdiag --check config --json
```

## Operator-critical values and what they do

| Parameter | What it controls | Typical signal of trouble |
|---|---|---|
| `shared_buffers` | Postgres's own cache | Too small: heavy `pg_stat_database` read activity while OS cache is idle |
| `effective_cache_size` | Planner's estimate of OS+PG cache | Too small: planner favors index scans that are slower than seq scans in reality |
| `work_mem` | Per-sort/hash memory | Too small: temp-file sorts (`pg_stat_database.temp_files`) |
| `maintenance_work_mem` | Vacuum/index build memory | Too small: slow index builds and slow vacuum |
| `max_connections` | Hard connection cap | Saturation: `pg_stat_activity` near cap, `FATAL: sorry, too many clients` |
| `wal_level` | What WAL carries | Must be `replica` (or higher) for archiving and streaming replication |
| `archive_mode` / `archive_command` | WAL archiving | See `04-backups-wal-pitr.md` |
| `autovacuum` / `autovacuum_max_workers` | Background maintenance | Rising `n_dead_tup`, XID wraparound risk; see `03-vacuum-and-bloat.md` |
| `log_min_duration_statement` | Slow-query logging threshold | 0 if you need every statement; 250-1000ms is a common operations default |
| `track_io_timing` | I/O timing in statistics | Off makes `pg_stat_database` I/O columns meaningless |
| `random_page_cost` | Planner cost of random reads | Overstated on SSD causes seq-scan preference for large tables |

## Changing configuration safely

1. Change in the file (or `ALTER SYSTEM SET ...`) on one named parameter.
2. Determine whether a reload or restart is required from `pg_settings.context`.
3. Prefer reload; schedule restarts with a maintenance window and a verified
   rollback (the previous value).
4. Verify with `SHOW`/`current_setting()` and re-run the affected diagnostic.

Hard boundaries:

- Never change `shared_preload_libraries` without a restart plan — a typo can
  make the server fail to start.
- Never raise `max_connections` without accounting for backend memory per
  connection (`work_mem` is per operation, but each backend holds base memory).
- Connection pooling for application workloads is an application-architecture
  decision that routes to `backend-engineering`; `max_connections` tuning here
  is server capacity, not app design.
