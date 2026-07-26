---
name: grafana
description: >-
  Operate, configure, provision, secure, and troubleshoot Grafana OSS, Enterprise, and Cloud, including dashboards, folders, data sources, annotations, alert rules, contact points, notification policies, silences, mute timings, service accounts, RBAC, plugins, APIs, and as-code workflows. Use for Grafana product work and Grafana-side integrations. Do not use for defining SLOs or paging policy, operating Prometheus/Loki/Tempo/InfluxDB backends, generic Docker/Kubernetes/Terraform/reverse-proxy work, plugin development, or authorized security assessments; use the corresponding specialist skill.
license: MIT
compatibility: Requires current Grafana documentation and authorized access to the target for live operations. API work requires an HTTP client and appropriately scoped Grafana credentials.
metadata:
  source: https://grafana.com/docs/grafana/latest/
  source_index: references/source-index.md
  research_checked: "2026-07-26"
---

# Grafana Operations

Treat Grafana as a set of versioned, separately authorized resources with explicit owners. Discover the target, resource provenance, and effective routing before proposing a mutation. A healthy server or attractive dashboard is not proof that provisioning, queries, alert evaluation, or notification delivery works.

## Operating contract

1. Identify Grafana version, edition, deployment mode, organization, folder or namespace, authentication model, and current permission scope before selecting an API or workflow.
2. Inventory existing file provisioning, Terraform/provider state, Git Sync, Grafana Operator resources, and API/UI-managed objects. Assign one authoritative owner per resource UID before changing it.
3. Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.
4. Treat dashboard, folder, data-source, alerting, user/RBAC, plugin, and server-configuration changes as separate authorization scopes.
5. Never print, commit, or preserve secret values from service-account tokens, passwords, `secureJsonData`, decrypted receiver settings, OAuth secrets, signing keys, SMTP credentials, or webhooks. Preserve supported secure configuration fields through their authorized secret mechanism and record redacted metadata only.
6. Validate dashboard and alert queries against the real data source when access exists. Otherwise state the offline limitation and do not claim semantic correctness.
7. Verify the requested boundary. Server health does not prove dashboard provisioning; rule firing does not prove routing; notification delivery does not prove resolution behavior.

## When not to use

Use `site-reliability-engineering` to define SLIs, SLOs, error budgets, page-worthiness, severity policy, escalation, and incident practice. Use data-source-specific guidance for PromQL, LogQL, TraceQL, Flux, SQL, storage, and backend operation. Use `docker-compose`, `kubernetes`, `traefik`, or `platform-engineering` for their infrastructure control planes. Use `secure-software-engineering` for preventive security design and `security-audit-methodology` for an authorized assessment. This skill owns Grafana product behavior and Grafana-side integration.

## Read-only discovery

Collect only what the current access permits:

```sh
grafana server -v
curl --fail --silent --show-error "$GRAFANA_URL/api/health"
```

For containers, packages, Helm, or Cloud, use the owning platform's read-only inventory to establish the image/tag, configuration path, deployment mode, and public boundary. Do not dump process environments or resolved configuration containing secrets. With an authorized service-account token, prefer bounded GET requests for the exact resource class; send the token through a protected environment or credential store, not command history or reports.

Record:

- version and edition: OSS, Enterprise, or Cloud;
- deployment owner and persistence: package, container, Compose, Kubernetes, Helm, Operator, or managed stack;
- organization, folder, namespace, and target environment;
- authentication method and effective permissions;
- data-source UIDs and types without secure fields;
- dashboard/folder UIDs, alerting resources, and their provenance;
- provisioning providers, watched paths, polling interval, deletion/edit settings, and duplicate ownership;
- rollback source and the boundary that can be tested safely.

Read [API and version discovery](references/api-and-version-discovery.md) before choosing endpoints. Grafana 12 introduced the new `/apis` model, while legacy `/api` routes begin deprecation in Grafana 13 and do not yet have complete one-to-one replacements.

## Route the task

