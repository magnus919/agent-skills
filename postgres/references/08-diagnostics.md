# Diagnostics with Evidence

> **Last Updated:** 2026-08-03

This reference maps symptoms to probes and fixes for PostgreSQL incidents,
with the evidence discipline that separates a real diagnosis from a guess.

## Evidence order

Diagnose in this order — each layer is cheaper than the next and rules out
whole classes of cause:

1. **Identity and version** — what are we actually looking at (primary or
   standby, which version)?
2. **Configuration** — are the operator-critical settings what the workload
   assumes?
3. **Connections** — is the instance saturated, or is the app doing something
   odd?
4. **Indexes and plans** — is the query the problem, or the data shape?
5. **Vacuum/bloat** — is maintenance keeping up?
6. **WAL archiving** — is the recovery story intact?
7. **Replication** — is the standby current and is failover defensible?
8. **Extensions** — did a library or extension change break something?

The bundled `pgdiag` script collects layers 1–8 in one bounded JSON payload:

```bash
scripts/pgdiag --json
scripts/pgdiag --check connections --check wal_archive --json   # targeted
scripts/pgdiag --plan-for "SELECT ..." --json                    # layer 4 probe
```

## Symptom-to-probe table

| Symptom | First probes | Likely next step |
|---|---|---|
| Queries suddenly slow | `pgdiag --json`; `EXPLAIN (ANALYZE, BUFFERS)` on the slow statement | Check plan row estimates vs actual; check `n_dead_tup` trend and planner stats freshness |
| Connections rejected | `pgdiag` `connections`; `pg_stat_activity` state counts | Compare against `max_connections`; look for stuck/idle-in-transaction backends; pooler sizing is `backend-engineering` |
| Backups stop completing | `pgdiag` `wal_archive`; archive destination disk/network | `failed_count`/`last_failed_wal`; fix `archive_command` or storage |
| Standby falls behind | `pgdiag` `replication` + `recovery`; `pg_replication_slots` | Lag columns, slot retention, network saturation; consider sync config |
| Instance is slow overall | `pg_stat_database` I/O + `pg_stat_bgwriter` | Check `track_io_timing` is on; look for checkpoint storms, heavy seq scans |
| Autovacuum stuck | `pg_stat_progress_vacuum`; long-running transactions | Find the snapshot-pinning transaction; tune workers if genuinely starved |
| After an upgrade, "everything is slow" | Planner statistics; extension reinstall | Run `analyze`; verify extensions were upgraded per `06-extensions.md` |

## Evidence discipline

- **Measure before claiming.** "The query is slow" is a symptom; "the plan
  shows a seq scan with 1.5M rows read while the index has zero scans" is
  evidence.
- **Correlation is not cause.** A high `n_dead_tup` and a slow query in the
  same window are correlated, not necessarily causal. State what was measured,
  what changed, and what was verified.
- **Re-run after acting.** A fix is verified when the relevant probe returns
  the expected value, not when the symptom seems quieter.
- **Keep evidence bounded.** Summarize statistics rows and log excerpts;
  never dump full logs or connection strings with passwords into chat.
- **When to stop.** Stop after three non-converging diagnostic passes and
  report the evidence gathered so far, the hypotheses ruled out, and the
  remaining candidates — rather than escalating into unconfirmed changes.

## Log sources

- Server log (wherever `logging_collector` writes) for errors, checkpoints,
  and slow statements when `log_min_duration_statement` is set.
- `pg_stat_activity` for live state; `pg_stat_archiver` and
  `pg_stat_replication` for the recovery story.
- Never parse the full server log into a response; extract the bounded window
  relevant to the incident.
