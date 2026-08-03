# OpenTelemetry Collector Operations

> **Last Updated:** 2026-08-03

Operational patterns for the OpenTelemetry Collector in the telemetry stack:
pipeline design, receivers/processors/exporters, sampling, and trace/span
correlation. Sources: OpenTelemetry Collector documentation
(opentelemetry.io/docs/collector, accessed 2026-08-03).

## Pipeline design

A pipeline is a named, directed acyclic chain per signal type (metrics, logs,
traces): one or more `receivers`, zero or more `processors`, one or more
`exporters`. Signals flow through every processor in order, so pipeline length
is a cost and a debugging surface.

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, tail_sampling]
      exporters: [otlp/backend]
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki]
```

Design rules:

- keep pipelines per signal — a pipeline that mixes traces and logs becomes
  un-debuggable and couples sampling decisions;
- run one `memory_limiter` processor before every exporter to bound memory
  (`ballast_size_mib` is deprecated; size `check_interval`/`limit_mib` against
  the container limit);
- `batch` after sampling and before exporting amortizes exporter cost;
- an unused receiver or exporter is dead configuration — remove it.

## Receivers, processors, exporters

| Role | Examples | Notes |
|---|---|---|
| Receiver | `otlp` (default port 4317 gRPC / 4318 HTTP), `prometheus`, `filelog`, `hostmetrics` | Receivers own the ingest surface; auth and TLS live here |
| Processor | `memory_limiter`, `batch`, `tail_sampling`, `probabilistic_sampler`, `resource`, `attributes`, `filter`, `transform`, `spanmetrics` | Order matters: sampling before batch changes semantics; `resource` should run early |
| Exporter | `otlp`, `prometheusremotewrite`, `loki`, `logging`/`debug`, `kafka` | Exporters own delivery and retry; failing exporters backpressure the pipeline |

The `logging`/`debug` exporter is the troubleshooting tool: attach it to a
pipeline temporarily to see what actually leaves the collector, then remove
it. Never ship a debug exporter in production config.

## Sampling

Two trace samplers ship with the collector:

- `probabilistic_sampler` — stateless, per-span hash of the trace ID, cheap,
  no cross-span state. Good for high-volume, low-value traffic.
- `tail_sampling` — buffers spans per trace and decides at the batch level,
  so policies can depend on span attributes (status, error, duration). Stateful
  and memory-hungry; belongs on a trace pipeline after `batch`.

Sample with the alerting and debugging goal in mind: keep every error and slow
path (via `tail_sampling` policy on `status.code`, `http.status_code`,
duration), sample the long tail of success traffic, and record the sampling
decision (`sampler.type`/`sampling.score`) as a span attribute so downstream
queries can scale results. Metrics and logs are not sampled by these processors
— do not apply trace samplers to other signal pipelines.

## Trace/span correlation

Correlation is the payoff of the stack: a trace ID in a log line or an
exemplar lets any query pivot from "this happened" to "here is the full
request". The collector supports this by:

- carrying `trace_id`/`span_id` through OTLP log records — the `loki` exporter
  maps them to `trace_id`/`span_id` structured metadata for LogQL matching;
- the `spanmetrics` processor deriving RED (rate/errors/duration) metrics from
  spans, with `trace_id` exemplars on the histogram so PromQL can jump to a
  trace;
- resource attributes (`service.name`, `deployment.environment`) flowing
  through to every signal so logs, metrics, and traces share the join keys.

Correlation is only as good as propagation: if the application does not
propagate context, the collector cannot invent it. Missing trace context in
logs usually means the SDK side is not wired — that is application-level work
for [backend-engineering](../backend-engineering/SKILL.md); the collector side
of the join is this skill.
