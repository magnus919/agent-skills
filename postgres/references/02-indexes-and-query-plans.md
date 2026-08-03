# Indexes and Query Plans

> **Last Updated:** 2026-08-03

This reference covers measuring and operating indexes and diagnosing query
plans. Designing which index to add for a new workload is schema design and
routes to `data-architect`; this skill owns reading the evidence and operating
what exists.

## Evidence first: statistics views

```sql
-- Which indexes are actually used, most used first
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC LIMIT 10;

-- Indexes with no recorded scans (write cost with no read benefit)
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY relname, indexrelname;

-- Tables scanned sequentially a lot (candidate for a missing index)
SELECT schemaname, relname, seq_scan, seq_tup_read, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC LIMIT 10;

-- Indexes marked unusable (dropped on next vacuum)
SELECT c.relname AS index_name, i.indrelid::regclass AS table_name
FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
```

The bundled `pgdiag` script runs these probes in its `index_usage`,
`unused_indexes`, `invalid_indexes`, and `seq_scan_heavy` checks.

## Reading a plan

- `EXPLAIN` shows the planner's estimate; `EXPLAIN (ANALYZE, BUFFERS)` executes
  the statement and reports actual rows, timing, and buffer usage. Read the
  estimated-versus-actual row counts: a large mismatch means the planner is
  working from stale or missing statistics.
- `EXPLAIN (FORMAT JSON)` is the machine-readable form:
  `scripts/pgdiag --plan-for "SELECT ..." --json`.
- Node shapes to recognize: `Seq Scan` (whole-table read), `Index Scan` /
  `Index Only Scan` (index seek), `Bitmap Heap Scan` (index + heap filter),
  `Nested Loop`/`Hash Join`/`Merge Join`, `Sort`, `Materialize`.

## Common findings and next steps

| Finding | Likely cause | Check before acting |
|---|---|---|
| `Seq Scan` on a filtered large table | Missing index or planner cost settings | `pg_stat_user_tables.seq_tup_read`; actual row estimate vs `random_page_cost`/`effective_cache_size` |
| Estimated rows far from actual | Stale `pg_statistic` | Has `autovacuum`/autoanalyze run since the last big change? |
| Index with `idx_scan = 0` for weeks | Unused index (write overhead) | Confirm the access path is genuinely gone, then a deliberate drop in a maintenance window |
| Invalid index | Interrupted build / catalog issue | Repair deliberately; never assume it is serving queries |
| `Index Only Scan` not used | Visibility map not set | Check `pg_class.relallvisible`; the heap pages are probably dirty |

## Query-plan hygiene

- Test plans on the real workload shape, not on tiny samples: statistics scale
  with data, and a plan that is right on a 1k-row table is often wrong at 10M.
- Change planner parameters one at a time and re-measure with
  `EXPLAIN (ANALYZE, BUFFERS)` before and after.
- `pg_stat_statements` (extension) is the best aggregate evidence for which
  statements deserve plan work. See `06-extensions.md` for enabling it.
- Never "fix" a slow query by disabling index scans globally
  (`enable_indexscan=off`): treat that as a diagnostic probe, not a fix.

## Verification

After any index change: re-run the affected query's `EXPLAIN (ANALYZE,
BUFFERS)` and compare total time and rows, and re-check `idx_scan` trends on
the next reporting window. A plan change is verified by measurement, not by
assertion.
