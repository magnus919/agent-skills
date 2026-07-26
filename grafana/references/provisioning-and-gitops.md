# Provisioning and GitOps

Grafana supports multiple as-code and automation paths. They are not interchangeable. Choose one authoritative owner per resource and reconcile existing state before adopting another.

## Ownership inventory

For each UID, record:

| Field | Question |
|---|---|
| Resource | Dashboard, folder, data source, alert rule/group, receiver, policy tree, template, mute timing, RBAC object, or plugin configuration? |
| Target | Version, edition, organization, folder/namespace, environment? |
| Owner | File provider, Terraform, Git Sync, API/SDK, Operator/Crossplane, UI, or another controller? |
| Source | Repository/path/state address and revision? |
| Reconcile | Startup, poll/watch, webhook, controller loop, plan/apply, or manual request? |
| Delete behavior | `prune`, delete list, source removal, provider deletion, Terraform destroy, or policy reset? |
| Edit behavior | Is UI editing blocked, allowed but overwritten, or authoritative? |
| Rollback | Revert, prior state/config, version history, export, backup, or provider rollback? |

Inventory every potential writer. Duplicate UIDs, overlapping provider paths, copied dashboards, and multiple controllers can create conflict even when each configuration is individually valid.

## File provisioning

Self-hosted Grafana reads provisioning files for data sources, dashboards, plugins configuration, alerting, and some Enterprise RBAC behavior.

- Dashboard provisioning needs a provider YAML and a path containing dashboard definitions. Merely placing JSON under a conventional directory is not sufficient.
- Use stable UIDs. Avoid duplicate UIDs and duplicate titles in a folder.
- `allowUiUpdates: true` permits database saves but does not write changes back to the file. A later file update overwrites the database copy regardless of the JSON version field.
- Removing a provisioned dashboard source can delete the database dashboard unless `disableDeletion: true`.
- Multiple providers must not scan the same files. Grafana can reject database writes when duplicate UIDs/titles are claimed by overlapping providers.
- Polling and filesystem watch behavior depends on `updateIntervalSeconds`; mounted/network filesystems may not deliver watch events.
- Data-source `deleteDatasources` runs before add/update. `prune: true` removes resources absent from the provisioning file and can act when the file itself disappears.
- In multi-instance deployments, data-source version fields prevent older configurations from overwriting newer ones.
- File-provisioned alerting is self-hosted only and can be reloaded through an administrative operation. Reload/restart is a mutation requiring scope and rollback.

## Terraform and provider workflows

Use Terraform when the organization already operates Terraform and the provider covers the required resources.

1. Pin provider versions and inspect target Grafana compatibility.
2. Import existing resources before declaring them, preserving UIDs and folder context.
3. Review `plan` for replacement, deletion, policy-tree changes, secret handling, and provider drift.
4. Protect state as sensitive operational data; it can contain resource details and secrets.
5. Apply to a non-production or canary target when practical.
6. Verify in Grafana and on the next plan. A zero-change plan is useful drift evidence, not runtime proof.

Do not let Terraform and file/Git/UI ownership overlap for the same UID.

## Git Sync and observability as code

Grafana 12 introduced new APIs and official tooling including Git Sync, `gcx`, and Foundation SDKs. Availability and maturity depend on target version and edition.

- Confirm Git Sync support and repository permissions on the target before designing around it.
- Define branch, folder mapping, review, merge, reconciliation, conflict, and rollback behavior.
- Preserve stable UIDs and choose classic versus newer dashboard resource schemas deliberately.
- The newer dynamic/dashboard-v2 model requires the Kubernetes resource format where supported.
- Prefer the Foundation SDK over unsupported Grafonnet for new programmatic dashboard generation when the supported languages and target capabilities fit.
- Do not migrate solely because a newer workflow exists. Migrate when it creates one clear owner and a tested rollback.

## Operator and Kubernetes-native ownership

The Grafana Operator and Crossplane introduce controller reconciliation and custom resources. Use `kubernetes` for cluster mechanics and controller health. Here, verify resource scope, instance selectors, UID preservation, secret references, supported Grafana resources, controller ownership, and what happens to direct UI edits.

## Migration sequence

1. Freeze concurrent writers or establish a controlled change window.
2. Inventory live resources and all owners by UID.
3. Export or back up non-secret definitions and record version history.
4. Choose the destination owner and prove schema/version support.
5. Import/adopt without creating duplicate ownership.
6. Preview deletion, pruning, replacement, and policy-tree effects.
7. Reconcile in a test target or bounded subset.
8. Remove the old owner only after the new owner is verified.
9. Verify resource content, links, queries, permissions, alert routes, and persistence across another reconciliation cycle.
10. Confirm the old owner no longer proposes changes.

## Secrets

- Put data-source passwords, TLS private keys, custom authorization headers, and receiver credentials in `secureJsonData`, secure settings, Compose/Kubernetes secrets, or an external secret manager as supported.
- Environment interpolation is not a secret manager. Protect the source and runtime environment.
- Grafana performs two `$` substitution passes in provisioning. Use the documented escaping rules for literal dollars, including alert templates that contain `$labels` or similar expressions.
- Do not commit resolved provisioning output or exported decrypted receiver settings.

## Rollback and verification

Rollback through the authoritative owner: revert Git, restore the prior Terraform configuration/state relationship, restore provider files, or issue a version-aware API update. Do not roll back by editing Grafana's database.

After reconciliation, verify one owner per UID/path, no duplicate/drift warnings across multiple cycles, expected editability, stable URLs, successful representative queries, correct alert routing, and no unintended deletions.
