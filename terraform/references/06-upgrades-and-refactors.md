# Upgrades and refactors

Upgrades change the tool/provider contract; refactors change the module structure. Do them one at a time, in a controlled order, with a plan review between every step.

## Version upgrades

1. **Read the upgrade guides for the whole span** — each minor version from current to target (Terraform upgrade guides; OpenTofu publishes its own). Collect deprecations, default changes, and behavior changes.
2. **Validate** in place first: `terraform validate` / `tofu validate` and a plan show whether the current config is compatible with the current binary before you change anything.
3. **Stage**: upgrade the tool in a non-production environment (or a clone workspace), run plan, apply, and verify before touching production.
4. **Provider migrations** within an upgrade: `terraform state replace-provider` handles provider source/version moves (e.g., moving to a namespaced provider); run it with the state backed up and a lock held.
5. **Rollback**: the tool binary can be downgraded within supported bounds, and the state file is version-agnostic at the format level — keep the previous binary available until the new version has applied cleanly.

## Refactors (renames and restructures)

- Prefer `moved` blocks: they make the plan show pure renames (no destroy/create), keep the state change explicit, and are reviewable in the diff. This is the default for renaming resources or modules.
- Fall back to reviewed `terraform state mv` only when `moved` does not fit (e.g., migrating between backends/workspaces); each `state mv` is a state mutation and needs a backup and a held lock.
- Never delete state entries to force recreation of a resource that exists; that loses the resource's data and identity.
- Sequence: upgrade first, then refactor — two change classes compounding is the classic trap (a failed refactor is then blamed on the upgrade and vice versa).

## Verification

- After each step: `terraform validate`, a clean plan (renames show as renames, not replaces), apply in staging, and a drift-free re-plan.
- `tfops plan --state FILE --json` gives a quick state-level sanity check (serial, lineage, resource inventory) before and after refactors.

## Sources

> **Last Updated:** 2026-08-03
- Terraform upgrade guides: https://developer.hashicorp.com/terraform/upgrade-guides (accessed 2026-08-03)
- Refactoring module resources (`moved` blocks): https://developer.hashicorp.com/terraform/language/modules/develop/refactoring (accessed 2026-08-03)
- `terraform state mv`: https://developer.hashicorp.com/terraform/cli/commands/state/mv (accessed 2026-08-03)
- `terraform state replace-provider`: https://developer.hashicorp.com/terraform/cli/commands/state/replace-provider (accessed 2026-08-03)
- OpenTofu refactoring documentation: https://opentofu.org/docs/language/modules/develop/refactoring/ (accessed 2026-08-03)
- Version observations (current lines): see `00-source-index.md` (accessed 2026-08-03)
