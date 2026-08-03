---
title: "Observability Contract: [Service Name]"
doc_id: OBC-[SERVICE-CODE]-[VERSION]
status: draft | reviewed | approved | superseded
created: [YYYY-MM-DD]
last_modified: [YYYY-MM-DD]
owner: "[Service Owner / Team]"
approver: "[SRE / Platform Lead]"
---

# Observability Contract — [Service Name]

## 1. Service Context

| Field | Value |
|---|---|
| **Service Name** | [Service Name] |
| **Owner** | [Team / Individual] |
| **Environments** | [dev, staging, prod] |
| **Dependencies** | [Upstream/downstream services, data stores] |
| **SLO reference** | [Link to SLO declaration or error budget policy] |

## 2. Signals Required

Every service must emit all three signals before production traffic is accepted.

### 2.1 Metrics

| Metric | Type | Name | Definition |
|---|---|---|---|
| Request rate | Counter | _[fill: e.g., svc_http_requests_total]_ | _[fill: label set, status split]_ |
| Error rate | Counter | _[fill: e.g., svc_http_errors_total]_ | _[fill: which statuses count as errors]_ |
| Latency | Histogram | _[fill: e.g., svc_http_request_duration_seconds]_ | _[fill: buckets, percentiles consumed]_ |
| Saturation | Gauge | _[fill: e.g., svc_queue_depth]_ | _[fill: what resource is near exhaustion]_ |

- **Scrape endpoint:** _[fill: e.g., /metrics on :9090]_ — must be reachable by the platform scraper.

### 2.2 Logs

- **Format:** _[fill: structured JSON with timestamp, level, service, trace_id, span_id]_
- **Shipping:** _[fill: agent/target — e.g., Promtail/Alloy/Fluent Bit]_
- **Retention requirement:** _[fill: hot/warm/cold tiers and durations]_
- **Sensitive data:** _[fill: what must never be logged — tokens, PII, full payloads]_

### 2.3 Traces

- **Instrumentation:** _[fill: OpenTelemetry SDK, auto-instrumentation, or manual spans]_
- **Context propagation:** _[fill: W3C TraceContext across all outbound calls]_
- **Sampling:** _[fill: head/tail sampling strategy and rate]_
- **Key spans:** _[fill: entry, external calls, DB queries, background jobs]_

## 3. Dashboards and Recording Rules

| Artifact | Name / Path in Git | Content |
|---|---|---|
| Service dashboard | _[fill: provisioning path]_ | _[fill: RED panels, per row: traffic, errors, latency, saturation]_ |
| Recording rules | _[fill: rules file path]_ | _[fill: rate/error-duration derivations, error budget expressions]_ |
| Dashboard links | _[fill: links to related platform dashboards]_ | _[fill: cross-service dependency view]_ |

- **Dashboard-as-code requirement:** _[fill: dashboards live in Git and change via review, not ad-hoc UI edits]_

## 4. Alerting and Error Budgets

| Alert | Condition (query) | Severity | Routing | Action |
|---|---|---|---|---|
| _[fill: High error rate]_ | _[fill: PromQL expression]_ | _[fill: critical/warning]_ | _[fill: page/Slack]_ | _[fill: incident response, freeze, rollback]_ |
| _[fill: Latency p99 breach]_ | _[fill: PromQL expression]_ | _[fill: severity]_ | _[fill: routing]_ | _[fill: action]_ |
| _[fill: Budget burn rate]_ | _[fill: multi-window burn rate expression]_ | _[fill: severity]_ | _[fill: routing]_ | _[fill: action]_ |

- **Error budget policy applied:** _[fill: link or reference to the team error budget policy]_
- **Noise control:** _[fill: `for:` durations, deduplication, silenced maintenance windows]_

## 5. Release and Verification Gate

| Gate | Requirement |
|---|---|
| Pre-release | _[fill: dashboards live, alerts firing correctly, metrics scraping, traces flowing]_ |
| Canary verification | _[fill: what SLIs are compared between canary and control and at what divergence]_ |
| Post-release | _[fill: regression check against baseline within N minutes, on-call notified]_ |

- **Verification evidence:** _[fill: where the evidence (dashboards, alert receipts, trace samples) is recorded]_

## 6. Ownership and Review

| Item | Value |
|---|---|
| **Observability owner** | [Team / Individual] |
| **Review cadence** | [Quarterly or on architecture change] |
| **Next review date** | [YYYY-MM-DD] |

### Sign-off

| Role | Name | Date |
|---|---|---|
| Service Owner | [Name] | [YYYY-MM-DD] |
| SRE / Platform Lead | [Name] | [YYYY-MM-DD] |

*This contract is part of the service's production readiness review and lives in Git next to the dashboards and rules it describes.*
