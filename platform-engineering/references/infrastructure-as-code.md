# Infrastructure as Code — Reference

> **Last Updated:** 2026-08-03
> Patterns and decision guidance for infrastructure-as-code. Operational commands and runbooks belong to the tool skills (`terraform`, `kubernetes`, `docker-compose`); this file carries the judgment frameworks for choosing, structuring, and reviewing IaC.

## Tool Selection — Decision Guidance

### Terraform / OpenTofu

- **Core concepts:** Resources, data sources, providers, state (local, remote backends), modules, variables, outputs, lifecycle rules (`create_before_destroy`, `prevent_destroy`)
- **State management:** Remote backends (S3 + DynamoDB, GCS, Azure Storage, Terraform Cloud), state locking, state migration, workspaces for env separation, `terraform state` subcommands (mv, rm, pull, push)
- **Module design:** Composition (call smaller modules), version pinning, registry conventions (hashicorp/terraform-google-modules), output minimal surface area, internal vs published modules
- **Advanced patterns:** `for_each`/`count` for dynamic resources, `templatefile` for config injection, file/external data sources for bridge to external systems, provisioners as last resort (remote-exec/local-exec)
- **OpenTofu specifics:** Drop-in Terraform replacement, same HCL syntax, OSS license (no BSL change), `tofu` CLI, supports encryption at rest in state natively, enhanced provider signing
- **When to choose:** The default for cloud resource provisioning. Largest provider ecosystem, most transferable skills, works across all three major clouds. Choose OpenTofu when license/BSL or state encryption is a hard requirement.

### Pulumi

- **Core model:** Infrastructure as real code — Go, Python, TypeScript, .NET, Java, YAML
- **Key concepts:** Programs (stack definitions), stacks (env instances), resources, components (custom abstractions), providers (Pulumi-native, TF bridge), outputs, config/secret management
- **State:** Pulumi Cloud (managed), self-managed backends (S3, GCS, Azure Blob S3-compatible), state encryption
- **Automation API:** Embed Pulumi in applications (CI/CD, self-service platforms), inline updates, preview + deploy in code
- **Bridge to Terraform:** TF bridge adapter wraps existing TF providers as native Pulumi providers — convenient but adds a layer
- **When to choose:** Teams that need real programming-language logic (loops, conditionals, tests) inside the IaC layer, or who are building self-service automation and want the Automation API.

### Ansible

- **Core model:** Agentless — SSH/WinRM transport, push-based, YAML playbooks, Jinja2 templating
- **Key concepts:** Inventory (static, dynamic from cloud APIs), modules (idempotent operations), roles (reusable content packages), playbooks (execution order), variables and facts, handlers (notify-based triggers)
- **Best practices:** Role-based layout, vault for secrets, molecule for testing, ansible-lint, `--check --diff` for dry-run, `--limit` for targeted execution
- **Use case in platform engineering:** Day-2 configuration (post-provisioning), OS hardening, agent installation, but generally less suited than Terraform for cloud resource provisioning
- **When to choose:** Configuration management of existing servers and day-2 operations; not the right tool for the initial cloud resource graph.

### CloudFormation / CDK

- **CloudFormation:** Native AWS IaC — JSON/YAML templates, stacks, nested stacks, change sets, drift detection, stack sets (multi-account, multi-region)
- **CDK (Cloud Development Kit):** CloudFormation as real code (TypeScript, Python, Go, Java, C#) — constructs (L1/L2/L3 abstraction), `cdk synth` → CloudFormation template, `cdk deploy` / `cdk diff`, context, aspects, permissions boundaries
- **CDKTF (CDK for Terraform):** Bridge for Terraform providers in CDK languages — cross-platform between AWS and non-AWS providers
- **When to choose:** AWS-only shops that want native drift detection and change-set review, or teams already writing real code who prefer CDK's type safety over HCL.

## State and Drift Governance

- **State is a source of truth, not a database:** treat state as a serialized representation of the resource graph, never edit it directly; all changes go through `plan`/`apply` (or the equivalent)
- **Remote backend with locking is non-negotiable:** local state is a team-of-one anti-pattern; choose S3+DynamoDB, GCS, Azure Storage, or Terraform Cloud/Pulumi Cloud and make locking explicit
- **Drift detection cadence:** run periodic plans (`plan` on a schedule, `drift detect` in Terraform Cloud, or cloud-native drift tools) and review unintended diffs before they become incidents
- **Workspaces vs directories:** prefer directory-per-environment with shared modules over workspaces when environments differ materially; use workspaces only for near-identical instances
- **Import-before-manage:** adopt pre-existing resources with `terraform import`/state moves rather than `delete + recreate`; plan for state surgery (`state mv`, `state rm`) only with a locked state and a reviewed plan

## Secrets in IaC

- **Never commit secrets in plaintext:** secrets in HCL/JSON/YAML drift into state and logs; use provider-native secret references (`data "aws_secretsmanager_secret_version"`), Vault dynamic credentials, or SOPS/age for encrypted-at-rest config
- **Prefer dynamic credentials:** database and cloud keys should come from Vault dynamic secrets or managed identity (IRSA, Workload Identity) rather than static long-lived keys
- **State encryption:** OpenTofu encrypts state natively; on Terraform, encrypt the state backend at rest and restrict state read access (state holds secrets)
- **Mark sensitive outputs:** `sensitive = true` so values are redacted in logs and plan output; keep the full secret in the manager, only a reference in IaC

## Review Checklist Patterns

- **Composition over monoliths:** root modules should call child modules; a module that owns VPC + cluster + IAM + app is a candidate for splitting
- **Parameterize environment specifics:** no hardcoded account IDs, regions, or names; variables + data sources + consistent naming convention
- **Minimal outputs:** expose only what consumers need; every output is API surface
- **Plan review before apply:** review the plan for unintended replaces/deletes, not just additions; enforce a human gate on destructive changes
- **Tagging and cost attribution:** consistent tags (`CostCenter`, `Environment`, `Owner`, `Service`) enforced at plan time by guardrails/validators
- **Lifecycle rules:** `prevent_destroy` on irreplaceable resources (databases, state backends); `create_before_destroy` where downtime matters

## Sources and Dated References

- OpenTofu documentation and state encryption: https://opentofu.org/docs/ (accessed 2026-08-03)
- Terraform module composition best practices: https://developer.hashicorp.com/terraform/tutorials/modules (accessed 2026-08-03)
- Pulumi documentation (stacks, state, Automation API): https://www.pulumi.com/docs/ (accessed 2026-08-03)
- Ansible best practices (roles, vault, molecule): https://docs.ansible.com/ansible/latest/tips_tricks/sample_setup.html (accessed 2026-08-03)
- AWS CDK reference: https://docs.aws.amazon.com/cdk/v2/guide/home.html (accessed 2026-08-03)
