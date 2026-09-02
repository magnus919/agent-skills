---
name: telemetry
description: >-
  Operate the observability stack that deploys as one unit: Prometheus scrape
  configuration, recording and alerting rules, relabeling, retention, and high
  availability; OpenTelemetry Collector pipelines (receivers, processors,
  exporters, sampling, trace/span correlation); and Loki ingest, LogQL,
  retention, and label design — with a bundled read-only telemetry-check script
  for Prometheus rule sanity and scrape-target reachability. Use when running,
  tuning, or troubleshooting a Prometheus, OpenTelemetry Collector, or Loki
  deployment, or reviewing the collection/ingest/retention layer, including
  bounded PromQL and LogQL query construction, semantic review, and no-data
  diagnosis. Do not use for observability strategy, SLI/SLO design, or paging
  policy (that is platform-engineering), Grafana dashboards, panels, and
  Grafana-side alerting (that is grafana), or Tempo/tracing operations, which
  remain deferred to a future named-tool skill.
license: MIT
compatibility: >-
  The bundled telemetry-check script runs on Python 3.9+ and needs no
  Prometheus server for --help. Rule and scrape-config checks read local
  YAML/JSON files; scrape-target reachability probes use TCP connects only and
  require network access to the targets.
metadata:
  source: https://prometheus.io/docs/introduction/overview/
  source_index: references/00-source-index.md
  research_checked: "2026-08-03"
---

# Telemetry Operations

Use this skill to operate the **telemetry stack** — Prometheus, the OpenTelemetry Collector, and Loki — as the one deployment unit it ships as: collection and scraping, ingestion, retention, and the rules that turn raw signals into alerts. This is a **tool skill** for one stack of named tools. Observability *strategy* — SLIs, SLOs, error budgets, and what to instrument — belongs to [platform-engineering](../platform-engineering/SKILL.md); dashboards, panels, and Grafana-side alert rules, contact points, and notification policies belong to [grafana](../grafana/SKILL.md). This skill owns the collection/ingest/retention layer and the Prometheus rules files that both of those skills consume.

## Operating contract

1. **Read-only discovery before any mutation.** Inspect scrape configs, rules files, collector pipelines, and retention settings first. The bundled `telemetry-check` script runs rule sanity and scrape-target reachability checks without changing anything.
2. **Confirm the target, scope, and rollback path before acting.** Read-only discovery may proceed without confirmation. Mutations — a config reload, a `promtool` rules push, a collector restart, a retention-policy change — require an explicit human directive naming the instance.
3. **A config that parses is not a config that works.** Rule sanity catches structure; it does not prove the expression is meaningful or that the target is scrapable. Verify at the delivery boundary (scrape succeeded, rule evaluated, alert fired) before claiming health.
4. **Keep evidence bounded.** Summarize config diffs and query results; never dump full `prometheus.yml`, collector pipelines, or credentials into chat.
5. **Own the retention decision.** Retention is a capacity and compliance decision made deliberately per component — Prometheus block retention, OTel exporter buffering, Loki retention per tenant — and reviewed on a schedule, not left at defaults.

## The telemetry-check script

`scripts/telemetry-check` is an agent-first, read-only checker. It parses Prometheus rules files with a bundled stdlib YAML reader and runs sanity checks mirroring `promtool check rules`; it extracts static targets from scrape configs and probes TCP reachability; and it emits bounded JSON. It never writes files and never sends data anywhere.

```bash
scripts/telemetry-check --help                      # no server needed
scripts/telemetry-check --rules rules.yml --json    # rule sanity, machine-readable
scripts/telemetry-check --scrape prometheus.yml --json   # probe static targets
scripts/telemetry-check --targets targets.txt --timeout 5
```

Exit codes: 0 all checks passed, 1 issues found or a fatal error, 2 usage error. The rule checks mirror promtool: exactly one of `record`/`alert` per rule, a non-empty expression with balanced delimiters, valid durations, recording-rule and label names, and string-only label values. Use `promtool check rules` for full PromQL parsing.

## Operating loop

1. **Identify the deployment**: which components are in scope (Prometheus, OTel Collector, Loki), how they are deployed (binary, container, operator), where configs live, and who owns them.
2. **Collect evidence**: run `telemetry-check --rules` and `--scrape` on the configs, then check the live status endpoints (`/-/healthy`, `/api/v1/targets`, collector health, Loki ready) where access exists.
3. **For a query investigation**, load `references/05-query-workflows.md`. Define the signal, selector, UTC time window, step/limit, and expected unit; validate syntax separately from semantics; execute read-only instant then bounded range/log queries; and capture status, scope, time, limits, warnings, and cardinality evidence.
4. **Triage against the symptom**: map the reported problem to the evidence (missing series → scrape or relabeling; alert not firing → rule or retention; logs missing → ingest or label cardinality). Treat an empty result as unknown, never as numeric zero, and distinguish stale, partial, expired, absent-label, and query-error states.
5. **Act with confirmation**: bounded, scoped mutations after a human directive, with a rollback path named first.
6. **Verify**: re-run the relevant check and confirm the observable at the delivery boundary.

