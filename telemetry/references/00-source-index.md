# Telemetry Operations — Source Index

> **Last Updated:** 2026-08-03

This index tracks the authoritative sources behind the telemetry skill
(Prometheus + OpenTelemetry Collector + Loki as one stack) and the refresh
procedure for keeping it current.

## Canonical sources

| Component | Source |
|---|---|
| Prometheus documentation (current) | https://prometheus.io/docs/introduction/overview/ |
| Prometheus configuration (scrape config, relabeling) | https://prometheus.io/docs/prometheus/latest/configuration/configuration/ |
| Prometheus recording rules | https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/ |
| Prometheus alerting rules | https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/ |
| Prometheus storage and retention | https://prometheus.io/docs/prometheus/latest/storage/ |
| `promtool` rule checking | https://prometheus.io/docs/prometheus/latest/command-line/promtool/ |
| Prometheus rule format reference (rulefmt) | https://github.com/prometheus/prometheus/blob/main/model/rulefmt/rulefmt.go |
| OpenTelemetry Collector | https://opentelemetry.io/docs/collector/ |
| Collector components (receivers/processors/exporters) | https://opentelemetry.io/docs/collector/configuration/ |
| Collector sampling | https://opentelemetry.io/docs/collector/sampling/ |
| OpenTelemetry traces and spans | https://opentelemetry.io/docs/concepts/signals/traces/ |
| Loki documentation (current) | https://grafana.com/docs/loki/latest/ |
| Loki storage and retention | https://grafana.com/docs/loki/latest/operations/storage/retention/ |
| LogQL | https://grafana.com/docs/loki/latest/query/ |
| Loki label design guidance | https://grafana.com/docs/loki/latest/get-started/labels/ |
| Prometheus HTTP API and querying | https://prometheus.io/docs/prometheus/latest/querying/api/ |
| PromQL operators and functions | https://prometheus.io/docs/prometheus/latest/querying/operators/ |
| Loki query HTTP API | https://grafana.com/docs/loki/latest/reference/loki-http-api/ |

## Version observations (as of this refresh)

- Prometheus 3.x defaults to UTF-8 metric-name validation; the legacy metric
  name pattern `[a-zA-Z_:][a-zA-Z0-9_:]*` remains the documented pattern for
  recording rule names and is what `promtool` enforces under legacy validation.
- `promtool check rules` validates rule files structurally and parses every
  expression with the full PromQL parser; `telemetry-check` deliberately
  covers the structural subset so it can run with no Prometheus tooling.
- The OpenTelemetry Collector's `memory_limiter` processor is recommended
  before every exporter; `tail_sampling` and `probabilistic_sampler` are the
  two supported sampler processors for traces.
- Loki retention is enforced by the compactor on a per-tenant basis;
  `retention_period` and `retention_size` are per-tenant limits, and
  `retention_enabled` must be `true` for period-based retention.
- OTLP is the current stable protocol; the Collector can also receive/export
  Prometheus exposition format, and its Loki exporter translates structured
  log records into LogQL-compatible streams.

## Refresh procedure

1. Re-check the sources above for new minor or major releases.
2. Update the version observations that changed (defaults, renamed components,
   new processors, changed retention semantics).
3. Re-run the bundled checker against a rules fixture and a scrape config and
   confirm every check still parses: `telemetry/scripts/telemetry-check
   --rules telemetry/fixtures/prometheus-rules.yml --json`.
4. Re-verify the SKILL.md keyword sweep from the validation contract and the
   routing links to `platform-engineering` and `grafana`.

## Related skill sources

- `platform-engineering` owns observability strategy (SLIs, SLOs, what to
  instrument) and its observability reference treats Prometheus, OTel, and
  Loki as one stack; this skill owns operating that stack.
- `grafana` owns dashboards, panels, and Grafana-side alerting; it queries
  Prometheus (PromQL) and Loki (LogQL) but does not operate the backends.
- `traefik` ships Prometheus and OTel configuration for the edge; its
  observability reference documents the metric names this stack ingests.
