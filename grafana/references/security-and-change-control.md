# Security and Change Control

Grafana brokers access to data sources, dashboards, alerts, receivers, plugins, and administration. A dashboard permission is not a complete data-access boundary.

## Assets and trust boundaries

Protect:

- service-account and legacy API tokens;
- data-source credentials, TLS keys, custom headers, and `secureJsonData`;
- notification webhooks, integration keys, SMTP credentials, and templates;
- OAuth/OIDC/SAML/LDAP/auth-proxy secrets and identity headers;
- dashboard queries, annotations, snapshots, reports, and rendered images;
- Terraform state, provisioning repositories, backups, and Grafana database encryption keys;
- organization, folder, data-source, alerting, and receiver permissions.

Map browser/client, reverse proxy, Grafana server, database, plugins, data sources, notification receivers, identity provider, and automation as separate trust boundaries.

## Authentication and service accounts

- Use an identity provider for people and service accounts for automation.
- Avoid shared administrator credentials and legacy API keys for new automation.
- Scope service accounts to one organization and the minimum actions/resources. Use separate tokens for separate clients to support audit and rotation.
- Set short token expiration where possible. Rotate without exposing the old or new value.
- Service accounts cannot perform instance-wide user/organization administration; do not grant a human session to automation as a workaround.
- Protect auth-proxy identity headers so only the trusted proxy can set them.

## Authorization realities

- Server administrator, organization role, folder/dashboard permission, Enterprise RBAC, and data-source permission are distinct layers.
- In standard organization roles, Viewers can issue arbitrary queries to data sources they can access, not only queries embedded in allowed dashboards.
- Folder permissions are a primary dashboard boundary, but they do not constrain the backend data source by themselves.
- Restrict backend credentials and schemas, use separate organizations/data sources when needed, and use Enterprise/Cloud data-source permissions where available.
- Test both an intended role and a lower-privilege role. UI visibility is not authorization proof; test the API/query boundary.

## Data-source and outbound request safety

- Restrict allowed data-source hosts/IPs and outbound network paths where supported.
- Treat data-source URLs, plugin resources, webhooks, image/rendering URLs, and callback destinations as server-side request boundaries.
- Verify TLS certificates and server names. Do not normalize `tlsSkipVerify` into an acceptable production default.
- Use least-privilege backend credentials and read-only accounts where the workload permits.
- Never expose secure fields in diagnostics. Redacted/"configured" state is enough for ordinary inspection.

## Sharing and anonymous access

Anonymous access can allow anyone to view Viewer-accessible dashboards, list folders, dashboards, and data sources through read APIs, and issue arbitrary queries against data sources available to the anonymous organization role. Before enabling it, review every current and future dashboard, folder permission, data source, queryable data class, and API exposure.

Treat public/shared dashboards, snapshots, reports, embeds, playlists, and rendered images as separate disclosure paths. Check whether data is live or copied, whether URLs are revocable, and whether variables or annotations disclose sensitive context.

## Plugins

- Record plugin source, signature status, version, compatibility, permissions, network/data access, and rollback.
- Installation/removal is an explicit approval boundary and may require restart or migration.
- Provisioning plugin configuration does not install the plugin itself.
- Route plugin development to Grafana's plugin-development documentation; this skill covers operation and risk.

## Change classes

| Class | Examples | Gate |
|---|---|---|
| Read-only | version, health, metadata, redacted config, logs, query inspection | May proceed within authorized scope |
| Reversible configuration | dashboard update through owner, rule threshold, provider mapping | Confirm target, scope, rollback, verification |
| External effect | test alert, report/email, webhook, public sharing | Explicit receiver/audience approval |
| Access/security | password reset, user/team/service account, RBAC, auth, tokens, anonymous access | Explicit approval and lower-privilege verification |
| Destructive | delete/prune/reset policy tree, remove data source/folder/dashboard/rule/plugin, direct DB recovery | Explicit directive, backup/recovery evidence, narrow target |
| Production interruption | reload, restart, upgrade, database/plugin migration | Change window, expected interruption, rollback, external-boundary check |

Before any mutation, capture target/UID, authoritative owner, exact diff, affected users/automation, expected interruption, secret handling, rollback artifact/command, stop condition, and verification owner.

## Backup and rollback

- Back up the authoritative source and metadata needed to preserve UIDs, folders, permissions, and policy relationships.
- For self-hosted recovery, protect both the Grafana database and configuration/secret-encryption material. A database copy without required keys/configuration may not restore secure settings usefully.
- Test restore on a separate target when recovery is part of the claim.
- Do not treat dashboard version history as full platform backup.
- Do not edit the database directly except under an explicitly authorized, version-matched recovery procedure with backup and post-recovery verification.

## Security verification

Verify authentication, intended and denied authorization, secret redaction, outbound destination restrictions, audit/log evidence where available, public/anonymous exposure, plugin trust, and rollback. Use `secure-software-engineering` for a full preventive threat model and `security-audit-methodology` for an authorized assessment.
