# Troubleshooting Grafana

Separate evidence from inference. Diagnose in layers and change configuration only after identifying the failing plane.

## Baseline evidence

Collect a bounded record:

- exact version/edition/commit and deployment owner;
- target URL, organization/folder, auth method, and permission scope;
- process/container state, restart/OOM state, listener, and `/api/health`;
- effective non-secret configuration paths and provisioning ownership;
- bounded server logs covering the failure window;
- browser/network response or API status with secrets removed;
- data-source query evidence and timestamps;
- resource UID/provenance and last known change.

Do not dump complete environment variables, configuration, logs, dashboard JSON, Terraform state, or API responses into evidence.

## Blank or misleading panel

1. Confirm dashboard UID/version, panel, time range, time zone, refresh, and variables.
2. Inspect query response and error in Query Inspector or Explore.
3. Run the smallest equivalent query against the same data source.
4. Check data-source UID, permission, authentication, TLS, proxy/network reachability, and source retention.
5. Inspect labels, aggregation, interval/step, transformations in order, field overrides, null handling, and hidden series.
6. Compare with a known time containing data and test no-data behavior.

Do not "fix" a blank panel by widening time range, replacing nulls, or changing transformations until source absence and query semantics are distinguished.

## Data-source authentication or query failure

1. Identify data-source type/plugin version, access mode, URL class, and credential owner without revealing secure fields.
2. Use the Grafana data-source health check, then a representative bounded query.
3. Compare Grafana-to-source network/DNS/TLS behavior with the source's own health and auth logs.
4. Check least-privilege grants, token expiry, certificate chain/server name, proxy whitelist/request security, and time skew.
5. Separate Grafana permission to query from backend permission to read the requested data.

Route backend repair to the relevant data-source skill.

## Provisioning failure or drift

1. Enumerate providers/controllers, paths, UIDs, folders, scan intervals, edit/delete flags, Terraform state addresses, and Git/Operator owners.
2. Search bounded logs for provisioning errors, duplicate UIDs/titles, parse failures, permissions, and reconciliation outcomes.
3. Compare source hashes/revisions with the running object and database/API metadata.
4. Detect overlapping provider paths and multiple writers before editing any dashboard.
5. Review source removal, `prune`, delete lists, and policy-tree replacement risk.

### Known live failure pattern

On a Grafana 11.6.14 Compose target observed on 2026-07-26, `/api/health` reported `database: ok` while two dashboard providers scanned the same directory. Every observed poll in the bounded log window produced duplicate UID/title warnings, and Grafana reported that both providers lacked database write permission because of the duplicates. The safe diagnosis is overlapping ownership, not a failed database. Remediation must make provider scopes non-overlapping or select one owner, preserve files/UIDs, and verify warning cessation across more than one poll. This observation is a failure pattern, not a universal version-specific bug.

## Alert rule not evaluating

1. Confirm rule type/provenance, enabled/paused state, group interval, scheduler state, and organization/folder.
2. Run query/expression components over the rule's relative time range.
3. Check data-source auth and support for server-side alert queries.
4. Inspect no-data/error state and evaluation logs.
5. Check rule-instance cardinality and label conflicts.

## Firing alert does not notify

1. Capture actual firing labels and state transition time.
2. Trace the complete policy path, inherited receiver/timing, continue behavior, grouping, silences, and mute timings.
3. Check contact-point configuration with secrets redacted.
4. Account for group wait/interval and repeat timing before calling delivery late.
5. Use a controlled test receiver if authorized; inspect Grafana and receiver-side evidence.
6. Verify resolved delivery separately.

## Reverse proxy, subpath, or authentication failure

1. Test Grafana directly on its internal listener and through the proxy boundary.
2. Compare scheme, host, domain, `root_url`, subpath settings, forwarded headers, cookies, WebSocket routes, and identity headers.
3. Check redirect chains, callback URLs, SameSite/Secure cookie behavior, proxy timeouts, and body/header limits.
4. Verify the proxy does not expose administrative or internal data-source endpoints unintentionally.
5. Route TLS, middleware, and proxy configuration changes to the proxy skill.

## Plugin and migration failures

- Record Grafana and plugin versions, signature status, architecture, installation owner, and startup logs.
- Disable or remove a plugin only with explicit approval and a dashboard/data-source impact review.
- Before upgrades, verify database backup/restore, plugin compatibility, schema migration logs, storage headroom, and rollback support.
- Do not downgrade across database migrations or edit migration tables without a documented, explicitly authorized recovery path.

## Stop conditions

Stop before mutation when the target, owner, credential scope, production impact, or rollback is unknown. After two materially different diagnostic paths fail, report the evidence and access needed instead of trying unbounded configuration changes.

Report diagnosis as: observed evidence, supported inference, competing explanations, safe next test, mutation/approval boundary, and unverified delivery boundary.
