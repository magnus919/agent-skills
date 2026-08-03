# Source index and maintenance contract

Research and verification date: 2026-08-03

## Primary sources

### Terraform (HashiCorp)

- https://developer.hashicorp.com/terraform/docs
- https://developer.hashicorp.com/terraform/cli/commands
- https://developer.hashicorp.com/terraform/language/modules
- https://developer.hashicorp.com/terraform/language/state/backends
- https://developer.hashicorp.com/terraform/language/state/locking
- https://developer.hashicorp.com/terraform/language/state/remote-state-data
- https://developer.hashicorp.com/terraform/cli/commands/plan
- https://developer.hashicorp.com/terraform/internals/json-format
- https://developer.hashicorp.com/terraform/language/modules/develop/refactoring
- https://developer.hashicorp.com/terraform/upgrade-guides
- https://developer.hashicorp.com/terraform/cli/commands/state/mv
- https://developer.hashicorp.com/terraform/cli/commands/import
- https://github.com/hashicorp/terraform/releases

### OpenTofu (Linux Foundation)

- https://opentofu.org/docs/
- https://opentofu.org/docs/language/state/backends/
- https://opentofu.org/docs/language/state/locking/
- https://opentofu.org/docs/language/modules/develop/refactoring/
- https://opentofu.org/docs/cli/commands/
- https://opentofu.org/blog/opentofu-1-12-0/
- https://github.com/opentofu/opentofu/releases

### Ecosystem and operational context

- https://endoflife.date/terraform
- https://endoflife.date/opentofu
- https://www.terraform.io/language/state (state-purpose and remote-state guidance)

## Verified release observations (2026-08-03)

| Product | Observation | Verification |
|---|---|---|
| Terraform | 1.15.x is the current stable line (1.15.8 as of July 2026); 1.16 is in alpha/beta; 1.13 reached EOL 2026-04-29 | Official release pages and eol tracking |
| OpenTofu | 1.12.x is the current line (1.12.0 released 2026-05-14; 1.12.5 as of July 2026); 1.9 reached EOL 2026-05-14 | OpenTofu blog and release pages |
| State format | Terraform state JSON format version 4 (serial and lineage fields) | State file format documentation |

These are dated observations, not promises. Refresh them before asserting a current version or support status.

## Refresh procedure

1. Re-check the official Terraform and OpenTofu release pages and the eol tracking pages above.
2. Compare version lines, deprecations, backend defaults, and upgrade guides against the references in this skill.
3. Record discrepancies before editing guidance; never update a version number without its source URL, retrieval date, and support interpretation.
4. Re-run `terraform/scripts/tfops` tests and the repository validators.
