# Scripting and command contract

Use this reference when writing an unattended restic job, parsing output, or deciding how automation reacts to failures.

## Keep the wrapper small and honest

A safe wrapper supplies credentials through a protected mechanism, calls one operation, preserves its exit code, and emits bounded evidence. It must not silently initialize a missing repository, turn every error into success, or chain destructive maintenance after a failed backup.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${RESTIC_REPOSITORY:?repository must be configured}"
: "${RESTIC_PASSWORD_FILE:?protected password file must be configured}"

restic backup /data --tag files --tag production
restic snapshots --json > /var/lib/restic/latest-snapshots.json
```

Use `--stdin-from-command` for database dumps or other generated content when possible. It preserves the producer command's exit status. If using a pipe to `backup --stdin`, enable `set -o pipefail`; otherwise a failed producer can leave a misleading successful backup process.

The documented shape is one producer command after `--`:

```sh
restic backup --stdin-filename production.sql --stdin-from-command -- \
  mysqldump --host example production
```

For compression or another transformation, pass a tested wrapper program as that
producer command. If the wrapper uses a shell pipeline, it must enable `pipefail`
and return a failing producer's status. Do **not** append `| gzip` outside the command after
`--stdin-from-command`: that pipe is handled by the invoking shell, not by
restic's child process, and can transform restic's own output rather than the
database export.

## Exit codes are a contract

Restic documents these general meanings. A command can define more specific behavior, and future versions can add codes. Treat every unrecognized nonzero code as a failure.

| Exit code | Meaning | Automation response |
|---|---|---|
| 0 | Success | Record snapshot freshness and duration, not merely process success |
| 1 | Fatal error | Alert and preserve redacted stderr |
| 2 | Go runtime error | Alert as execution failure |
| 3 | Partial backup because some source files were unreadable; or some forget removals failed | Treat backup as incomplete; inspect affected paths before declaring protection healthy |
| 10 | Repository does not exist (0.17.0+) | Do not auto-initialize without an explicit new-repository directive |
| 11 | Failed to lock repository (0.17.0+) | Determine whether an operation is active; retry/wait or investigate stale lock |
| 12 | Wrong password (0.17.1+) | Inspect secret retrieval and intended repository, without logging a secret |
| 130 | Interrupted by SIGINT/SIGTERM (0.19.0+) | Treat as interrupted; rerun deliberately and inspect snapshots |

## JSON contract

Use `--json` only for commands that support it. Main JSON data goes to stdout; fatal errors may yield a final `exit_error` JSON object on stderr. Long-running commands such as `backup`, `check`, `restore`, and `diff` can emit JSON Lines distinguished by `message_type`.

Do not assume JSON schemas are closed. Restic documents that fields and message types can be added. Parsers must ignore unknown fields/message types, retain the exit code, and avoid treating an absence of a known optional field as an error. `prune` does not support JSON, so `forget --prune --json` mixes JSON and text: keep prune in a separate operational path if a machine needs clean structured output.

## Locks and retries

A repository lock is protection, not a routine error to erase. For expected short contention, `--retry-lock` can wait. For a persistent lock, inspect scheduler state and live restic processes before considering `unlock`. Use `--no-lock` only for read-only operations when the operational risk of an unlocked read is understood; it is not an escape hatch for mutations.

## Configuration safeguards

- Use absolute source and exclude-file paths in scheduled jobs.
- Keep `TMPDIR` capacity in the job's preflight; temporary pack creation requires space.
- Pin an intended restic version for critical automation and run `restic <command> --help` during upgrades.
- Keep backup, retention/prune, sampled/full checks, and restore drills as separately observable jobs.
- Do not make `restic cat config || restic init` an unattended default. An authentication or backend error can be mistaken for a missing repository.

## Sources

- Scripting, exit codes, JSON output, and compatibility guidance: https://restic.readthedocs.io/en/stable/075_scripting.html (accessed 2026-07-15)
- Backup stdin behavior and source errors: https://restic.readthedocs.io/en/stable/040_backup.html (accessed 2026-07-15)
- Locks and recovery diagnosis: https://restic.readthedocs.io/en/stable/077_troubleshooting.html (accessed 2026-07-15)
