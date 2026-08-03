# Upgrades

> **Last Updated:** 2026-08-03

This reference covers upgrading PostgreSQL safely, distinguishing minor
in-place upgrades from major-version upgrades, and the rollback decision at
each step.

## Minor versus major

- **Minor upgrades** (e.g., 16.4 → 16.5) are binary swaps: stop, replace
  binaries, start. No data-format change; a restart is the whole procedure.
- **Major upgrades** (e.g., 15 → 16) change the on-disk format. Options:
  `pg_upgrade` (in-place, fast, link or copy mode) or logical dump/restore
  (`pg_dump`/`pg_dumpall`). Both are mutations requiring downtime and a
  verified backup.

## Before any major upgrade

1. Read the release notes and the upgrade guide for **the full version span**
   — skipping intermediate major versions compounds risks and deprecations.
2. Check extensions (see `06-extensions.md`): which have new binaries, which
   need reinstall, which block the move.
3. Check `pg_upgrade` prerequisites: `--check` mode reports problems without
   changing anything — run it first.
4. Rehearse in a scratch environment with the real data shape, including
   representative table sizes and the workload's slowest queries.

## pg_upgrade flow

```bash
# Pre-flight only — no changes
/path/to/new/bin/pg_upgrade --old-bindir /path/to/old/bin \
  --new-bindir /path/to/new/bin --old-datadir /var/lib/pg15 \
  --new-datadir /var/lib/pg16 --check

# Real run (after stop-writes confirmation and a verified backup)
/path/to/new/bin/pg_upgrade --old-bindir /path/to/old/bin \
  --new-bindir /path/to/new/bin --old-datadir /var/lib/pg15 \
  --new-datadir /var/lib/pg16
```

- Stop writes on the old cluster first; the upgrade moves data between the
  two directories.
- `--link` mode is fast but makes the old cluster unusable until the new one
  works (shared inodes); `--copy` is slower but keeps the old cluster intact
  as a rollback path.
- After the upgrade, run `analyze` on the new cluster (fresh planner
  statistics are mandatory) and re-install/upgrade extensions per their notes.
- Verify at the application boundary — the workflow the database serves —
  before decommissioning the old cluster.

## Logical upgrade paths

- `pg_dumpall`/`pg_dump` + restore into a fresh cluster: universal, slow for
  large data, but the safest for unusual setups.
- Logical replication (publisher/subscriber) as a near-zero-downtime major
  upgrade: run the new major as a subscriber, catch up, switch. This is also a
  migration pattern whose methodology lives in `data-engineering`.

## Rollback decision

- With `--copy` mode (or dump/restore), rollback is "start the old cluster
  again" — but WAL divergence since the upgrade start means the old cluster's
  data reflects the stop point, not anything written to the new one.
- Decide the rollback trigger *before* the window: how much new-write loss is
  acceptable, and who calls the rollback.
- Never delete the old cluster or its backup until the new cluster has
  survived the verification boundary.

## Hard boundaries

- Never run a major upgrade without a human directive, a maintenance window, a
  verified backup, and a rehearsed run.
- Never skip `analyze` on the new cluster and then debug "slow queries" as if
  they were config problems.
- Never decommission the old cluster until the new one is verified at the
  application boundary.