| Need | Read first |
|---|---|
| Discover version, edition, auth, organization, resource APIs, and permission scope | [API and version discovery](references/api-and-version-discovery.md) |
| Design or review dashboards, panels, variables, units, transformations, links, annotations, library panels, JSON, or accessibility | [Dashboard engineering](references/dashboard-engineering.md) |
| Build or diagnose rule evaluation, labels, contact points, policies, grouping, silences, mute timings, templates, and delivery | [Alerting and routing](references/alerting-and-routing.md) |
| Choose or reconcile file provisioning, Terraform, Git Sync, API, Foundation SDK, or Operator ownership | [Provisioning and GitOps](references/provisioning-and-gitops.md) |
| Diagnose blank panels, query/auth failures, provisioning drift, failed evaluations, missing notifications, or proxy/auth problems | [Troubleshooting](references/troubleshooting.md) |
| Handle credentials, users, service accounts, RBAC, plugins, deletion, sharing, or production-impacting change | [Security and change control](references/security-and-change-control.md) |
| Check evidence, version currency, live findings, or refresh rules | [Source index](references/source-index.md) |

## Safe workflow

### 1. Define the operational outcome

Name the audience, decision, resource UIDs, authoritative owner, target environment, expected interruption, verification method, and rollback. For dashboards, declare the observability method or question. For alerts, declare owner, severity rationale, runbook/dashboard link, expected route, and noise risk.

### 2. Reconcile ownership before content

Compare the running object with every potential writer. Do not edit a provisioned resource through another surface merely because that surface permits it. Detect overlapping provider paths, duplicate UIDs or titles, Terraform/API drift, UI edits that will be overwritten, and deletion or pruning behavior before changing files or objects.

### 3. Validate semantics before presentation

Run representative queries over a known time range. Confirm metric/log/trace type, units, labels, aggregation, cardinality, null/no-data behavior, time zone, refresh interval, and query cost. For repeated panels or multi-dimensional alerts, bound the dimension set and prove it remains actionable.

### 4. Preview and apply through the owner

Use the authoritative source and the narrowest supported operation. Review diffs and exported backups with secrets redacted. A policy-tree replacement, `prune`, provider-source removal, UID reuse, RBAC change, plugin install, or data-source/dashboard deletion requires explicit confirmation immediately before mutation.

### 5. Verify each affected plane

| Plane | Minimum evidence |
|---|---|
| Server | Versioned process responds and database health is reported; bounded logs show no new failure loop |
| Provisioning | One owner per UID/path; reconciliation completes; no duplicate/drift warnings across more than one scan |
| Data source | Authorized health/query test succeeds with expected time range and representative data |
| Dashboard | Queries are semantically valid; units/labels/empty states render correctly; links and variables preserve context |
| Alert evaluation | Expected normal, pending, firing, no-data/error, and recovery behavior is observed or explicitly untested |
| Notification routing | Actual labels select the intended policy/contact point; grouping and mute behavior are checked |
| Delivery | A controlled test reaches the intended receiver and a resolved notification is observed when permitted |
| Access | Intended role can act; a lower-privilege role cannot; secrets remain redacted |

## Approval boundaries

Explicit approval is required before password resets; user, organization, team, service-account, or RBAC changes; plugin installation or removal; data-source, dashboard, folder, alert-rule, contact-point, or policy deletion; notification-policy replacement; live notification tests; provisioning reloads or service restarts; secret rotation; anonymous/public sharing changes; or direct database recovery. Never edit Grafana's database directly unless the user explicitly authorizes a documented recovery procedure after backup and supportable alternatives are exhausted.

## Exit criteria

The task is complete when the requested resource or diagnosis is tied to a known Grafana version and owner, relevant queries or routes are validated at the strongest authorized boundary, no secret was exposed, and rollback remains available. List every stronger boundary not exercised, including authenticated API inventory, live data-source queries, alert firing, receiver delivery, resolved notifications, accessibility testing, reload/restart persistence, or production behavior.
