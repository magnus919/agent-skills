# PromQL and LogQL Query Workflows

> **Last Updated:** 2026-09-01

Use this reference for an offline query review or a live, read-only query investigation. It covers query shape and evidence; it does not replace `promtool` or Loki's parser.

## 1. Define a bounded question

Write down the signal, service/job, environment, exact UTC start and end, resolution, and expected unit before writing the expression. Prefer a narrow selector with equality matchers:

```promql
sum by (job, route) (rate(http_requests_total{job="api", environment="prod"}[5m]))
```

For logs, select streams first and filter lines second:

```logql
{app="api", environment="prod"} |= "timeout" | json | duration_ms > 1000
```

Do not begin with `{}` or `metric{label=~".*"}`. Avoid unbounded regex, arbitrary joins, and multi-day ranges while exploring. A range query must state its step; choose a step no finer than the evidence needs. Bound concurrency and request timeouts at the client/query gateway.

## 2. Validate in two distinct passes

Syntax and semantics are different claims:

1. **Syntax:** parse the expression with `promtool check rules` (PromQL) or the target Loki/Grafana parser. Check balanced delimiters, operators, durations, and LogQL pipeline syntax. A HTTP 200 only proves the endpoint accepted the request, not that the question is correct.
2. **Semantics:** confirm metric/log names, label keys and value types, counter-versus-gauge intent, compatible label sets for binary operators, and aggregation dimensions. For joins, make the matching labels explicit (`on(...)`/`ignoring(...)`) and use `group_left`/`group_right` only when the cardinality relationship is known. For LogQL, verify parsed fields exist and that aggregation is applied to the intended streams.

Record both results separately. A syntactically valid query can return an empty vector because the label was renamed, the metric was never scraped, or retention has expired.

## 3. Capture bounded evidence

For every query record:

- backend and endpoint, HTTP status, and response `status`/error type;
- exact query text or a redacted query identifier;
- UTC `start`, `end`, and Prometheus `step` (or Loki limit/direction);
- selector and grouping labels, estimated series/stream count, and duration;
- whether the result is instant, range, logs, or a derived metric;
- parser result, semantic checks, warnings, and a link/request ID if available.

Use instant queries to test existence, then a short range query to establish behavior. Keep result samples bounded; do not paste raw logs or credentials.

## 4. Control cost and cardinality

Start with a narrow equality selector and a short range. Expand one dimension at a time, checking series count and latency after each change. Prefer recording rules for repeatedly used expensive PromQL expressions and pre-extracted low-cardinality Loki labels for common filters. Keep request limits explicit: maximum lookback, step floor, series/stream limit, bytes/line limit, timeout, and query concurrency. A gateway or tenant limit is a safety net, not permission to issue a broad query.

Avoid `count by` over unbounded labels, grouping by request/user/trace IDs, regex over all streams, JSON/regexp parsing before a selective matcher, and joins where both sides are high cardinality. A label whose value changes per event belongs in the log body or structured metadata, not Loki's index.

## 5. Diagnose empty and partial results without inventing zeros

An empty result is **unknown**, never numeric zero. Distinguish:

| Observation | Next read-only check | Interpretation |
|---|---|---|
| Query parser error / non-2xx | response error type and expression | Query error; fix syntax or request shape |
| Empty with healthy backend | instant existence query, label/series API, exact time window | Could be absent label, wrong selector, or no events |
| Empty only for old time | retention bounds and backend clock | Data expired or outside retention |
| Empty for one target | scrape/ingest target state and relabel output | Failed target, dropped series, or missing stream |
| Stale/flat value | sample timestamps, scrape freshness, exporter metrics | Stale data, stalled producer, or timestamp issue |
| Partial response/warnings | HTTP status, response warnings, shard/limit metrics | Incomplete evidence; do not aggregate as complete |
| Backend timeout/limit | query duration, series/stream limit, concurrency | Cost or capacity rejection; narrow query |

For ratios, do not substitute zero for a missing numerator or denominator. Report `no data`, preserve `NaN`/absence semantics, and state what evidence is missing. A target can be `up` while a particular metric is absent because relabeling or instrumentation changed.

## Ownership and deferral

Route SLI/SLO definitions, error budgets, alert thresholds, and paging strategy to [platform-engineering](../../platform-engineering/SKILL.md). Route Grafana panels, data-source configuration, Grafana alert rules, contact points, and notification policies to [grafana](../../grafana/SKILL.md). This skill supplies backend query evidence those owners consume.

Tempo/tracing query workflows are intentionally deferred to a future named-tool decision. This skill may preserve trace/span IDs for correlation in logs and metrics, but it does not claim Tempo commands, APIs, or trace-query semantics. Route application propagation to [backend-engineering](../../backend-engineering/SKILL.md) and revisit a dedicated Tempo skill only when a concrete operational surface and non-overlapping trigger are established.
