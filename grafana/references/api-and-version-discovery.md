# API and Version Discovery

Read this before selecting an API, schema, or command. Grafana product, edition, and API surfaces evolve independently.

## Establish the target

Record:

1. Exact version and commit from `/api/health`, the server binary, package, image, or Cloud stack metadata.
2. OSS, Enterprise, or Cloud. Do not infer Enterprise capabilities from an Enterprise image name alone; verify licensed behavior where relevant.
3. Deployment owner: package, Docker/Compose, Helm, Operator, or Cloud.
4. Organization and folder context. Service accounts are organization-scoped; server administration is a different authority.
5. Authentication: interactive user, service account, identity provider, auth proxy, or Cloud access policy. Grafana API service accounts are not telemetry-ingestion credentials.
6. Existing resource provenance and the authorized read/write scope.

## API generations

- Grafana 12 introduced versioned Kubernetes-style APIs under `/apis`.
- Starting with Grafana 13, legacy `/api` routes are deprecated but remain operational for now.
- Migration is incomplete. Some legacy resources have no exact `/apis` equivalent, and some APIs have distinct versions or maturity levels.
- Dashboard APIs under `/apis/dashboard.grafana.app/...` require Grafana 12 or later. Consult the target's current Swagger because documentation examples may lag the newest API version.
- Alerting migration is resource-specific. Rules, recording rules, receivers, policy resources, templates, and time intervals can have different App Platform groups and versions.

Do not convert paths mechanically. For each operation, confirm the target version, documented endpoint, method, schema, namespace, concurrency/version field, required permissions, and response format.

## Read-only API procedure

1. Call `/api/health` without credentials only to establish reachable server/database metadata. It is not a provisioning or data-source test.
2. Use a least-privilege service account for organization-scoped reads. Prefer short-lived tokens and protected environment injection.
3. Query one bounded collection or UID at a time. Honor pagination and continuation tokens.
4. Record status, selected non-secret fields, and request scope. Do not retain full responses when they contain queries, annotations, receiver settings, user details, or secure metadata.
5. A `401` proves authentication was required, not whether the route exists. A `403` proves the authenticated identity lacked permission, not that the resource is absent.
6. A `404` can mean an absent object, unsupported route, wrong namespace, wrong organization, or proxy rewriting. Reconcile with version and server logs before concluding.

## Authorization scopes

Treat these separately:

| Scope | Typical resources |
|---|---|
| Server administration | global users, organizations, settings, licensing |
| Organization administration | data sources, teams, service accounts, plugins, organization settings |
| Folder/dashboard | folders, dashboards, library panels, annotations, permissions |
| Alerting | rules, groups, receivers/contact points, policies, templates, silences, mute timings |
| Data-source query | arbitrary queries allowed by the data source and Grafana permission model |

Grafana server administrator and organization administrator are distinct. In Grafana Cloud there is no server administrator role. Enterprise and Cloud add resource-level RBAC and data-source permissions not universally available in OSS.

## Safe authentication

- Prefer service accounts over legacy API keys for Grafana HTTP APIs.
- Start service accounts at the `None` basic role only where the target supports granting the required granular RBAC actions, such as Enterprise or Cloud. On OSS, choose the least-privileged basic role that can perform the task and constrain folders, organizations, data sources, and backend credentials separately.
- Use separate service accounts per organization and automation owner.
- Give tokens short expirations, rotate them independently, and never place them in URLs, shell traces, examples, or evidence artifacts.
- Do not request decrypted contact-point or data-source secrets for ordinary discovery.

## Discovery output

Report version/edition, deployment owner, organization/folder or namespace, API generation selected per resource, credential type and redacted scope, pagination boundary, observed status, and unresolved ambiguity. Do not report an API as compatible until a representative authorized read succeeds against that target.