## Prometheus: scrape, rules, relabeling, retention, HA

- **Scrape config** (`scrape_configs`): one job per scrape group with a deliberate `scrape_interval`, `scrape_timeout` below it, and `metrics_path`. Prefer `static_configs` for known endpoints and service discovery (`*_sd_configs`) for dynamic ones. Verify the running config with `/api/v1/status/config` and targets with `/api/v1/targets?state=active`.
- **Recording and alerting rules**: rules files are `groups` of `record` or `alert` rules with a PromQL `expr`, optional `for`/`keep_firing_for` durations, and `labels`/`annotations`. Validate every change with `promtool check rules` and with the bundled `telemetry-check --rules` before reload. Rules must be small, well-named, and reviewable — a 100-line expression is a debugging liability, not a rule.
- **Relabeling**: `relabel_configs` and `metric_relabel_configs` rewrite labels before ingestion. Use them to enforce label naming, drop high-cardinality or internal labels, and attach scrape metadata. Relabeling mistakes silently change series identity — verify with a targeted `curl` of `/metrics` and the target's `scrapeUrl` in `/api/v1/targets`.
- **Retention**: `--storage.tsdb.retention.time` and `--storage.tsdb.retention.size` bound local block retention; blocks are 2h by default. Retention is a capacity decision (see `references/04-stack-integration-and-retention.md`), not a default to leave alone. Watch `prometheus_tsdb_head_series` and `prometheus_tsdb_compaction` for cardinality and compaction pressure.
- **High availability (HA)**: two identically configured Prometheus instances with `--query.max-concurrency` headroom and consistent external labels let you shard or deduplicate at the query layer (Thanos, Mimir, or Grafana data sources). Alerting rules must not double-fire: HA pairs need a dedup layer or consistent labeling, and rule evaluation must stay consistent across replicas. Rule evaluation state (`for` counters) is local to each instance.

## OpenTelemetry Collector: pipeline, sampling, correlation

- **Collector pipeline**: a pipeline is a directed acyclic chain of `receivers` → `processors` → `exporters` per signal type (metrics, logs, traces). Keep pipelines narrow and per-signal; a pipeline that mixes signals becomes un-debuggable. Each pipeline must have at least one exporter; unused receivers/exporters are dead configuration.
- **Receivers, processors, exporters**: receivers accept data (OTLP, Prometheus, filelog, hostmetrics); processors transform, batch, filter, sample, and attach resource attributes; exporters send data onward (OTLP, Prometheus remote write, Loki, logging). Order matters — batching and the `memory_limiter` processor belong before exporters; `tail_sampling` belongs on trace pipelines only.
- **Sampling**: `tail_sampling` on traces decides at the batch level; `probabilistic_sampler` is stateless and cheaper. Sample deliberately: full traces for errors and slow paths, tail sampling for high-volume success traffic, and never sample away the error signal. Sampling must be coordinated with retention — a sampled trace is gone forever, so the decision belongs in the pipeline design, not in an emergency.
- **Trace/span correlation**: carry `trace_id` and `span_id` in log lines and metric exemplars so LogQL and PromQL can pivot back to the trace. The collector's `spanmetrics` processor derives RED metrics from spans, and OTLP logs with trace context land in Loki with `trace_id` as a structured label for correlation. Trace context propagation is an application-level concern that [backend-engineering](../backend-engineering/SKILL.md) owns; the collector side is here.

## Loki: ingest, LogQL, retention, labels

- **Ingest**: Loki ingests over the push API (`/loki/api/v1/push`) from Promtail, the OTel Collector's `loki` exporter, or the Grafana Agent/Alloy. Verify ingest with `loki_distributor_bytes_received_total` and the ready endpoint; an ingest that silently drops (rate limits, `too many outstanding requests`) hides outages.
- **LogQL**: `{label="value"} |= "filter" | json` selects streams and filters lines; label matchers are the primary cost driver. LogQL analytics (`sum by (...) (rate({app="x"} |~ "error"[5m]))`) work on the label index plus line filtering — design labels so the matchers you actually use are cheap.
- **Retention**: `retention_period` and `retention_size` apply per tenant; the compactor enforces them and merges index shards. Log volume is unbounded if ungoverned — set retention before rollout, track it with `loki_compactor` metrics, and treat log retention as a compliance decision with an owner.
- **Labels**: Loki labels are inverted indexes — high-cardinality labels (request IDs, user IDs, trace IDs) explode index size and streaming cost. Keep labels to tenant, app, environment, and job; put high-cardinality fields in the log line and extract them with LogQL `| json`/`| regexp` or OTel structured metadata. Cardinality guidance: a label whose values change with every log line does not belong in the index.

