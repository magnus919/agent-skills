# Replication and Failover

> **Last Updated:** 2026-08-03

This reference covers streaming replication setup, monitoring, and the
failover runbook. Replication topology design (sync vs async, quorum, cluster
managers) is an architecture decision; this skill owns the PostgreSQL
mechanics and their verification.

## Streaming replication model

A standby connects to the primary with a replication slot, receives WAL
segments as they are produced, and replays them. `wal_level = replica` (or
higher) and `max_wal_senders`/`max_replication_slots` must be sized for the
number of standbys.

Setup essentials:

- Create a physical replication slot per standby
  (`SELECT pg_create_physical_replication_slot('standby-1');`).
- Build the standby with `pg_basebackup -X stream` and configure
  `primary_conninfo` in `postgresql.conf` (12+) with `standby.signal`.
- Confirm the standby is actually streaming: it is `in_recovery` and appears
  in `pg_stat_replication` on the primary.

## Measuring replication health

```sql
-- On the primary: who is streaming and how far behind
SELECT application_name, state, sync_state, client_addr,
       sent_lsn, write_lsn, flush_lsn, replay_lsn, replay_lag
FROM pg_stat_replication;

-- On the standby: is it receiving and replaying?
SELECT pg_is_in_recovery(), pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();
```

The `pgdiag` `recovery` and `replication` checks report both views.

Health rules of thumb:

- `state = streaming` for every standby; anything else (`startup`,
  `catchup`, `backup`) is transitional or stuck.
- Lag should stay within the agreed bound. `replay_lag` measures the gap
  between the primary's current WAL and what the standby has replayed.
- A slot that is far behind but still `streaming` means the standby cannot
  keep up or the network is saturated — the slot's retained WAL grows on the
  primary until it does.

## Synchronous versus asynchronous

- Asynchronous (default): the primary commits without waiting; failover can
  lose the most recent commits.
- Synchronous (`synchronous_standby_names = 'standby-1'`): the primary waits
  for that standby's flush before acknowledging commits. Trade-off: commit
  latency for a durability guarantee.
- Choose deliberately and document the choice; the failover runbook must
  state what durability was promised.

## Failover runbook

A failover plan names: who promotes, how clients are redirected, what happens
to the old primary when it returns, and how the result is verified.

1. **Confirm the directive**: failover is a mutation; it requires an explicit
   human decision naming the target standby.
2. **Check lag and timeline first**: how much data is at risk, and has the
   standby been applying continuously? Promotion with a lagging standby is a
   deliberate data-loss decision, not an accident.
3. **Promote**: `pg_ctl promote` or `SELECT pg_promote();` on the chosen
   standby. With a cluster manager (Patroni, repmgr) use its switchover
   command instead of manual promotion.
4. **Redirect clients**: DNS, connection strings, or the pooler — verify a
   fresh connection lands on the new primary and writes succeed.
5. **Rejoin the old primary** as a standby with `pg_rewind` (it is now
   diverged from the new primary's timeline) — never let two primaries accept
   writes.

## Hard boundaries

- Never promote without a human directive and a stated rollback path.
- Never let two primaries run: the old primary must be fenced or rejoined
  before it can accept writes again.
- Never fail over to a standby with unknown lag and call it "the same data".
- Never disable `archive_mode`/WAL sending to "simplify" replication — the
  archive and the stream are both part of the recovery story.
