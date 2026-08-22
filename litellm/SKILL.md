---
name: litellm
description: >-
  Operate, configure, secure, and troubleshoot the LiteLLM AI gateway (proxy) and
  Python SDK: run the proxy (litellm --config), route to 100+ providers through one
  OpenAI-compatible API, configure model lists and routing/reliability, virtual keys,
  teams, budgets, rate limits, caching, guardrails, observability, and spend, and
  diagnose request failures. Use when deploying or running a LiteLLM proxy or gateway
  (config.yaml, ghcr.io/berriai/litellm), wiring the Python SDK or OpenAI SDK through
  it, or hardening a public-facing deployment. Do not use for operating a single
  inference engine (vllm, llama-cpp), for engine-selection methodology (ml-engineering),
  or for building applications on top of an LLM API (backend/frontend engineering).
license: MIT
compatibility: >-
  Requires litellm (pip, Python >=3.10) or the litellm proxy image
  (ghcr.io/berriai/litellm or docker.litellm.ai/berriai/litellm, pinned >=1.83.7 for
  public deployments). The bundled litellm-health script runs on Python 3.9+ and needs
  no proxy for --help; live probes require HTTP(S) access to a running proxy, and
  model routes require the master key or a virtual key.
metadata:
  source: https://docs.litellm.ai/
  source_index: references/00-source-index.md
  research_checked: "2026-08-22"
---

# LiteLLM AI Gateway Operations

Use this skill to operate **LiteLLM** as an organization's AI gateway: run the proxy
(`litellm --config config.yaml`), route requests to 100+ LLM providers through one
OpenAI-compatible API, manage model lists, routing and reliability, virtual keys,
teams, budgets and rate limits, caching, guardrails, observability, and spend — and
diagnose failures with evidence. LiteLLM ships two surfaces: a Python SDK
(`litellm.completion()`, in-process) and the proxy (a FastAPI service on port 4000
with keys, budgets, and an admin UI). This is a **tool skill** for the named tool.
Engine selection and serving methodology belong to
[ml-engineering](../ml-engineering/SKILL.md); operating a single engine belongs to
[vllm](../vllm/SKILL.md) or [llama-cpp](../llama-cpp/SKILL.md).

## Operating contract

1. **Record the deployment before tuning it.** Capture the pinned image or pip
   version, `config.yaml`, model list, routing, budgets, env-var references, and
   data stores in the [proxy config record](templates/proxy-config-record.md). That
   record is the rollback unit.
2. **Confirm the target, scope, and rollback path before mutating.** Read-only
   discovery (health probes, `/v1/models`, logs, spend queries) may proceed without
   confirmation. Mutations — config changes, key mint/revocation, restarts, image
   upgrades, DB migrations — require an explicit human directive naming the deployment.
3. **A proxy that responds is not a proxy that serves.** `/health/liveliness`
   returning 200 proves liveness only. Verify at the delivery boundary: a
   representative `/v1/chat/completions` request returns tokens and
   `x-litellm-model-id` names the deployment you expected.
4. **Keep evidence bounded.** Summarize logs and configs; never dump full logs,
   `.env` contents, master keys, or provider credentials into chat. Spend logs and
   debug output can contain prompt content — redact before sharing.
5. **Pin versions.** LiteLLM releases weekly and changes defaults; every claim here
   was checked against 1.97.0 (2026-08-22). Re-verify version-sensitive behavior
   against your installed release before relying on it.

## The litellm-health script

`scripts/litellm-health` is a read-only probe for a running proxy. It issues GET
requests only, never writes files, and emits bounded output.

```bash
scripts/litellm-health --help                                   # no proxy needed
scripts/litellm-health --url http://127.0.0.1:4000 --json
scripts/litellm-health --check health --check readiness --json
scripts/litellm-health --check models --check model_info \
  --key "$LITELLM_MASTER_KEY" --json
```

Exit codes: 0 all checks passed, 1 issues found or a fatal error, 2 usage error,
124 timeout. Checks: `health` (`GET /health/liveliness`, unauthenticated), `readiness`
(`GET /health/readiness`, unauthenticated; 503 when the configured DB is unreachable),
`models` (`GET /v1/models`, requires key), and `model_info` (`GET /model/info`,
requires key). Keys are sent as `Authorization: Bearer <key>`. The script never sends
data anywhere except the proxy you name.

