# LiteLLM Observability: Callbacks, Metrics, Headers, Privacy

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/logging ,
> https://docs.litellm.ai/docs/proxy/prometheus ,
> https://docs.litellm.ai/docs/proxy/config_settings ,
> https://docs.litellm.ai/docs/proxy/debugging

This reference covers logging integrations (callbacks), Prometheus metrics, the
forensic response headers, debugging workflow switches, and the privacy flags that
decide what content leaves the proxy. Scope: seeing and controlling what happened;
error-specific fixes live in [08-troubleshooting.md](08-troubleshooting.md).

## Callbacks

```yaml
litellm_settings:
  success_callback: ["langfuse"]        # success-only
  failure_callback: ["sentry"]          # failure-only
  callbacks: ["otel"]                   # both
  service_callbacks: ["datadog", "prometheus"]   # system health (redis/postgres/auth)
  turn_off_message_logging: true        # metadata yes, message content no
  redact_user_api_key_info: true        # redact key/user/team identifiers in traces
```

- Langfuse needs `LANGFUSE_PUBLIC_KEY/SECRET_KEY/HOST`; request `metadata` passes
  through (`trace_id`, `tags`, ...). OTel needs `OTEL_EXPORTER=otlp_http|otlp_grpc|console`,
  `OTEL_ENDPOINT`, `OTEL_HEADERS`; per-callback redaction via
  `callback_settings.otel.message_logging: false`.
- Every event carries a standardized payload (`standard_logging_object`) documented
  at the logging spec page — build dashboards/SIEM rules on it rather than scraping
  free-text logs.

## Prometheus metrics

```yaml
litellm_settings:
  callbacks:
    - prometheus
```

- The `/metrics` endpoint **requires auth since v1.85.0**: configure the scraper
  with `authorization: Bearer <key>` or open it explicitly with
  `require_auth_for_metrics_endpoint: false`. Multiple workers need a writable
  `PROMETHEUS_MULTIPROC_DIR`.
- Key series: `litellm_proxy_total_requests_metric`,
  `litellm_proxy_failed_requests_metric`, `litellm_spend_metric`,
  `litellm_deployment_success_responses/_failure_responses`,
  `litellm_deployment_state` (0 healthy / 1 partial / 2 outage),
  `litellm_deployment_cooled_down`, latency family including TTFT for streaming,
  cache hit metrics, and budget gauges.
- Official Grafana dashboard JSON ships in the upstream repo's cookbook directory;
  cardinality controls (`custom_prometheus_metadata_labels`, metric filtering) exist
  for large fleets — end-user labels are opt-in for good reason.

## Forensic response headers

```
x-litellm-call-id           correlate one request across logs/callbacks
x-litellm-model-id          which deployment served this request
x-litellm-model-api-base    resolved provider base URL
x-litellm-version           proxy version
x-litellm-response-cost     computed USD cost
x-litellm-key-tpm-limit / x-litellm-key-rpm-limit   applied limits
x-litellm-applied-guardrails (when guardrails ran)
```

Some cost-detail headers are documented as non-streaming only; verify which headers
survive on streamed responses for your release before building alerts on them.

## Debugging workflow

1. Reproduce through the proxy with `--detailed_debug` (CLI) or
   `LITELLM_LOG=DEBUG`; logs show the resolved outbound curl (masked key) and raw
   provider response. Single-request variant: `"litellm_request_debug": true` in the
   body emits raw request/response for that request only.
2. Classify provider vs gateway from the error string (see
   [08-troubleshooting.md](08-troubleshooting.md)).
3. Check what the router sees: `/v1/models`, `/model/info`, `/health?model=<name>`,
   `/health/readiness/details` (authenticated diagnostics).
4. Correlate with `x-litellm-call-id` in callback logs; enable JSON logs
   (`json_logs: true`) and `request_correlation_in_logs` to stamp trace ids.
5. CLI helpers: `litellm --config config.yaml --health` health-checks configured
   models; `--test` fires a test chat request. Keep debug off in production
   (`LITELLM_LOG=ERROR`); `set_verbose` is deprecated.

## Privacy switches

| Flag | Effect |
|---|---|
| `store_prompts_in_spend_logs` (default false) | Opt-in full prompt/response storage in Postgres; raises memory floor |
| `turn_off_message_logging: true` | Metadata reaches callbacks, content does not |
| `redact_user_api_key_info: true` | Redacts hashed token/user/team info in supported callbacks |
| `"no-log": true` (per request) | Skips logging for that request (globally disableable) |
| UI Spend Log settings toggle | Overrides config-file values at runtime — audit it on managed deployments |

The Admin UI can flip prompt storage on without a restart and without touching your
config file — treat the UI state as part of the effective configuration when
auditing privacy posture (details:
[07-security-and-public-hosting.md](07-security-and-public-hosting.md)).

## Verification at the delivery boundary

- One test request appears in each configured destination (Langfuse trace, OTel
  span, `/metrics` counters move).
- With `turn_off_message_logging: true`, confirm prompts are absent from the
  callback destination while metadata still arrives.
- `/metrics` scrape succeeds with the exact auth configuration production will use.
