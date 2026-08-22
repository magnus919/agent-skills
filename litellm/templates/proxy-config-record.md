# LiteLLM Proxy Configuration Record

Fill this record before changing a proxy configuration. It is the rollback unit:
the previous record plus the previous pinned image is the rollback path.

## Deployment identity

- Requested outcome: _[fill: what this gateway must do and for whom]_
- Deployment type: _[fill: bare litellm / Docker / Compose / Helm / raw manifests]_
- Target and scope confirmed with: _[fill: who confirmed, when]_
- Rollback path: _[fill: previous image tag + previous config record]_

## Pinned artifacts

- LiteLLM version or image tag/digest: _[fill: ghcr.io/berriai/litellm:vX.Y.Z or pip litellm==...]_
- Cosign verification status: _[fill: verified against pinned key commit / not verified]_
- fastapi pin (pip installs): _[fill: e.g. fastapi==0.136.3 for 1.97.0, or n/a]_
- Config file source and path: _[fill: repo path or S3/GCS bucket reference]_
- Config-in-DB state: _[fill: store_model_in_db true/false; if true, note DB overlay wins]_
- Enterprise license in use: _[fill: yes/no]_

## Model list summary

| model_name | litellm_params.model | weight/rpm/tpm | order | notes |
|---|---|---|---|---|
| _[fill]_ | _[fill: provider/prefixed string]_ | _[fill]_ | _[fill]_ | _[fill: base_model, access_groups, ...]_ |

## Routing and reliability

- routing_strategy: _[fill: simple-shuffle default unless deliberately changed]_
- num_retries (settings/deployment/request): _[fill]_
- fallbacks / context_window_fallbacks / content_policy_fallbacks: _[fill: alias targets only]_
- cooldown settings: _[fill: allowed_fails, cooldown_time, policy overrides]_
- enable_pre_call_checks / optional_pre_call_checks: _[fill: on/off and why]_

## Keys, budgets, limits

- master_key source: _[fill: secret manager reference — never the value]_
- salt_key set (never rotated after models added): _[fill: yes/no]_
- global budget / duration: _[fill]_
- team/key budget scheme summary: _[fill: scopes and caps]_
- rate limits (tpm/rpm per scope; admin exemption acknowledged): _[fill]_

## Caching, guardrails, observability

- cache backend and ttl: _[fill: redis/none; semantic caching excluded for agents?]_
- guardrails configured (names, modes): _[fill]_
- callbacks wired: _[fill: langfuse/otel/prometheus/...]_
- privacy posture: _[fill: turn_off_message_logging, redact flags, store_prompts_in_spend_logs off?]_

## Data stores

- Postgres endpoint and pool math: _[fill: MAX_DB_CONNECTIONS / (instances x workers)]_
- Redis version and endpoints: _[fill: >=7.0 required when >1 instance]_
- Backup schedule for Postgres: _[fill]_

## Verification checklist

- [ ] `/health/liveliness` returns 200 (`litellm-health --check health`)
- [ ] `/health/readiness` returns 200 (DB reachable)
- [ ] `/v1/models` lists expected aliases for a representative key
- [ ] A representative chat request returns tokens; `x-litellm-model-id` matches intent
- [ ] Budget enforcement proven once with a tiny test budget
- [ ] Fallback path proven once by forcing a deployment failure

## Changes from the previous record

- _[fill: what changed, why, which verification backs it]_