## Operating loop

1. **Identify the deployment**: pinned version/image digest, how it runs (bare,
   Docker, Compose, Helm), config source (file, `store_model_in_db`, or both), and
   data stores (Postgres? Redis?).
2. **Collect evidence**: `litellm-health --json`; `GET /v1/models` and
   `/model/info` with a key; response headers (`x-litellm-call-id`,
   `x-litellm-model-id`, `x-litellm-model-api-base`, `x-litellm-version`);
   `--detailed_debug` logs or `LITELLM_LOG=DEBUG` for the outbound request.
3. **Triage against the symptom**: classify provider vs gateway errors (see
   [troubleshooting](references/08-troubleshooting.md)); check cooldown state,
   budgets, DB connectivity.
4. **Act with confirmation**: bounded, scoped changes after a human directive, with
   the rollback path named first.
5. **Verify**: re-run the probe and a representative chat request at the delivery
   boundary.

## Quickstart: one config, many providers

```yaml
model_list:
  - model_name: gpt-4o                     # name clients request
    litellm_params:
      model: openai/gpt-4o                 # routed string (provider prefix required)
      api_key: os.environ/OPENAI_API_KEY   # resolved inside the proxy process
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: os.environ/ANTHROPIC_API_KEY

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY   # require auth on every call
```

Start with `litellm --config config.yaml --port 4000`. Success logs
`Proxy initialized with Config, Set models:`. Clients call the OpenAI surface:
`/v1/chat/completions`, `/chat/completions`, `/v1/embeddings`, `/v1/images/generations`,
`/v1/audio/transcriptions`, plus `/responses`, Anthropic-compatible `/messages`,
`/model/info`, `/health/liveliness`, `/health/readiness`. Any OpenAI SDK works
unchanged: `openai.OpenAI(base_url="http://localhost:4000", api_key=<virtual key>)`.
Details and the SDK surface: [quickstart reference](references/01-quickstart-and-sdk.md).

## Config and routing

- Entries sharing a `model_name` form one load-balanced group; each entry is a
  deployment with its own hashed `model_id` used for health and cooldown tracking.
- `router_settings.routing_strategy` — `simple-shuffle` (default, recommended;
  weighted by `rpm`/`tpm` or `weight` under `litellm_params`), `least-busy`,
  `latency-based-routing`, `usage-based-routing` (docs warn against it in prod),
  `cost-based-routing`.