## Retention across the stack

Retention is a stack-wide decision: Prometheus blocks (raw samples), OTel Collector buffering (in-memory queue, exporter retries), and Loki (indexed logs) each have independent retention, and the *combined* storage footprint is what the team pays for. Decide per component based on the question the data answers (hot metrics for alerting, samples for trends, logs for debugging and audit), set it in config, and review it on a schedule. See `references/04-stack-integration-and-retention.md` for the trade-off tables and the alerting rule that watches retention.

## Reference routing

| Load when | Reference |
|---|---|
| Sources, version observations, refresh procedure | `references/00-source-index.md` |
| Scrape config, recording/alerting rules, relabeling, retention, HA | `references/01-prometheus-operations.md` |
| Collector pipelines, receivers/processors/exporters, sampling, correlation | `references/02-opentelemetry-collector.md` |
| Ingest, LogQL, retention, label design | `references/03-loki-operations.md` |
| PromQL/LogQL construction, semantic review, bounded cost, and no-data diagnosis | `references/05-query-workflows.md` |
| Cross-component retention decisions and stack integration | `references/04-stack-integration-and-retention.md` |

## Included artifacts

- `scripts/telemetry-check`: read-only rule sanity + scrape-target reachability checker (stdlib-only, `--json`, `--rules`/`--scrape`/`--targets`, `--help` without a server).
- `tests/test_telemetry_check.py`: deterministic tests against fixture configs, including the read-only contract.
- `fixtures/`: `prometheus-rules.yml` (valid rules) and `scrape-config.yml` (valid scrape config) used by the tests and as starting points.
- `references/`: five dated, source-indexed references plus the source index, including the bounded PromQL/LogQL workflow.
- `evals/evals.json`: six output-quality evaluation cases for agent runs.

## Verification boundary

| Claim | Minimum evidence |
|---|---|
| A rules file is structurally sound | `telemetry-check --rules FILE --json` exits 0 with no errors |
| A rules file is semantically valid | `promtool check rules FILE` exits 0 |
| A target is scrapable | `telemetry-check --scrape CONFIG --json` reports it reachable, and `/api/v1/targets` shows `state="up"` |
| A pipeline is live | Collector health endpoint responds and per-signal metrics (`otelcol_receiver_*`, `otelcol_exporter_*`) advance |
| Ingest is healthy | Distributor metrics advance and the ready endpoint returns 200 |
| Retention is governed | `retention_period`/`retention_size` are set explicitly, and compactor/TSDB metrics confirm the policy |

## Hard boundaries

- Never mutate a scrape config, rules file, collector pipeline, or retention policy without an explicit human directive naming the target and a stated rollback path. Read-only discovery may proceed freely.
- Never claim a rule or target works without delivery-boundary evidence: a scrape that succeeded, a rule that evaluated, an alert that fired.
- Never expose full configs, credentials, or raw logs in chat; summarize evidence instead.
- Never run `telemetry-check` as anything but what it is — read-only. It has no mutation surface.
- Dashboards, Grafana alert rules, contact points, and notification policies are [grafana](../grafana/SKILL.md) territory; SLI/SLO design and observability strategy are [platform-engineering](../platform-engineering/SKILL.md) territory. Do not duplicate their content here.

## When not to use

- **Observability strategy and SLOs** (what to instrument, SLI/SLO design, error budgets, paging policy) — that is [platform-engineering](../platform-engineering/SKILL.md).
- **Grafana product work** (dashboards, panels, data sources, Grafana alert rules, contact points, notification policies, RBAC) — that is [grafana](../grafana/SKILL.md); it queries Prometheus and Loki but owns the Grafana side.
- **Application instrumentation code** (OTel SDKs in services, trace context propagation, custom exporters in application code) — that is application development; see [backend-engineering](../backend-engineering/SKILL.md).
- **Reverse proxy and edge observability** (Traefik metrics/tracing/access-log config) — that is [traefik](../traefik/SKILL.md), whose observability reference treats this stack as its backend.
- **Infrastructure deployment of the stack** (Helm charts, Kubernetes operators, Docker Compose for the stack itself) — that is [kubernetes](../kubernetes/SKILL.md) and [docker-compose](../docker-compose/SKILL.md).
- **Other backends** (Tempo, Mimir, Thanos, Datadog, InfluxDB) — those stay with their owners; this skill covers Prometheus, the OTel Collector, and Loki as a unit.
