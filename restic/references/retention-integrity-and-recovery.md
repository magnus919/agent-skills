# Retention, integrity, and recovery

Use this reference for snapshot lifecycle, repository health, and evidence that data can actually be recovered.

## Retention is a policy, not a command fragment

First define the recovery window by source class. A common pattern retains a mix of recent, daily, weekly, monthly, and yearly snapshots, grouped by host, path, and tags. The exact values depend on recovery requirements, legal constraints, storage cost, and how independently each source class must be retained.

Preview a policy before deleting anything:

```sh
restic forget --dry-run \
  --keep-last 7 --keep-daily 14 --keep-weekly 8 --keep-monthly 12 \
  --group-by host,paths,tags
```

The `--group-by` fields are part of the policy. Omitting them or changing their order/scope can make a policy operate on a broader snapshot population than intended. Review both the keep and remove sets before running the same command without `--dry-run`.

## Forget versus prune

`forget` deletes snapshot references. The data that is no longer referenced may remain in the repository. `prune` identifies and removes that unreferenced data, which can be expensive and locks the repository while it runs. `forget --prune` combines both when snapshots were removed.

Operational consequences:

- Schedule prune separately from frequent backups unless its duration and lock behavior are known.
- Run `restic check` after pruning, as the restic manual recommends.
- Do not promise storage reclamation merely because `forget` ran.
- Do not confuse provider lifecycle deletion with restic retention. A provider lifecycle rule can remove objects restic still needs.

## Integrity verification tiers

| Tier | Command | What it demonstrates |
|---|---|---|
| Metadata | `restic check` | Repository metadata and structure can be read and validated |
| Sampled data | `restic check --read-data-subset=5%` | A bounded sample of repository pack data can be read and verified |
| Full data | `restic check --read-data` | All repository pack data can be read and verified |
| Recovery drill | `restore` to a separate target | Snapshot selection, decryption, extraction, filesystem write, and human/application inspection |

The first three are important but none proves that the intended source data or application will recover correctly. A restore drill does. Run it periodically, rotate snapshots/tags tested, and record the command, target, selected snapshot, validation result, duration, and limitations.

## Restore safely

First identify the exact snapshot and content:

```sh
restic snapshots --host app-01 --tag production
restic ls latest
restic find important-file
```

Restore to a separate empty target:

```sh
restic restore latest --host app-01 --target /var/tmp/restore-test
```

`--path` selects a snapshot when used with `latest`; it does not restrict which files are restored. Use `--include`/`--exclude` or the documented `<snapshot>:<subfolder>` syntax when recovering a subset. Do not use an in-place restore as the first diagnostic action. The official documentation warns an interrupted in-place restore can leave files partially restored.

After restore, compare a representative set of files, ownership and permissions where relevant, and application-level behavior. For databases, import into an isolated instance and run an application query or integrity check.

## Recovery drills

Use `templates/restore-drill.md` to capture:

1. Objective and selected snapshot
2. Separate restore target and disk-space check
3. Command and duration
4. File-level and application-level validation
5. Gaps, remediation, and next drill date

A successful drill is evidence about that selected snapshot and environment, not a perpetual guarantee. Repeat after major backend, credential, client-version, policy, or application changes.

## Sources

- Snapshot removal, prune behavior, locks, and post-prune check: https://restic.readthedocs.io/en/stable/060_forget.html (accessed 2026-07-15)
- Snapshot listing and filters: https://restic.readthedocs.io/en/stable/045_working_with_repos.html (accessed 2026-07-15)
- Restore selection, include/exclude behavior, and in-place restore cautions: https://restic.readthedocs.io/en/stable/050_restore.html (accessed 2026-07-15)
- `check` options: https://restic.readthedocs.io/en/stable/045_working_with_repos.html#checking-integrity (accessed 2026-07-15)