- Reliability: `litellm_settings.num_retries` (per-deployment and request-level
  overrides exist; `num_retries` is not the provider SDK's `max_retries`),
  `fallbacks` / `context_window_fallbacks` / `content_policy_fallbacks`,
  cooldowns (`allowed_fails`, `cooldown_time`), deployment `order` for priority,
  `enable_pre_call_checks: true` to enforce context windows and region filters
  pre-call (opt-in).
- With `store_model_in_db: true`, UI/API writes deep-merge over YAML in Postgres and
  win on key conflicts — editing those YAML keys later has no effect while the DB row
  exists. Details: [config and routing reference](references/02-config-and-routing.md).

## Keys, teams, budgets, spend

- `general_settings.master_key` (must start `sk-`) is the admin credential and UI
  password. Virtual keys (`POST /key/generate`) scope models, budgets, and rpm/tpm
  per workload; keys are stored hashed and never contain provider credentials.
- **Budgets require Postgres.** Without a connected DB, budgets fail open (a startup
  warning is the only signal) and key endpoints return `No connected db.` — never run
  a budget-sensitive deployment DB-less.
- Team keys enforce team (+ team-member) budgets only; the owner's personal budget
  does not apply. Rate limits do not apply to proxy admins. Spend lands in
  `/spend/logs` and `/global/spend`; `store_prompts_in_spend_logs` defaults to false.
  Details: [keys and budgets reference](references/03-keys-teams-budgets-spend.md).

## Caching and guardrails

- Response cache: `litellm_settings.cache: true` + `cache_params.type: redis` for
  multi-instance production (in-memory is per-process; disk/S3/GCS exist). Per-request
  controls: `cache: {ttl, no-cache, namespace}` in the body.
- Semantic caches (`qdrant-semantic`, `redis-semantic`, `valkey-semantic`) embed the
  whole messages array and can replay stale answers across similar multi-turn turns —
  docs recommend excluding agentic traffic from semantic caching.
- Guardrails run `pre_call`, `post_call`, `during_call`, or `logging_only` (there is
  no `all` mode); Presidio PII masking is OSS. Violations fail with HTTP 400 and an
  embedded verdict; `x-litellm-applied-guardrails` names what ran.
  Details: [caching and guardrails reference](references/04-caching-and-guardrails.md).

## Observability and logging

- Callbacks: `litellm_settings.success_callback` / `failure_callback` / `callbacks`
  (Langfuse, OTel, Prometheus, Datadog, Sentry, ...). Prometheus `/metrics` requires
  auth since 1.85.0 — give the scraper a bearer key or set
  `require_auth_for_metrics_endpoint: false`.
- Forensic response headers: `x-litellm-call-id`, `x-litellm-model-id`,
  `x-litellm-model-api-base`, `x-litellm-version`, `x-litellm-response-cost`.
- Privacy: `turn_off_message_logging: true` keeps metadata but drops content from
  callbacks; `redact_user_api_key_info: true` redacts key/user/team identifiers.
  Debug with `--detailed_debug`, `LITELLM_LOG=DEBUG`, or per-request
  `"litellm_request_debug": true`.
  Details: [observability reference](references/05-observability-and-logging.md).

## Deployment

- Postgres is mandatory for keys, teams, spend, budgets, and UI state; Redis >=7 is
  required for more than one instance (shared rate-limit counters, cooldowns, cache).
- Pin image tags (`ghcr.io/berriai/litellm:vX.Y.Z` — semver tags since 1.84.0;
  `-stable` suffixes are gone, `main-latest` is deprecated). Images are cosign-signed.
- Prisma migrations run at startup by default; on Kubernetes use the migration job
  pattern with `DISABLE_SCHEMA_UPDATE=true` on serving pods. One Uvicorn worker per
  pod; size the DB pool as `MAX_DB_CONNECTIONS / (instances x workers)`.
  Details: [deployment reference](references/06-deployment.md).

## Security and public hosting

- Version floor for any internet-reachable proxy: **>=1.83.7** (CVE-2026-42208
  pre-auth SQLi, CVE-2026-42203 SSTI, CVE-2026-42271 command injection, plus
  Starlette >=1.0.1 for the CVE-2026-48710 host-header chain). Two of these were
  CISA KEV-listed and actively exploited in 2026.
- Never expose management routes (`/key/*`, `/user/*`, `/team/*`, `/config/*`,
  `/model/*`, `/spend/*`, `/ui`, `/prompts/test`, `/mcp-rest/*`). Route lockdown via
  `allowed_routes` is Enterprise — on OSS, enforce at the reverse proxy.
- `LITELLM_SALT_KEY` encrypts DB-stored provider credentials; set it once and never
  rotate it after adding models. Rotate the master key only via the documented flow.
- March 2026 supply-chain incident: backdoored `litellm==1.82.7/.8` PyPI wheels
  (~40 minutes). Prefer cosign-verified pinned images over unpinned pip installs.
  Hardening checklist: [security reference](references/07-security-and-public-hosting.md).

## Troubleshooting: the master diagnostic rule

**If the error contains `<Provider>Exception`, the provider failed — not the
gateway.** `AnthropicException`, `OpenAIException`, `BedrockException`, ... mean the
upstream call happened and its response is the evidence. No provider name means the
gateway itself rejected the call (bad LiteLLM key, unknown model, cooldowns, budget).

| Symptom | First move |
|---|---|
| `Invalid model name passed in model=X` | Name not in `model_list` or not granted to the key; check `GET /v1/models` with the same key |
| `No deployments available for selected model, Try again in N seconds` | All deployments cooling down (usually upstream 429s) or a missing provider prefix on `litellm_params.model` |
| `AnthropicException - Overloaded` (HTTP 500, Anthropic's 529) | Provider-side overload; retry/fail over — not a gateway bug |
| `Authentication Error ... ExceededTokenBudget` | Key/team budget exhausted; check `GET /key/info` |
| `ImportError: cannot import name 'get_flat_dependant'` at startup | fastapi too new for the pinned litellm; pin `fastapi==0.136.3` for 1.97.0 |

Full taxonomy and fixes: [troubleshooting reference](references/08-troubleshooting.md).

## Reference routing

| Load when | Reference |
|---|---|
| Sources, version observations, refresh procedure | `references/00-source-index.md` |
| Proxy quickstart, config.yaml, Python SDK, OpenAI-SDK drop-in | `references/01-quickstart-and-sdk.md` |
| model_list, routing strategies, retries/fallbacks/cooldowns | `references/02-config-and-routing.md` |
| Virtual keys, teams, budgets, rate limits, spend | `references/03-keys-teams-budgets-spend.md` |
| Response caching and guardrails | `references/04-caching-and-guardrails.md` |
| Callbacks, Prometheus, headers, privacy switches | `references/05-observability-and-logging.md` |
| Docker/Compose/K8s/Helm, scaling, migrations, upgrades | `references/06-deployment.md` |
| Public-facing hardening, CVE floor, supply chain | `references/07-security-and-public-hosting.md` |
| Error taxonomy, failure modes, debugging workflow | `references/08-troubleshooting.md` |

## Included artifacts

- `scripts/litellm-health`: read-only proxy probe (stdlib-only, `--json`, `--check`
  subsets, `--key` for authenticated routes, `--help` without a server).
- `tests/test_litellm_health.py`: deterministic tests against a local stub HTTP
  server, including the read-only contract.
- `templates/proxy-config-record.md` and `templates/proxy-deployment.md`: fillable
  records — the config record is the rollback unit; the deployment record freezes the
  runtime (image digest, ports, env, data stores, probes, rollback).
- `references/`: nine dated, source-indexed references covering the topics above.
- `evals/evals.json`: six output-quality evaluation cases.

## Verification boundary

| Claim | Minimum evidence |
|---|---|
| The proxy is alive | `litellm-health --check health` reports `/health/liveliness` 200 |
| The proxy is ready | `--check readiness` reports `/health/readiness` 200 (503 means DB down) |
| The right models are registered | `/v1/models` (with the calling key) lists the expected aliases |
| A deployment is configured correctly | `/model/info` shows the expected `litellm_params` with keys redacted |
| Inference works | A representative `/v1/chat/completions` request returns tokens and `x-litellm-model-id` names the intended deployment |
| Budgets are enforced | A connected DB is verified (readiness) and `/key/info` shows spend tracking for the key |
| A diagnosis is sound | Evidence (error string, headers, logs) was collected before the claim, and the fix was verified by re-running the probe and a representative request |

## Hard boundaries

- Never mutate a production proxy (config, keys, teams, budgets, image, DB) without
  an explicit human directive naming the target and a stated rollback path. Read-only
  discovery may proceed freely.
- Never expose the master key, management routes, or `/ui` beyond the trust boundary;
  authentication is not a substitute for network and TLS controls.
- Never commit provider keys, `DATABASE_URL`, `LITELLM_MASTER_KEY`, or
  `LITELLM_SALT_KEY` anywhere; use `os.environ/` references and a secret manager.
- Never run a budget-sensitive public deployment without Postgres — budgets fail
  open without one.
- Never treat a 200 from `/health/liveliness` as proof the gateway serves; verify at
  the delivery boundary.

## When not to use

- **Engine selection, serving methodology, quantization decisions, evaluation
  design** — that is [ml-engineering](../ml-engineering/SKILL.md).
- **Operating a single inference engine** — [vllm](../vllm/SKILL.md) for vLLM,
  [llama-cpp](../llama-cpp/SKILL.md) for the llama.cpp stack. LiteLLM routes *to*
  engines; it does not replace their own operation.
- **Kubernetes/Docker fundamentals and reverse-proxy/TLS configuration** — that is
  [kubernetes](../kubernetes/SKILL.md), [docker-compose](../docker-compose/SKILL.md),
  and [traefik](../traefik/SKILL.md); this skill covers the LiteLLM-specific layer.
- **Building applications on top of an LLM API** (app architecture, agent frameworks)
  — that is backend/frontend engineering; this skill owns the gateway and its SDK.
