# Backup design and automation

Use this reference to design what is protected, how consistency is achieved, and how restic is invoked without hiding failures.

## Define the protection contract before a command

For each backup job, write down:

| Decision | Questions to answer |
|---|---|
| Sources | Which paths, volumes, databases, or application exports are in scope? |
| Consistency | Is a normal filesystem read sufficient, or do you need an application dump, quiesce hook, filesystem snapshot, or VSS? |
| Exclusions | Which paths are disposable, regenerated, secret, mounted, or outside the backup boundary? |
| Identity | What stable `--host` and `--tag` values separate data classes? |
| Frequency | What recovery-point objective does the schedule support? |
| Recovery | Where can data be restored and how is it validated? |
| Ownership | Who receives failures and who can retrieve the repository password? |

Do not back up an active database directory as if it were ordinary files unless its database vendor documents that as safe. Prefer a transactionally consistent dump, vendor backup, or snapshot procedure; then back up that artifact. Verify application restoration separately.

## Create predictable snapshots

```sh
restic backup /srv/app-data \
  --host app-01 \
  --tag production \
  --tag app-data \
  --exclude-file /etc/restic/app-data.exclude
```

Use a stable host label rather than relying on a transient container or cloud hostname. Tags should represent recovery-relevant classes, not a free-form log. The same tags and source path grouping must be used by the corresponding retention command, otherwise a global policy can delete a class you intended to retain.

Use `--exclude-file` for reviewable exclusions. Test pattern behavior against a small representative tree before using it on a broad source. Beware that excluding a mount point may be different from excluding its contents; inspect snapshots with `restic ls` after the first backup.

## Source consistency by platform

- Linux/macOS files: ordinary file backup is appropriate only when applications tolerate concurrent reads. Use application-native exports or a filesystem snapshot if not.
- Windows: `backup --use-fs-snapshot` uses Volume Shadow Copy Service (VSS), allowing reads of files locked by other processes. Restic exposes VSS options under `-o vss.*`; load the official backup documentation before changing providers, volumes, or timeouts.
- Containers: back up a named volume only after determining the application consistency boundary. Prefer a database dump and configuration export over copying an active data directory.
- Virtual machines: use the hypervisor's documented snapshot/export workflow when crash consistency is not enough.

## Automation contract

A scheduled job must be non-interactive, bounded, and observable:

1. Use a restricted service account.
2. Supply repository and password through a protected file or secret-manager command.
3. Set the working directory and absolute paths deliberately.
4. Capture stdout/stderr to a protected, bounded log or journal.
5. Preserve the restic exit code. Do not append `|| true` or hide failures behind a pipeline.
6. Alert on failure and on stale success, not just on a failing command.
7. Run retention/prune in a separately scheduled maintenance window.

The systemd templates use `Type=oneshot` and a timer. Copy them locally, set only non-secret policy values, and put credential paths in a protected environment file. A timer is not itself evidence that backups ran: inspect service result, snapshot age, and restore-drill evidence.

## Example job wrapper logic

```sh
set -eu
restic backup /data --tag files
restic snapshots --json > /var/lib/restic/last-snapshots.json
```

This is intentionally small. Add application pre/post hooks only when the application needs them, and make cleanup idempotent. A pre-hook that leaves an application frozen after failure is worse than no hook.

## Monitoring signals

Capture at least:

- Exit status and duration
- Newest expected snapshot timestamp for each source/tag group
- Backup errors reported by restic
- Repository size growth and raw-data statistics over time
- `check` result and date of the latest sampled/full data read
- Date and result of the latest restore drill

Use JSON where a machine will consume output: `restic snapshots --json`, `restic stats --json`, and command-specific JSON options where available. Keep raw output bounded and redact paths if they themselves are sensitive.

## Sources

- Backup behavior, progress, deduplication, exclusions, and Windows VSS: https://restic.readthedocs.io/en/stable/040_backup.html (accessed 2026-07-15)
- Systemd scheduling documentation: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html (accessed 2026-07-15)
- Command reference: https://restic.readthedocs.io/en/stable/manual_rest.html (accessed 2026-07-15)
