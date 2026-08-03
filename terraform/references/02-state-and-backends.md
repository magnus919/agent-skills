# State backends and locking

The backend owns state storage and locking. State is the source of truth for what exists, holds sensitive values, and is the thing concurrent operators can corrupt — treat it accordingly.

## Backend selection

- `local` (default): state on disk in the working directory. Fine for experiments; unsafe for any shared environment.
- Object-storage backends with a locking sidecar: S3 + DynamoDB lock table, GCS, Azure Storage. Standard for team use; the lock sidecar is what makes them safe to share.
- Managed state backends: Terraform Cloud / OpenTofu Cloud (or a compatible cloud) — built-in locking, run history, policy hooks.
- Consul: locking natively via Consul sessions; niche but lock-capable.

Backend behavior is implementation-dependent: some backends lock, some do not. Check the backend documentation before trusting locking (the `00-source-index.md` lists backend docs).

## Locking semantics

- `plan` takes a lock only when it needs to (normally plan can run lock-free except with `-refresh-only` and similar); `apply` and `state push` acquire and hold the lock for the whole run.
- A stale lock (crash, killed process) blocks the next run. Resolution is backend-specific: inspect the lock holder, confirm nothing is genuinely running, then `force-unlock <LOCK_ID>` — never delete the lock row blindly and never bypass locking by switching backends.
- Locking does not protect against `state push` misuse: `push` is "extremely dangerous" per upstream docs and should be avoided; it refuses to overwrite a different lineage or a higher serial unless `-force` is used, which itself requires a backup and reviewed scope.

## Migrating between backends

1. Backup the current state first (`terraform state pull > state-backup.json`).
2. Add the new backend block; run `terraform init` — it offers `-migrate-state` (copy) or `-reconfigure` (re-point, no copy). Choose deliberately.
3. Verify: `tfops state --state <pulled> --json` on the migrated state, a clean plan, and a lock/unlock cycle from two concurrent processes.

## State as a secrets-bearing artifact

- Encrypt the backend at rest; restrict read/write to operators that need it.
- Mark sensitive values `sensitive = true` so they are redacted in plan output and logs.
- Enable versioning/soft-delete on the backend so an accidental overwrite is recoverable, and restore-drill it.

## Sources

> **Last Updated:** 2026-08-03
- State storage and locking (Terraform): https://developer.hashicorp.com/terraform/language/state/backends (accessed 2026-08-03)
- State locking (Terraform): https://developer.hashicorp.com/terraform/language/state/locking (accessed 2026-08-03)
- State backends (OpenTofu): https://opentofu.org/docs/language/state/backends/ (accessed 2026-08-03)
- State locking (OpenTofu): https://opentofu.org/docs/language/state/locking/ (accessed 2026-08-03)
- Manual state pull/push warnings: https://developer.hashicorp.com/terraform/language/state/backends#manual-state-pull-push (accessed 2026-08-03)
