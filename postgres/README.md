# PostgreSQL — Operational Skill for PostgreSQL

Operate PostgreSQL safely: configuration review, index and query-plan analysis, vacuum and bloat management, WAL archiving and point-in-time recovery, replication and failover, extensions, major-version upgrades, and diagnostics with evidence.

## Why Install This Skill

Your agent can run PostgreSQL operations instead of guessing: review configuration against the workload, find the index and query-plan evidence behind a slow query, verify that autovacuum is keeping up, check that WAL archiving is actually working (not just configured), measure replication lag, plan a failover or a major-version upgrade, and diagnose incidents in a fixed evidence order.

It ships a read-only diagnostic script (`pgdiag`) that collects the operator-critical evidence in one bounded JSON payload — server version, configuration values, connection pressure, index usage, bloat signals, archiver health, replication state, extensions, and database sizes. Every session opens read-only (`default_transaction_read_only=on`), so the tool cannot mutate anything even by mistake, and `--help` works with no cluster and no psql installed.

The references are distilled from the official PostgreSQL documentation with dated sources and verification-first guidance. Schema design, application-level data access, and cross-engine methodology deliberately route to the skills that own them (`data-architect`, `backend-engineering`, `data-engineering`); this skill owns the day-to-day operation of PostgreSQL itself.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop, mutation gates, and verification boundaries |
| `references/` | Nine dated references: configuration, indexes/plans, vacuum/bloat, backups/WAL/PITR, replication/failover, extensions, upgrades, diagnostics, source index |
| `scripts/pgdiag` | Read-only diagnostic collector: stdlib-only Python, `--json`, `--check` subsets, `--plan-for` (EXPLAIN JSON), `--help` without a cluster |
| `tests/` | Deterministic tests against a fake psql stub, including the read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no cluster and no psql installed
scripts/pgdiag --help

# Full read-only diagnostics, machine-readable
scripts/pgdiag --json

# Against a specific instance
scripts/pgdiag --host db1.example.com --dbname app --user ops --json

# Targeted checks
scripts/pgdiag --check identity --check wal_archive --check replication --json

# Add an EXPLAIN plan for one read-only statement
scripts/pgdiag --plan-for "SELECT * FROM orders WHERE id = 42" --json
```

The script shells out to `psql` (override the binary with `--psql /path/to/psql`; connection defaults come from the usual `PGHOST`/`PGPORT`/`PGUSER`/`PGDATABASE` environment variables or the flags above). Exit codes: 0 ok, 1 runtime/collection error, 2 usage error, 127 psql not found, 124 timeout.

## Triggers

Load this skill for `postgres`/`PostgreSQL`/`psql` operations: configuration review and `postgresql.conf` tuning, slow queries and `EXPLAIN` plan analysis, index usage measurement, vacuum and bloat, WAL archiving and point-in-time recovery, backups and restore drills, replication and standby lag, failover planning, extension installs and upgrades, minor or major version upgrades (`pg_upgrade`), or any PostgreSQL incident that needs evidence-first diagnosis. Do not load it for application data-access code (that's `backend-engineering`), schema design (that's `data-architect`/`data-engineering`), Supabase platform administration (that's `supabase`), or other database engines (those stay in `data-engineering`).

## Requirements

- Python 3.9+ for the `pgdiag` script (`--help` needs nothing else).
- The `psql` client (PostgreSQL 10+ server) for live diagnostics; it must be on `PATH` or passed with `--psql`.
- Socket or network access to the target instance and, for read-only diagnostics, a role that can read the system catalogs and statistics views.
