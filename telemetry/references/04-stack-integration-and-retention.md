# Stack Integration and Retention

> **Last Updated:** 2026-08-03

How the three components of the telemetry stack fit together, and how to make
retention decisions across them instead of per-component by accident. Sources:
Prometheus storage documentation, OpenTelemetry Collector documentation, and
Loki retention documentation (all accessed 2026-08-03).

## The stack as one unit

The components share a data flow — instrumented services emit metrics, logs,
and traces; the OpenTelemetry Collector (or direct exporters) delivers them;
Prometheus stores metrics and evaluates rules; Loki stores logs; Grafana
queries both and displays the result. The stack is operated as one unit
because a change in any layer changes the behavior of every layer above it:

| Layer | Component | Owns |
|---|---|---|
| Collection | OTel Collector receivers, Prometheus scrape jobs | What data enters the stack |
| Processing | Collector processors (batch, sample, resource) | What the data looks like when stored |
| Storage | Prometheus TSDB, Loki chunks/index | How long data lives and how fast queries are |
| Evaluation | Prometheus rules | What the data means (alerts, recording rules) |
| Presentation | Grafana | What humans see (dashboards, Grafana-side alerting) |

Operational decisions therefore cross component boundaries: a label added in
relabeling is a label PromQL sees; a `trace_id` carried by the collector is a
LogQL matcher; a retention window chosen for Prometheus is a gap in history a
dashboards-as-code change cannot recover.

## Retention as a stack decision

Each component has independent retention, and the combined footprint is what
the team pays for:

| Component | Setting | Applies to | Default behavior |
|---|---|---|---|
| Prometheus | `--storage.tsdb.retention.time` / `.size` | Raw samples (blocks) | 15 days; lazily enforced by compaction |
| OTel Collector | exporter queue + `memory_limiter` | In-flight data | Queue backs up then drops oldest on pressure |
| Loki | `retention_enabled`, `retention_period`, `retention_size` (per tenant) | Indexed log streams | No retention unless enabled; compactor enforces it |

Decide per component by the question the data answers:

- hot metrics for alerting: keep enough history to evaluate every rule window
  plus headroom (a `for: 10m` rule needs at least that much history);
- samples for trends: retention length is a capacity trade-off, not a
  correctness requirement — long histories belong in a separate store
  (Thanos/Mimir) with its own owner;
- logs for debugging and audit: retention is a compliance decision with an
  owner; short retention on logs destroys the only evidence an incident
  post-mortem can use.

The failure mode is defaulting every component and discovering the cost when
storage is the incident. Write the decision down: `retention_period`,
retention flags, and the RPO/RTO framing belong in the deployment config and
its review checklist, not in tribal memory.

## Cross-component consistency checks

- Scrape config and collector receivers must agree on the metrics endpoint:
  a `metric_relabel_configs` drop on Prometheus side does not stop the
  collector from exporting the metric elsewhere.
- Rule expressions and recording rules must not depend on labels the scrape
  config does not produce — validate with `telemetry-check --rules` plus a
  live query, not by reading the config.
- LogQL matchers must match labels the `loki` exporter actually attaches —
  a matcher on `app` fails silently when the collector maps it to
  `service.name` only.
- Trace correlation needs `trace_id`/`span_id` in both the OTLP log records
  and the metrics exemplars; verify one pivot query end-to-end after any
  collector pipeline change.

## Alerting on the stack itself

The stack needs its own health rules (in a file you also validate with
`telemetry-check --rules`):

- `up{job=~"prometheus|otel-collector|loki"}` == 0 for component loss;
- `prometheus_tsdb_head_series` growth vs a budget for cardinality;
- `rate(loki_distributor_lines_received_total[5m])` vs a floor to catch
  silent ingest loss;
- `otelcol_exporter_send_failed_ratio` above a threshold for delivery loss;
- retention drift: `prometheus_tsdb_storage_blocks_bytes` and compactor
  delete counters vs the decided policy.

These rules live in this skill's scope (the Prometheus rules file); the
dashboards and Grafana-side alert routes for them are `grafana` territory.

## Routing

- Observability strategy — what to instrument, SLI/SLO design, error budgets —
  is [platform-engineering](../platform-engineering/SKILL.md).
- Dashboards, panels, Grafana alert rules, contact points, and notification
  policies are [grafana](../grafana/SKILL.md).
- This skill owns the collection/ingest/retention layer and the Prometheus
  rules files those layers consume. When a task crosses into those skills,
  route there instead of duplicating their content.
