# Terraform — Operational Skill for Terraform and OpenTofu

Run, inspect, and repair Terraform and OpenTofu infrastructure safely: module structure, state backends and locking, plan/apply workflow, drift detection, remote state, upgrades and refactors, and diagnostics with evidence.

## Why Install This Skill

Your agent can operate a Terraform codebase end to end: understand the module graph, verify the backend and lock are healthy, review a plan before anything is applied, detect and reconcile drift, work with remote state, and plan version upgrades and module refactors without guessing. It ships a small wrapper script (`tfops`) that analyzes state files directly — so an agent can inventory what a state file describes even when it has no terraform binary on the machine.

The references are distilled from the official Terraform and OpenTofu documentation with dated sources, favoring verification commands and explicit mutation gates over copy-paste optimism. Design decisions (which IaC tool, how to structure modules, provider strategy) intentionally route up to `platform-engineering`; this skill owns the day-to-day operation of the tool itself.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop, mutation gates, and verification boundaries |
| `references/` | Eight dated references: modules, state/backends, plan/apply, drift, remote state, upgrades/refactors, diagnostics, source index |
| `scripts/tfops` | Agent-first wrapper: `--json` output, direct state-file analysis, and an apply gate that checks and applies the same saved plan |
| `tests/` | Deterministic tests plus a bundled fixture state file |

## Quick Start

```bash
# Inventory a state file without any terraform binary installed
python3 scripts/tfops doctor --json
python3 scripts/tfops plan --state tests/fixtures/fixture-state.json --json

# With terraform (or OpenTofu) installed, in a config directory
terraform init
python3 scripts/tfops plan --json
python3 scripts/tfops apply --dry-run --json
python3 scripts/tfops plan --save-plan reviewed.tfplan --json
# Review the saved plan before applying
python3 scripts/tfops apply --yes --plan reviewed.tfplan --json
```

The `--help` output documents every flag and works without the terraform binary. Create plans for guarded apply with `tfops plan --save-plan FILE`; this explicitly enables refresh and writes a SHA-256 sidecar. Apply checks the sidecar, snapshots the plan, checks taint/drift from `terraform show -json`, and passes that same snapshot to Terraform. `--force` bypasses detected findings only after valid plan evidence is available. The sidecar is local provenance against accidental plan mix-ups, not a cryptographic signature. Set the `TERRAFORM` environment variable to a specific binary (e.g., `tofu`) when both are installed.

## Triggers

Load this skill for `terraform`, `OpenTofu`, `tofu`, `tfstate`, `terraform plan/apply/import`, state backends and locking, drift between config and infrastructure, remote state, Terraform version upgrades, module refactors (`moved` blocks, `state mv`), or any Terraform plan/apply/state error. Do not load it for IaC methodology or cloud design decisions — that is `platform-engineering`.

## Requirements

- Python 3.8+ for the `tfops` script (`--help` and state-file analysis need no other dependency).
- Terraform CLI 1.5+ or OpenTofu CLI 1.6+ only for delegated commands (`plan`, `apply`, `validate`, `import`) against a real backend.
- Backend access (credentials, network) for remote state operations.
