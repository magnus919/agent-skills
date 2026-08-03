# Drift detection

Drift is the difference between declared configuration and actual infrastructure. The plan is the drift probe: a plan that shows changes against a supposedly stable environment is drift, whether intended or not.

## Proving the diff is real

Before remediating, prove the diff is real:

1. Check the state serial and lineage (`tfops state --state FILE --json` shows both): a stale serial means the local state is behind the backend, not that the world changed.
2. Compare against the previous known-good plan for the same workspace.
3. Check git history and change records: was the config touched? Was a plan applied that CI never recorded?
4. Only then classify the cause:
   - **Out-of-band manual change**: someone changed the live resource (console, another tool). Config is the desired state — reconcile with a reviewed apply.
   - **Unapplied config change**: config was edited but never applied. Apply it deliberately after review.
   - **State/config desync**: resource was created outside Terraform and never imported, or state was edited. Import the resource (`terraform import` / `tfops import`) instead of delete-and-recreate.

## Cadence and automation

- Schedule periodic plans (CI cron or a drift-detection run) and treat unexpected diffs as incidents with owners.
- Cloud-hosted runs (Terraform Cloud/OpenTofu Cloud) can run drift detection on a schedule and notify; self-managed teams build the cron equivalent with `plan -refresh-only` or plain plans.
- After any remediation, re-plan to confirm the diff is gone; a clean plan is the drift-free proof.

## Remediation rules

- Reconcile with plan + reviewed apply. Never delete-and-recreate as a default reflex — a resource's data may be irreplaceable.
- Import-before-manage: adopt pre-existing resources with `import` rather than deleting and rebuilding.
- Tainted resources (`tfops` lists them under `tainted`) force replacement on the next apply: review why they were tainted before applying, and never apply them blind.
- Distinguish intended drift (deliberate out-of-band action with a record) from incidents; both still end with a clean plan or a documented, reviewed exception.

## Sources

> **Last Updated:** 2026-08-03
- Terraform state purpose and refresh: https://developer.hashicorp.com/terraform/language/state (accessed 2026-08-03)
- Import command: https://developer.hashicorp.com/terraform/cli/commands/import (accessed 2026-08-03)
- Drift detection in Terraform Cloud: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/drift-detection (accessed 2026-08-03)
- OpenTofu state documentation: https://opentofu.org/docs/language/state/ (accessed 2026-08-03)
- IaC review and drift-baseline checklist (methodology): `platform-engineering/templates/iac-review-record.md` (accessed 2026-08-03)
