# Prometheus Operations

> **Last Updated:** 2026-08-03

Operational patterns for the Prometheus half of the telemetry stack: scrape
configuration, recording and alerting rules, relabeling, retention, and high
availability. Sources: Prometheus documentation (prometheus.io/docs,
accessed 2026-08-03) and the rule format reference in the Prometheus source
(reviewed 2026-08-03).

## Scrape configuration

One scrape job is one scrape group: a `job_name`, a `scrape_interval`, a
`scrape_timeout` strictly below the interval, a `metrics_path`, and a target
source. The default `metrics_path` is `/metrics`; TLS and auth go in
`scheme`, `tls_config`, and `basic_authorization`/`authorization`.

```yaml
scrape_configs:
  - job_name: node
    scrape_interval: 30s
    scrape_timeout: 10s
    metrics_path: /metrics
    static_configs:
      - targets: ["node1:9100", "node2:9100"]
```

Verify the live state, not the file: `/api/v1/status/config` returns the
effective config and `/api/v1/targets?state=active` returns per-target scrape
state. A target that never appears in the target list is usually a relabeling
or discovery problem, not a Prometheus outage.

## Recording and alerting rules

Rules files are `groups`, each with a `name`, an optional `interval`, and a
`rules` list. Every rule has exactly one of `record` or `alert` plus an
`expr`; alerting rules may add `for`, `keep_firing_for`, `labels`, and
`annotations`. Group names must be unique within a file; label and annotation
names must be valid label names; label values must be strings.

```yaml
groups:
  - name: api-slo
    interval: 1m
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total{job="api"}[5m]))
      - alert: ApiHighErrorRate
        expr: job:http_errors:rate5m / job:http_requests:rate5m > 0.05
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "API error rate above 5%"
```

Rules that touch the same series belong in one group because groups evaluate
sequentially; cross-group timing is undefined. Validate with
`promtool check rules` (full PromQL parsing) and `telemetry-check --rules`
(structural sanity, no external tools) before every reload, then
`promtool reload` via `POST /-/reload` and confirm with
`/api/v1/rules?type=alert`.

Recording rules are caching, not aggregation religion: name them with the
conventional `level:metric:operation` style, keep them idempotent, and prefer
`sum`/`rate` over `count`-style ratios that need division in every query.
Alerting rules should be small and reviewable; a rule whose expression needs
a comment to explain is a candidate for a recording rule instead.

## Relabeling

`relabel_configs` run at target discovery time (before scraping) and
`metric_relabel_configs` run after scraping (per metric). Use them to:

- enforce label naming and drop forbidden labels (`__meta_*`, `job`);
- add scrape metadata (`__address__`, `__scheme__`, `__metrics_path__`);
- drop high-cardinality labels from `metric_relabel_configs` before the TSDB.

Relabeling is the classic silent-breakage point: a dropped or renamed label
changes series identity without an error. Verify with the target's effective
labels in `/api/v1/targets` and a spot-check of `/metrics` on the endpoint.
`keep`/`drop`/`replace`/`labelmap` are the operators you will actually use;
`regex` capture groups feed `replacement` with `$1`-style references.

## Retention

Local retention is `--storage.tsdb.retention.time` (age) and
`--storage.tsdb.retention.size` (bytes); blocks are ~2h and compaction merges
them. Set retention as a deliberate capacity decision (see
`references/04-stack-integration-and-retention.md`), never leave the defaults
for a long-running server. Watch `prometheus_tsdb_head_series` (cardinality),
`prometheus_tsdb_compactions_total` and `prometheus_tsdb_blocks_loaded` for
compaction health, and `prometheus_tsdb_storage_blocks_bytes` for the
footprint. Retention is enforced lazily by compaction — a server under
compaction pressure can exceed its retention window temporarily.

## High availability (HA)

HA for Prometheus means two identical instances scraping the same targets,
with the same rules, and consistent external labels, so a query layer can
deduplicate or shard. The instances do not share state: each has its own TSDB,
its own `for`-counter state, and its own alert evaluation. Practical rules:

- run both replicas with `--web.external-url` stable and identical rule files;
- give replicas distinct `replica` external labels so dedup can pick one;
- never add alert-specific noise that makes the two replicas fire different
  alert instances — dedup is by label sets;
- consider Thanos or Mimir for query federation and long-term retention, but
  only after the two-replica story is correct.

Rule evaluation correctness across replicas matters more than uptime: a
failover that changes when alerts fire is worse than a brief scrape gap.
