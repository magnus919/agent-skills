# Loki Operations

> **Last Updated:** 2026-08-03

Operational patterns for the Loki half of the telemetry stack: ingest, LogQL,
retention, and label design. Sources: Grafana Loki documentation
(grafana.com/docs/loki, accessed 2026-08-03).

## Ingest

Loki ingests via the push API (`POST /loki/api/v1/push`) from Promtail, the
OpenTelemetry Collector `loki` exporter, Grafana Alloy/Agent, or the SDKs.
Ingest health is distributor-side:

- `loki_distributor_bytes_received_total` and
  `loki_distributor_lines_received_total` must advance per tenant;
- `loki_ingester_streams` shows active streams — a flat line here while
  producers push means a config or network problem;
- the ready endpoint (`/ready`) must return 200; `429 Too Many Requests` from
  the distributor means rate limits — the producer retries, but a sustained
  backlog is a capacity signal.

The OTel Collector `loki` exporter maps log records to streams: the
`loki.tenant` and `loki.format` attributes plus configured labels control
stream cardinality (see Labels below). Promtail is the file-tailer option;
choose one producer per source and document it.

## LogQL

LogQL has two layers: stream selectors and pipeline expressions.

- Selectors choose streams by label: `{app="api", env="prod"}`. Label
  matchers are evaluated against the inverted index — this is the cheap part,
  and it is why label design matters.
- Pipeline expressions filter and transform lines: `|= "error"`,
  `|~ "5[0-9][0-9]"`, `| json`, `| regexp "(?P<field>...)"`, `| line_format`.
  These run per line after selection — the expensive part.

Metric queries wrap the pipeline in `rate`, `count_over_time`, etc.:
`sum by (app) (rate({job="api"} |~ "error"[5m]))`. When a query is slow,
the cause is almost always a too-broad selector (too many streams) or
regexp/JSON parsing on every line; fix the selector or pre-extract fields at
ingest, not by writing a faster regexp.

## Retention

Loki retention is per-tenant, enforced by the compactor:

- `retention_enabled: true` in the limits config enables period-based
  retention; `retention_period` sets the age limit and `retention_size` the
  byte limit per tenant;
- the compactor deletes expired chunks and merges index shards; watch
  `loki_compactor_delete_requests_total` and
  `loki_compactor_compactor_running` to confirm it is actually running;
- retention applies at query and delete time, so expired data can still be
  counted until compaction finishes — size-based limits are the practical
  control for runaway log volume.

Set retention before rollout and treat it as a compliance decision with an
owner (see `references/04-stack-integration-and-retention.md`). A Loki with
default retention and no owner will silently grow until storage is the
incident.

## Labels

Loki labels are an inverted index — every distinct label value adds index
entries and stream overhead. The guidance is deliberately simple:

- keep labels to tenant, app, environment, job, and a handful of
  service-defined dimensions;
- never index high-cardinality fields: request IDs, user IDs, trace IDs,
  IPs, timestamps, or any field whose values change per log line;
- put high-cardinality data in the log line itself and extract it with LogQL
  `| json`/`| regexp`, or as OTel structured metadata, when you need it;
- a good rule of thumb: if a label's values exceed the low hundreds of
  distinct values, it is a line field, not a label.

Cardinality damage is silent and cumulative: `loki_ingester_streams`
climbing while label changes are "small" is the leading signal. Stream
sharding and `chunk_target_size` tune large-stream handling, but they do not
make a bad label design good.
