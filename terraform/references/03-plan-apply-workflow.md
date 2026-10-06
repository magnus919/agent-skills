# Plan/apply workflow

`plan` proposes; `apply` realizes. The plan output is the contract the apply fulfills — review it as a diff, not a wall of text.

## The loop

1. **Validate** before planning: `terraform validate` / `tofu validate` catches syntax and semantic errors early.
2. **Plan**: `terraform plan -json` (JSON, machine-reviewable) or `terraform plan -out plan.tfplan` (binary, reproducible apply input). `tfops plan --json` wraps the native plan or analyzes a state file directly when the backend is unreachable.
3. **Review**: classify every change — create, update in place, destroy, replace (destroy + create). Replaces are the highest risk; databases and stateful services deserve lifecycle checks (`prevent_destroy`, `create_before_destroy`, backup/restore proof) before approval.
4. **Apply**: save the reviewed plan (`terraform plan -out reviewed.tfplan`) and apply that exact file. `tfops plan --save-plan reviewed.tfplan` creates a plan with `-refresh=true` and records its SHA-256 in a local `.tfops.json` sidecar. After review, `tfops apply --yes --plan reviewed.tfplan` validates that binding, snapshots the exact plan, decodes the snapshot with `terraform show -json`, fails closed on missing/invalid format, success, or provenance evidence and invalid prior state when present, refuses detected taint or drift by default, then applies that same snapshot without generating a different plan. `--force` bypasses detected findings only after valid evidence is checked; it does not bypass missing or invalid evidence. A standalone `--state` summary cannot establish drift and cannot authorize apply.
5. **Verify**: apply exit 0 is evidence about Terraform only — check the external boundary the resource serves (DNS, endpoint, API) and re-plan to confirm no residual drift.

## Plan-reading rules

- Count creates/updates/destroys/replaces before reading details; a plan with unexpected destroys is a stop condition.
- `~` in-place update, `+` create, `-` destroy, `-/+` replace. A replace is a delete-then-create pair in the diff.
- Sensitive changes show as redacted values — if the diff implies a secret rotation you did not intend, stop and find the cause.
- `-target` narrows a run: acceptable for emergencies, never the default workflow (it leaves the rest of the state unverified).
- Workspaces: `terraform workspace list/select` before planning so the plan is against the right state; plan output should state the workspace.

## JSON plan output

`terraform plan -json` emits NDJSON events (one JSON object per line). For a reproducible apply, use `terraform plan -out reviewed.tfplan`; `terraform show -json reviewed.tfplan` provides the plan representation. `tfops apply` requires that saved plan and checks `resource_changes[*].action_reason` for taint and `resource_drift` for out-of-band changes. The `resource_changes` and `resource_drift` arrays may be omitted when empty in supported Terraform/OpenTofu JSON output; malformed arrays/items are rejected. Terraform `applyable` and `complete` fields, when present, must be true; all supported formats must report `errored: false`. The sidecar prevents accidental plan mismatch but is local metadata, not a signature against a malicious editor.

## Sources

> **Last Updated:** 2026-08-03
- Terraform plan command: https://developer.hashicorp.com/terraform/cli/commands/plan (accessed 2026-08-03)
- Terraform JSON output format: https://developer.hashicorp.com/terraform/internals/json-format (accessed 2026-10-06)
- Terraform apply command: https://developer.hashicorp.com/terraform/cli/commands/apply (accessed 2026-08-03)
- JSON output format: https://developer.hashicorp.com/terraform/internals/json-format (accessed 2026-08-03)
- OpenTofu CLI commands: https://opentofu.org/docs/cli/commands/ (accessed 2026-08-03)
- Lifecycle rules (`create_before_destroy`, `prevent_destroy`): https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle (accessed 2026-08-03)
