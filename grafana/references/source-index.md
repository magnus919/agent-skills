# Source Index

Research checked **2026-07-26**. Current upstream release observed through the GitHub releases API: Grafana **13.1.1**, published 2026-07-21. Operational guidance must still be refreshed against the target because supported deployments can run older major versions and Grafana's API migration is in progress.

## Coverage matrix

| Required capability | Primary evidence | Skill reference | Status |
|---|---|---|---|
| Version, edition, auth, API and resource scope | API overview/migration, service accounts, roles | `api-and-version-discovery.md` | Covered with target capability gate |
| Dashboard design/review | Build dashboards, JSON model, variables, links, annotations, library panels, best practices | `dashboard-engineering.md` | Covered with live-query limitation |
| Alert evaluation and routing | Alerting fundamentals/best practices, policies, contact points, silences/mute timings | `alerting-and-routing.md` | Covered end to end |
| Provisioning and GitOps | Provisioning, alert file/API provisioning, as-code, Git Sync, Terraform/Operator | `provisioning-and-gitops.md` | Covered with ownership model |
| Troubleshooting | Troubleshooting docs plus live Grafana 11 duplicate-provider evidence | `troubleshooting.md` | Covered by diagnostic chains |
| Security/change control | Security, roles, service accounts, provisioning secret behavior | `security-and-change-control.md` | Covered with mutation gates |

## Primary Grafana documentation

| Area | Source | Claims used |
|---|---|---|
| Documentation index | https://grafana.com/docs/grafana/latest/ | Current product documentation root |
| Provisioning | https://grafana.com/docs/grafana/latest/administration/provisioning/ | Data-source/dashboard providers, environment interpolation, deletion/pruning, UI overwrite, polling/watch behavior, secure JSON |
| As-code overview | https://grafana.com/docs/grafana/latest/as-code/ | Observability-as-code and infrastructure-as-code split |
| Observability as code | https://grafana.com/docs/grafana/latest/as-code/observability-as-code/ | Grafana 12 APIs, `gcx`, Git Sync, Foundation SDK, file provisioning, Grafonnet support boundary |
| Infrastructure as code | https://grafana.com/docs/grafana/latest/as-code/infrastructure-as-code/ | Terraform, Ansible, Operator, Crossplane capabilities and ownership behavior |
| Dashboard building | https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/ | Variables, links, annotations, library panels, JSON, version history |
| Dashboard best practices | https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/ | Audience/story, RED/USE/Golden Signals, cognitive load, query load, drill-down, version control |
| Alerting fundamentals | https://grafana.com/docs/grafana/latest/alerting/fundamentals/ | Rule evaluation, multidimensional instances, contact points, policy routing, grouping, silences/mute timings |
| Notification policies | https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/notification-policies/ | Tree selection, deepest-match routing, sibling continuation, inheritance, multiple-policy option |
| Configure notification policies | https://grafana.com/docs/grafana/latest/alerting/configure-notifications/create-notification-policy/ | Alertmanager scope, mute non-inheritance, timing, and `alertingMultiplePolicies` public preview |
| Alerting best practices | https://grafana.com/docs/grafana/latest/alerting/best-practices/ | Symptoms, actionability, ownership, dimensions, grouping, flapping, continuous review |
| Alert file provisioning | https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/file-provisioning/ | Cloud limitation, editability, import conflict, policy-tree replacement, interpolation |
| Alert provisioning API | https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/http-api-provisioning/ | API/export schema difference, provenance, endpoint deprecations and replacements |
| Legacy HTTP API | https://grafana.com/docs/grafana/latest/developers/http_api/ | Legacy API inventory and Grafana 13 deprecation notice |
| API migration | https://grafana.com/docs/grafana/latest/developers/http_api/apis/ | `/apis` availability from Grafana 12, incomplete parity, legacy removal posture |
| Dashboard APIs | https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/ | Namespaces, resource schema, pagination, permissions, current Swagger warning |
| Service accounts | https://grafana.com/docs/grafana/latest/administration/service-accounts/ | API-key replacement, organization scope, tokens, expiration, permissions |
| Roles and permissions | https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/ | Server/org/folder boundaries, Viewer queries, Enterprise data-source permissions and RBAC |
| Security | https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/ | Data-source proxy restrictions, request security, anonymous access, arbitrary Viewer queries |
| Troubleshooting | https://grafana.com/docs/grafana/latest/troubleshooting/ | Log locations, debug logging, panel/transform/backend diagnosis |

## Canonical source and schemas

- Grafana source and releases: https://github.com/grafana/grafana
- New App Platform OpenAPI definitions: https://github.com/grafana/grafana/tree/main/packages/grafana-openapi/src/apis
- Grafana Terraform provider: https://github.com/grafana/terraform-provider-grafana
- Grafana Operator: https://github.com/grafana/grafana-operator
- Alert provisioning examples: https://github.com/grafana/provisioning-alerting-examples

Use release-pinned source or the target's Swagger for exact schemas. `main`, `latest`, and generated Swagger are live sources, not stable historical evidence.

## Live technical verification

Read-only checks on host `saru` on 2026-07-26 observed:

- Grafana `11.6.14+security-04`, commit `d88d482f3740c49ede664014fda4827a5fc2e9db`, in Docker Compose with Prometheus, Loki, and Promtail.
- `/api/health` returned `database: ok`; the container was running with zero restarts and no OOM kill, but had no Docker healthcheck.
- Grafana configuration, data, and logs were stored in named volumes. Dashboard JSON/provider files and a Loki data-source file existed under `/etc/grafana/provisioning`.
- Two dashboard providers, `magnus919` and `Traefik`, both polled `/etc/grafana/provisioning/dashboards` every 30 seconds with `disableDeletion: false`.
- Bounded logs repeatedly reported duplicate dashboard UIDs/titles and stated that both providers had no database write permissions because of duplicates.
- Protected legacy and new-style paths returned `401` without credentials. This proves the authentication boundary, not route compatibility or resource existence.

No files, services, tokens, Grafana resources, or external receivers were changed. No authenticated API inventory, data-source query, alert evaluation, notification delivery, or resolved notification was performed.

## Source evaluation

The retained product claims use Tier 1 official documentation, canonical source/schema repositories, release metadata, and direct read-only runtime evidence. Grafana Labs documentation is authoritative for supported behavior but is a vendor source and sometimes points to newer Swagger versions than its prose examples. The live target provides strong evidence for one Grafana 11 failure pattern, not a universal behavior claim.

Community posts, generic dashboard lists, and unsourced tutorials were excluded because primary documentation and runtime evidence covered the required scope. Existing repository PromQL examples were not reused because several require independent semantic validation.

## Refresh rules

Recheck sources and the target when any of these change:

- Grafana major/minor version, edition/license, Cloud stack generation, or deployment owner;
- `/api` or `/apis` route, API group/version, namespace, schema, pagination, provenance, or permission;
- dashboard classic/v2 schema, dynamic dashboards, Git Sync, `gcx`, Foundation SDK, or Operator support;
- alert-rule, recording-rule, receiver, policy, template, silence, or time-interval API/provisioning behavior;
- provisioning watch/poll, edit, delete, prune, version, interpolation, or hot-reload behavior;
- service-account, RBAC, data-source permission, anonymous/public sharing, plugin signature, or request-security behavior.

Always refresh destructive, access-control, secret, and production-routing instructions immediately before use.
