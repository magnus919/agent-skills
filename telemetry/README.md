# Telemetry — Operational Skill for the Prometheus + OpenTelemetry + Loki Stack

Operate the observability stack that deploys as one unit: Prometheus scrape configuration, recording and alerting rules, relabeling, retention, and high availability; OpenTelemetry Collector pipelines (receivers, processors, exporters, sampling, trace/span correlation); and Loki ingest, LogQL, retention, and label design.

## Why Install This Skill

Your agent can run the collection/ingest/retention layer of observability instead of guessing: review and fix Prometheus scrape configs, author and sanity-check recording and alerting rules, design OpenTelemetry Collector pipelines with deliberate sampling, tune Loki ingest and retention, and diagnose the classic failure modes — missing series, silent ingest loss, and exploding label cardinality — in a fixed evidence order. It can also construct bounded PromQL and LogQL investigations, separate syntax from semantic validation, and explain empty or partial results without turning missing data into zero.

It ships a read-only checker (`telemetry-check`) that parses Prometheus rules files with a bundled stdlib YAML reader and runs sanity checks mirroring `promtool check rules`, then probes scrape-target reachability with TCP connects. It cannot mutate anything: no config writes, no reloads, no data sent anywhere. That makes it safe for an agent to run during discovery.

The references are distilled from the official Prometheus, OpenTelemetry Collector, and Loki documentation with dated sources and verification-first guidance. Observability strategy deliberately routes to `platform-engineering` and dashboards/alerting to `grafana`; this skill owns the layer those two skills query.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop, mutation gates, and verification boundaries |
| `references/` | Six dated references: source index, Prometheus operations, OpenTelemetry Collector, Loki operations, bounded PromQL/LogQL query workflows, stack integration and retention |
| `scripts/telemetry-check` | Read-only rule sanity + scrape-target reachability checker: stdlib-only Python, `--json`, `--rules`/`--scrape`/`--targets`, `--help` with no server |
| `fixtures/` | Valid `prometheus-rules.yml` and `scrape-config.yml` used by the tests and as starting points |
| `tests/` | Deterministic tests against the fixture configs, including the read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no Prometheus server installed
telemetry/scripts/telemetry-check --help

# Sanity-check a Prometheus rules file, machine-readable
telemetry/scripts/telemetry-check --rules telemetry/fixtures/prometheus-rules.yml --json

# Probe the static targets of a scrape config
telemetry/scripts/telemetry-check --scrape telemetry/fixtures/scrape-config.yml --json

# Probe a plain host:port list with a per-target timeout
telemetry/scripts/telemetry-check --targets targets.txt --timeout 5
```

Exit codes: 0 all checks passed, 1 issues found or a fatal error, 2 usage error. The rule checks mirror `promtool check rules` for structure (exactly one of `record`/`alert`, non-empty `expr` with balanced delimiters, valid durations, valid names and label values); use `promtool check rules` when you need full PromQL parsing.

## Triggers

Load this skill for `prometheus`, `otel`/`opentelemetry`, `loki`, or general telemetry/observability operations: scrape config and `prometheus.yml` review, recording and alerting rule authoring or debugging, `relabel_configs` problems, TSDB retention and compaction, Prometheus HA pairs, OpenTelemetry Collector pipeline design or troubleshooting (receivers, processors, exporters, sampling), trace/span correlation with logs and metrics, Loki ingest health, LogQL query cost, Loki retention and compactor, and label cardinality. Do not load it for observability strategy or SLOs (that is `platform-engineering`), Grafana dashboards or Grafana-side alerting (that is `grafana`), application instrumentation code (that is `backend-engineering`), or deploying the stack itself on Kubernetes/Docker (that is `kubernetes`/`docker-compose`).

## Requirements

- Python 3.9+ for the `telemetry-check` script (`--help` and rule/scrape parsing need nothing else).
- Network access to scrape targets for `--scrape`/`--targets` reachability probes; rule checks are purely local.
- For live verification beyond the checker: access to the Prometheus `/api/v1/*` endpoints and the OTel Collector and Loki health endpoints, and `promtool` if you want full PromQL rule validation.
