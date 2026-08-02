# Data Integrity Verification

## Purpose

Verify that data is correct and consistent after a restore, failover, or recovery event. A successful restore that produces corrupted or inconsistent data is a failed recovery. Data integrity verification is a required step in every restore-based recovery exercise.

## Verification levels

| Level | What it checks | When to use |
|---|---|---|
| **Structural** | Files exist, schemas match, row counts are expected | Every restore — fast, automated, catches gross failures |
| **Checksum** | Cryptographic hash of data blocks or files matches pre-backup hash | Every restore for systems where data corruption is a risk |
| **Application-level** | Business rules hold — foreign keys resolve, aggregates compute, workflows execute | Restores of critical systems; DR failovers |
| **Reconciliation** | Restored data matches an independent source of truth (e.g., event log replay, replica comparison) | High-assurance restores; financial/healthcare data |

## Post-restore validation procedure

### 1. Pre-restore baseline
- Record expected row counts per table or collection.
- Record expected checksums for critical data sets.
- Record schema version and migration state.

### 2. Structural validation
- [ ] Restored files or database exist and are accessible.
- [ ] Schema version matches expected version.
- [ ] Row counts match expected counts within tolerance.
- [ ] Indexes are present and valid.

### 3. Checksum validation
- [ ] Compute checksums on restored data blocks.
- [ ] Compare against pre-backup checksums.
- [ ] Flag any mismatch for investigation.

### 4. Application-level validation
- [ ] Run application-level consistency queries: foreign keys resolve, no orphaned records.
- [ ] Compute key aggregates and compare against pre-restore baseline.
- [ ] Execute critical business workflows in a test context against restored data.
- [ ] Verify that application can connect to and query the restored data store.

### 5. Reconciliation (high-assurance systems)
- [ ] Replay event log against restored state and compare.
- [ ] Compare restored data against an independent replica or audit log.
- [ ] Verify that all committed transactions are present and no uncommitted transactions appear.

### 6. Sign-off
- [ ] Validation owner reviews all results.
- [ ] Any discrepancy is recorded in the follow-up work ledger.
- [ ] Validation owner signs off or escalates.

## Common failure modes

| Failure mode | Detection | Mitigation |
|---|---|---|
| Backup is corrupted | Checksum mismatch | Multiple backup copies; periodic restore testing |
| Backup is incomplete (missing recent data) | Row count below expected; reconciliation gap | Verify backup completeness at time of creation |
| Restore process introduces corruption | Post-restore checksum mismatch | Use verified restore tooling; test restore procedure regularly |
| Schema migration mismatch | Application errors on connect; foreign key failures | Record schema version at backup time; validate compatibility |
| Replica lag captured in backup | Data inconsistency between related tables | Use consistent snapshot or transactionally-consistent backup |
