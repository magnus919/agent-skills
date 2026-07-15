# Troubleshooting and migration

Use this reference for failed jobs, locks, repository errors, damaged metadata, backend changes, or copy/migration work.

## Diagnose in order

1. Capture the exact restic command, version, exit status, and bounded stderr. Redact passwords, tokens, signed URLs, and private paths before sharing.
2. Separate source failures from repository/backend failures. A permission-denied source path, an expired S3 credential, and a corrupt index have different owners and remedies.
3. Reproduce with a read-only command if possible: `snapshots`, `stats`, `check`, or a limited `ls`.
4. Check for an active restic process before manipulating locks.
5. Read the installed command's `--help` and the matching stable documentation before a repair or migration command. These operations are version- and repository-state-sensitive.

## Symptom map

| Symptom | Evidence first | Do not do |
|---|---|---|
| Password/repository cannot open | Confirm repository URL, password source readability, backend identity, and exact error | Do not initialize the same target again |
| Permission denied | Identify source versus backend, execution user, file mode/ACL, and provider policy | Do not broaden permissions globally as a first fix |
| Locked repository | Process list/job scheduler, lock age, known concurrent maintenance | Do not immediately run `unlock` |
| Slow or timed-out job | Source scan, backend latency, bandwidth, lock contention, logs | Do not change many performance flags at once |
| Backup had errors | Examine failed source paths and whether snapshot policy allows partial backups | Do not call the backup healthy from exit code alone |
| `check` failure | Exact check error, version, backend health, last good restore | Do not run repair blindly |
| Need new storage backend | Destination compatibility, credentials, capacity, copy/restore test | Do not delete old repository after a copy-only claim |

## Locks

Restic uses repository locks to protect concurrent operations. A running backup, prune, check, or interrupted process can leave a lock. Establish whether an operation is active through the scheduler and process list; only then consider `restic unlock` for a stale lock. If the host may have crashed or the backend is eventually consistent, document the evidence and retry conservatively.

## Repository repair and index work

Commands such as `rebuild-index`, `repair`, `migrate`, and `recover` exist for specific conditions. They are not routine maintenance. Before invoking one:

- Preserve the exact error and `restic version`.
- Run the least-invasive documented diagnostic first.
- Confirm a second copy or tested recovery point where feasible.
- Read the corresponding command help for the installed release.
- Verify afterward with `check` and a restore test.

Do not invent a repair sequence based on a search snippet. Repository state and restic version determine the valid path.

### Documented repair posture

For a reported integrity failure, stop retention/prune jobs and preserve the current evidence before repair. The troubleshooting documentation's general sequence is: run `check --read-data`; make a copy of the repository metadata at minimum (especially `index/` and `snapshots/`); run `repair index` when check suggests it; rerun backups if overlapping source data can replenish missing content; run `repair snapshots --dry-run`; then decide whether `repair snapshots --forget` is an acceptable, explicit data-loss action; finally run another full check and a restore test.

`repair packs` and `repair snapshots` are remediation commands, not health checks. They can change what remains recoverable. Do not automate them, and never describe repair as successful without a post-repair `check` plus a restore of the relevant data.

## Copy and migration

`restic copy` copies snapshots between repositories. It is not a substitute for a recovery verification. For a migration:

1. Inventory source snapshots and repository/client versions.
2. Initialize and secure the destination independently.
3. Copy a small representative scope first if the command/backend supports it.
4. Compare source and destination snapshot inventory.
5. Run destination `check` and restore a representative snapshot from the destination.
6. Keep the source immutable/available until the agreed retention period and recovery drill are complete.

A backend move may require moving credentials, lifecycle policy, monitoring, and recovery documentation as well as data. Update all of them.

For `copy`, source and destination use distinct credential namespaces (`RESTIC_FROM_REPOSITORY`, `RESTIC_FROM_PASSWORD_FILE`, and related `RESTIC_FROM_*` variables for the source). Different repository encryption keys require data to be downloaded and uploaded. If cross-repository deduplication matters, initialize a new destination with `init --from-repo SOURCE --copy-chunker-params` before writing it; chunker parameters cannot be changed later. These details make the copy path a migration project, not a one-line storage move.

## Version compatibility

Repository format and client version are related but not interchangeable. The stable documentation identifies repository format version 2 as the current default and states its minimum restic version. Before upgrading automation, pin and test the candidate client against a non-production repository or a representative restore. Review the project's release notes for behavior changes, especially around commands used unattended.

## Evidence bundle for escalation

Provide only:

```text
restic version:
backend class (not credentials):
operation and redacted flags:
exit code:
timestamp/timezone:
first relevant stderr lines:
active-job/lock evidence:
last known-good check and restore-drill dates:
```

This is enough to diagnose most issues without disclosing keys or a full infrastructure inventory.

## Sources

- Restic command reference: https://restic.readthedocs.io/en/stable/manual_rest.html (accessed 2026-07-15)
- Working with repositories and lock-related commands: https://restic.readthedocs.io/en/stable/045_working_with_repos.html (accessed 2026-07-15)
- Restic release notes: https://github.com/restic/restic/releases (accessed 2026-07-15)
- Restic changelog: https://github.com/restic/restic/blob/master/CHANGELOG.md (accessed 2026-07-15)
