---
name: terraform
description: >-
  Operate Terraform and OpenTofu across the whole infrastructure lifecycle:
  module structure, state backends and locking, plan/apply workflow, drift
  detection, remote state, upgrade and refactor flows, and evidence-based
  diagnostics. Use when running or inspecting terraform plans, applies, state
  files, imports, or state surgery, or when the bundled tfops script should
  handle the task. Do not use for IaC methodology or cloud design decisions -
  those route up to platform-engineering.
license: MIT
compatibility: >-
  Terraform CLI 1.5+ or OpenTofu CLI 1.6+ for delegated commands; the bundled
  tfops script runs on Python 3.8+ and its --help and state-file analysis need
  no terraform binary.
metadata:
  source: https://developer.hashicorp.com/terraform/docs
  spec: https://opentofu.org/docs/
---

# Terraform / OpenTofu Operations

Use this skill to run, inspect, and repair Terraform and OpenTofu infrastructure safely: understand a module graph, verify state backends and locking, review plans before applies, find and fix drift, work with remote state, plan version upgrades and refactors, and diagnose failures with evidence. This is a **tool skill** for one named tool (Terraform and its drop-in OpenTofu fork share one agent workflow and one trigger). Design decisions and IaC methodology belong to [platform-engineering](../platform-engineering/SKILL.md) and its `references/infrastructure-as-code.md`; this skill owns execution.

## Operating contract

1. **Discover before assuming.** Read the module layout, provider requirements, backend block, workspaces, `terraform.lock.hcl`, and CI invocation before running anything. Never infer state from a config file — the state file is the source of truth for what exists.
2. **Plan first, apply after review.** Every mutation goes through a visible plan (or `tfops` dry-run) and an explicit confirmation. Never run `apply` with unreviewed changes.
3. **Lock and scope state.** Confirm the backend supports locking and that the operator holds the lock before any state mutation. State surgery (`state mv`, `state rm`, `state push`) is a reviewed, scoped operation with a backup.
4. **Verify at the boundary.** A green `apply` is not proof of success: verify the external boundary (DNS, load balancer, API response) that the resource was supposed to satisfy, and check for drift on the next plan.
5. **Keep evidence bounded.** Never dump raw state files, backend credentials, or provider secrets into chat. `tfops` redacts nothing by itself but all outputs should be bounded summaries.

## The tfops script

`scripts/tfops` is an agent-first wrapper around the terraform/tofu CLI. It works without a terraform binary for `--help`, `doctor`, and direct `--state` analysis, so an agent can inventory a state file anywhere.

```bash
scripts/tfops doctor --json                 # binary, config, backend, state availability
scripts/tfops state --state state.json --json   # inspect a local state file directly
scripts/tfops plan --state state.json --json    # state-level plan summary (no binary needed)
scripts/tfops plan --json                   # full plan via terraform plan -json
scripts/tfops apply --dry-run --json        # preview only, never mutates
scripts/tfops apply --yes --json            # mutation: requires --yes
scripts/tfops apply --yes --force --json    # bypass the taint/drift guard after review
scripts/tfops import aws_instance.web i-0abc --dry-run
```

Mutation gate: `apply` and `import` refuse to run without `--yes` (exit 2); `--dry-run` previews without mutating; `--force` skips the taint/drift guard after the plan is reviewed. `TERRAFORM` env var overrides binary selection (`terraform` then `tofu` are auto-detected otherwise). Exit codes: 0 ok, 1 analysis/runtime error, 2 gate refusal, 127 binary missing, 124 timeout.

## Operating loop

1. **Inventory**: module tree, provider requirements, backend config, workspaces, lock file, state serial/lineage.
2. **Analyze**: `terraform validate`, `tfops plan --json` (or a state-file summary when the backend is unreachable).
3. **Review**: read the plan as a diff of resources, not a wall of text — count creates/updates/destroys, check replaces (destroy-before-create), spot-check sensitive changes.
4. **Apply**: scoped, confirmed, with a backend lock held; verify the boundary afterwards.
5. **Drift-check**: re-plan after changes and on a schedule; investigate diffs that should not exist.

## Module structure

- One module per unit of composition: inputs (variables), outputs, and resources with a single responsibility. Call modules from a root module; keep the root thin.
- Pin providers (`required_providers`) and module versions; commit `terraform.lock.hcl`.
- Use `for_each`/`count` for repetition, not code generation; use `templatefile` for config injection, and treat provisioners as a last resort.
- Structure conventions and composition patterns live in `references/01-modules-and-structure.md`.

## State backends and locking

- The backend owns state storage and locking. Default `local` backend stores state on disk; remote backends (S3+DynamoDB, GCS, Azure Storage, Terraform Cloud/OpenTofu Cloud, Consul) keep state off disk and enable collaboration.
- Locking prevents concurrent writers: always confirm the lock is held during applies and state surgery. A stale lock blocks operations until released (`force-unlock` only after verifying no other run is active).
- State holds secrets: encrypt the backend at rest, restrict read access, and mark sensitive values `sensitive = true`.
- Backend choice, migration (`terraform init -migrate-state` / `-reconfigure`), and lock troubleshooting: `references/02-state-and-backends.md`.

