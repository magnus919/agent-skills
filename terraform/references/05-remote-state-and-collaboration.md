# Remote state and collaboration

Remote backends make state shared, durable, lockable, and recoverable. The rules below keep multi-operator and cross-stack workflows safe.

## Operating with a remote backend

- `terraform init` once per backend config; it stores the backend configuration locally. `-reconfigure` re-points to a new backend without migrating data; `-migrate-state` copies existing state.
- All commands that touch state acquire the backend lock; verify locking works before trusting a multi-operator workflow (see `02-state-and-backends.md`).
- The working directory keeps only config and lock files; state lives in the backend. If you find a `terraform.tfstate` file next to a remote backend config, that is a migration mistake or a leftover — investigate, do not delete.

## Cross-stack consumption

- Read another stack's outputs with `data "terraform_remote_state"` in the consuming workspace, selecting by workspace name.
- Never hand-copy output values into config; the data source keeps the reference live and the dependency explicit.
- Document the producer/consumer relationship: a consumer makes the producer's state a dependency of its own applies.

## Protection and recovery

- Encrypt at rest; scope IAM/ACLs so only operators who must read state can; audit access.
- Enable backend versioning/soft-delete and restore-drill it: recovery of a corrupted or overwritten state file is a drill, not a hope.
- `terraform state pull` / `terraform state push` are the manual escape hatches: pull for backup and inspection, push only for reviewed fixups with lineage/serial protection understood (see `02-state-and-backends.md`).

## Sources

> **Last Updated:** 2026-08-03
- Remote state data source (Terraform): https://developer.hashicorp.com/terraform/language/state/remote-state-data (accessed 2026-08-03)
- Backends overview: https://developer.hashicorp.com/terraform/language/settings/backends/configuration (accessed 2026-08-03)
- State pull/push commands: https://developer.hashicorp.com/terraform/cli/commands/state/pull (accessed 2026-08-03)
- OpenTofu remote state: https://opentofu.org/docs/language/state/remote-state-data/ (accessed 2026-08-03)
- State management patterns (methodology): `platform-engineering/references/infrastructure-as-code.md` (accessed 2026-08-03)
