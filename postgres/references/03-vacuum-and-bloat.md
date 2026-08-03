# Vacuum and Bloat Management

> **Last Updated:** 2026-08-03

This reference covers the maintenance loop that keeps PostgreSQL tables
healthy: autovacuum supervision, dead-tuple and bloat measurement, and the
disciplined use of manual vacuum operations.

## Why vacuum matters

- Vacuum reclaims dead tuple space and refreshes the visibility map and
  planner statistics. Without it, tables bloat and transaction ID wraparound
  becomes an emergency.
- `autovacuum` is on by default; the operational task is *supervision*: is it
  keeping up with the workload?

## Measuring the signals

```sql
-- Dead tuples per table, worst first
SELECT schemaname, relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC LIMIT 10;

-- How far tables are from forced anti-wraparound vacuum
SELECT datname, age(datfrozenxid) AS xid_age
FROM pg_database ORDER BY xid_age DESC;

-- Is a vacuum running right now, and where?
SELECT * FROM pg_stat_progress_vacuum;
```

The `pgdiag` `bloat` check reports the dead-tuple signal in one bounded payload.

## Interpreting the evidence

- `n_dead_tup` rising faster than vacuum runs complete → autovacuum is falling
  behind. Common causes: not enough `autovacuum_max_workers`, long-running
  transactions pinning old snapshots, connection saturation, or very large
  tables where a full pass takes longer than `autovacuum_naptime`.
- Table file size far above live-data size → heap bloat. Check `pg_class`
  `relpages` against `n_live_tup` × average row width; a bloat estimate query
  can quantify it.
- Index bloat shows as large `relpages` on indexes relative to key count.
- `age(datfrozenxid)` approaching `autovacuum_freeze_max_age` (default 200M) is
  the wraparound warning; below ~50M it is time to act deliberately.

## Acting deliberately

1. Confirm the target and maintenance window with the human before any
   maintenance vacuum; a manual `VACUUM` on a big table is a bounded mutation
   with a measurable cost.
2. Prefer `VACUUM (ANALYZE)` on the specific tables showing the problem over a
   blanket full-cluster pass.
3. `VACUUM FULL` rewrites the table and takes an exclusive lock; it is a
   last resort for severe bloat, never routine. It requires a maintenance
   window and a verified backup path.
4. After acting, re-run the `bloat`/dead-tuple probe and confirm the trend
   direction changed; also confirm autovacuum is keeping up afterwards.

## Config levers (all reload-safe)

- `autovacuum_max_workers`, `autovacuum_naptime`, `autovacuum_vacuum_cost_limit`
  — worker capacity and pacing.
- Per-table overrides via storage parameters (`autovacuum_vacuum_scale_factor`,
  `autovacuum_vacuum_threshold`) for tables that need faster or slower cycles.

## Hard boundaries

- Never run `VACUUM FULL` without a maintenance window and a confirmed backup.
- Never stop autovacuum to "save load" on a production instance — the deferred
  work comes back as bloat and wraparound risk.
- Never present a high `n_dead_tup` as a diagnosis by itself; it is evidence
  that the vacuum loop needs attention, and the cause (long transactions,
  worker starvation, pacing) must be identified before acting.
