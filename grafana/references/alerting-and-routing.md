# Alerting and Notification Routing

Treat Grafana Alerting as one end-to-end path. A syntactically valid rule or a firing instance does not prove that the intended responder receives or resolves a notification.

## Model the path

Trace:

```text
data-source query -> expressions -> condition -> rule evaluation
-> alert instances and labels -> direct contact point or policy tree
-> grouping and timing -> silence/mute evaluation -> receiver integration
-> firing delivery -> recovery -> resolved delivery
```

Record Grafana version/edition, organization, rule provenance, rule group and interval, data-source UID, labels, annotations, policy owner, contact point, and authorized test route.

## Rule design

- Define the user-visible symptom, owner, service scope, severity rationale, and required action before writing the rule.
- Prefer symptom-based paging. Route infrastructure or diagnostic signals to a lower-interruption channel unless policy says otherwise. Use `site-reliability-engineering` for page-worthiness and SLO/burn-rate design.
- Validate every query and expression with representative data. Confirm units, reduction, thresholds, evaluation range, delay, and data-source availability.
- Decide `noDataState`, execution-error state, pending period, and keep-firing/recovery behavior deliberately. Defaults are not a reliability policy.
- Multi-dimensional rules create one instance per retained label set. Keep only dimensions that change routing or action, and bound instance cardinality.
- Add concise summary/description, owner, severity, dashboard/panel link, and runbook link. Labels route and group; annotations explain.
- Review duplicate coverage, flapping risk, downstream cascades, and maintenance behavior before enabling.

## Routing semantics

Grafana uses one notification-policy tree by default. The public-preview `alertingMultiplePolicies` feature flag can enable multiple independently managed routing trees. Discover the feature-flag state, selected tree, and Alertmanager before tracing a route. For the exact firing labels, inspect:

1. root receiver and inherited grouping/timing;
2. child matcher order, deepest matching child, and whether matching continues to siblings;
3. contact point and integration settings, with secrets redacted;
4. group-by labels, group wait, group interval, and repeat interval;
5. active or mute intervals and their time zones;
6. silences and matchers;
7. default-route fallback and unmatched labels;
8. direct contact-point selection on rules, which creates internal routing outside the user-managed policy tree;
9. external receiver-side deduplication or escalation.

Routing descends recursively through matching children. By default, only the deepest matching child handles the instance and sibling evaluation stops after a match; enabling continuation allows subsequent siblings to handle it too. Contact point, grouping, and general timing can be inherited from parents, while mute timings must be configured at each applicable level.

Preserve existing routing and escalation unless the requested scope explicitly changes them. A policy-tree provisioning operation can replace that complete user-managed tree, but it does not replace internal policies created when rules directly select contact points. Diff every affected tree and direct-contact-point route, not only the desired branch.

## Silences and mute timings

- Silences are one-time matcher-based suppression; mute timings are recurring intervals.
- They pause notifications, not rule evaluation.
- Scope matchers narrowly and record owner, reason, start/end or recurrence, time zone, and expiry/review.
- Verify that unrelated alerts still route. Never use a broad silence as a substitute for fixing a noisy rule.

## Safe testing

Sending a notification is an external mutation. Before testing, confirm receiver, audience, expected message volume, maintenance window, and cleanup.

Preferred sequence:

1. Inspect rule, query result, current instances, labels, and policy tree without delivery.
2. Use a designated test rule/contact point or non-paging receiver.
3. Exercise normal to pending to firing behavior with a controlled signal where supported.
4. Confirm the effective route and grouped firing notification.
5. Remove the condition and confirm recovery plus resolved notification when enabled.
6. Check duplicate notifications, timing, templates, links, and secret redaction.
7. Restore the test signal and remove temporary test resources through their owner.

If production injection or receiver delivery is not authorized, stop at route simulation/inspection and report the gap.

## Provisioning and API cautions

- File-provisioned alerting resources are not editable in the UI and are unavailable in Grafana Cloud.
- Importing an existing alerting resource can conflict; reconcile ownership before import.
- API object formats and export/file-provisioning formats differ. Export JSON is not necessarily valid as an API update body.
- Provenance controls editability. Do not disable provenance merely to bypass the source-of-truth model.
- Legacy alert provisioning endpoints and App Platform APIs have resource-specific deprecation and maturity. Read current schemas for the target version.
- Contact points, policies, templates, and mute timings can expose secrets. Do not request decryption for routine export or evidence.

## Diagnosis

| Symptom | Evidence chain |
|---|---|
| Rule never evaluates | scheduler/rule-group state -> pause state -> query execution -> data-source auth -> expression/condition |
| Rule stays Normal | raw data -> time range -> reduction -> threshold -> pending period -> label instances |
| Rule is Error/No Data | query inspector/evaluation error -> source availability -> no-data/error policy |
| Firing but no notification | actual labels -> policy path -> silence/mute -> grouping timers -> contact point test -> receiver logs |
| Wrong team notified | matcher set/order -> inherited receiver -> continue behavior -> default route -> external escalation |
| Firing repeats/noise | instance cardinality -> flapping -> group labels/timers -> repeat interval -> duplicate rules/routes |
| No resolved message | recovery state -> keep-firing behavior -> disable-resolve setting -> grouping -> receiver delivery |

## Completion

Report separately whether query semantics, rule state transitions, policy matching, firing delivery, and resolved delivery were verified. Never collapse them into one "alert works" claim.
