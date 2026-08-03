# Modules and structure

Operational guidance for working with Terraform/OpenTofu module trees. Design methodology (when to split, interface contracts, registry conventions) lives in `platform-engineering`; this file is the execution-side structure playbook.

## Reading a module tree

- Locate the root module (the working directory with the backend/state) and the called modules (`module "name" { source = ... }`).
- Check `required_providers` in each module's `versions.tf` or `terraform.tf` for provider source and version constraints; the root pins what the tree may use.
- `terraform.lock.hcl` records exact provider versions: commit it, and use `terraform providers lock` to add platforms deterministically.
- `terraform graph` / `terraform providers` / `terraform version` give the resolved picture; never guess the provider set from imports alone.

## Composition conventions

- One module per unit of composition: inputs, outputs, resources with a single responsibility. A root module stays thin and wires modules together.
- Use `for_each` (maps) or `count` (indexed lists) for repetition; conditional creation via `count = var.enabled ? 1 : 0`.
- Inject configuration with `templatefile`; read external data via data sources, not `file` at plan time where freshness matters.
- Provisioners (`local-exec`/`remote-exec`) are a last resort: prefer provider-native mechanisms and exit statuses over scripted side effects.

## Interface discipline when operating someone else's module

- Read the variable defaults and validations before changing a call site; a `validation` block tells you the contract the module enforces.
- Prefer module outputs over reaching into the module's internals; referencing an internal resource of another module breaks encapsulation.
- When a module is pinned to a tag or registry version, record which version is in use before any upgrade (see `06-upgrades-and-refactors.md`).

## Sources

> **Last Updated:** 2026-08-03
- Terraform module overview and structure: https://developer.hashicorp.com/terraform/language/modules (accessed 2026-08-03)
- Module development / composition patterns: https://developer.hashicorp.com/terraform/language/modules/develop (accessed 2026-08-03)
- OpenTofu modules documentation: https://opentofu.org/docs/language/modules/ (accessed 2026-08-03)
- Provider lock file mechanics: https://developer.hashicorp.com/terraform/language/dependency-lock (accessed 2026-08-03)