## Plan/apply workflow

- `plan` reads config + state + provider data and proposes a diff; `apply` realizes it. Treat `plan` output as the contract the apply will fulfill.
- Review destroys and replaces as the highest-risk changes; use `prevent_destroy` and `create_before_destroy` lifecycle rules where recreation is dangerous.
- Use `-target` only for emergencies, never as a habit; `-auto-approve` only inside a reviewed CI/CD gate.
- Full workflow, JSON plan output (`-json`), and review checklists: `references/03-plan-apply-workflow.md`.

## Drift detection

- Drift is the difference between declared config and actual infrastructure. A clean plan is the drift probe: schedule periodic plans and treat unexpected diffs as incidents.
- Distinguish intended drift (out-of-band manual change, external mutation) from unintended (config/state desync, provider bug).
- Remediation is `plan` + reviewed `apply` (reconcile), or `import` when the resource was never managed; never delete-and-recreate as a default reflex.
- `tfops` flags tainted resources in state analysis — those force replacement and should never be applied blind. Methods and cadence: `references/04-drift-detection.md`.

## Remote state

- Remote backends make state shared, durable, and lockable; local state is for experiments only.
- Consume another stack's outputs with `data "terraform_remote_state"` — reference by workspace/environment, never hand-copy outputs.
- The state file is not the delivery artifact: remote state must be protected (encryption, ACLs, audit) and recoverable (versioning, backups, restore drills). Practices: `references/05-remote-state-and-collaboration.md`.

## Upgrade and refactor flows

- Upgrades: read the upgrade guides for the version span, validate with `terraform validate`/`tofu validate`, run a plan, apply in a non-production environment first, and use `terraform state replace-provider` / `state mv` for provider-version or address changes.
- Refactors: rename or restructure resources with `moved` blocks (plan-safe, no state surgery), or reviewed `state mv` when `moved` does not fit; never delete state to force recreation.
- Version/support observations and step-by-step flows: `references/06-upgrades-and-refactors.md`.

## Diagnostics

Diagnose in evidence order: binary/version → config validation → backend + lock status → state serial/lineage → plan diff → apply error → boundary check.

- Lock errors: find the holder (backend-specific) before any `force-unlock`.
- State serial/lineage mismatches: a stale or foreign state; use `state pull`/`state push` only with a backup and reviewed scope.
- `tfops doctor` gathers the first layer of evidence; failure patterns and their probes live in `references/07-diagnostics.md`.

## Reference routing

| Load when | Reference |
|---|---|
| Module design, composition, or structure conventions | `references/01-modules-and-structure.md` |
| Backend choice, migration, or locking problems | `references/02-state-and-backends.md` |
| Planning, applying, or reviewing a change | `references/03-plan-apply-workflow.md` |
| Unexpected config-vs-reality differences | `references/04-drift-detection.md` |
| Shared or cross-stack state | `references/05-remote-state-and-collaboration.md` |
| Version bumps, provider migrations, or module refactors | `references/06-upgrades-and-refactors.md` |
| A failed apply, lock, or state error | `references/07-diagnostics.md` |
| Sources, version observations, and refresh procedure | `references/00-source-index.md` |

## Included artifacts

- `scripts/tfops`: agent-first wrapper (state analysis, plan/apply, gated mutations, JSON output).
- `tests/test_tfops.py` + `tests/fixtures/fixture-state.json`: deterministic tests against a bundled state fixture.
- `references/`: eight dated, source-indexed references covering the operational topics above.

## Verification boundary

| Claim | Minimum evidence |
|---|---|
| Config is valid | `terraform validate` (or `tofu validate`) exit 0 |
| State is readable | `tfops state --state FILE --json` parses and inventories it |
| Plan is safe | Reviewed plan diff with counts of create/update/destroy/replace and no tainted resources applied blind |
| Apply succeeded | Apply exit 0 **plus** the external boundary the resource serves responds correctly |
| No drift | A clean re-plan immediately after apply and on the declared cadence |

## Hard boundaries

- Never expose state files, backend credentials, provider secrets, or `sensitive` output values.
- Never run `apply`, `import`, `state push`, or `force-unlock` without the mutation gate (`--yes` after a reviewed plan, or an explicit human directive).
- Never delete state or a resource just to "fix" drift — reconcile or import.
- Never run a provider-specific procedure without checking the module's `required_providers` and version pins.

## When not to use

- **IaC methodology, tool selection, or cloud design decisions** — route up to [platform-engineering](../platform-engineering/SKILL.md).
- **Cloud provider depth** (AWS/GCP/Azure service-by-service operations) — provider references and platform patterns live under `platform-engineering`; this skill owns the Terraform/OpenTofu tool itself.
- **Ansible, Pulumi, CloudFormation, or CDK** — different tools with their own operational contracts; only Terraform/OpenTofu live here.
- **Designing a new module from scratch** (composition, interfaces, versioning policy) — start from `platform-engineering` methodology, then execute with this skill.
