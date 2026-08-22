# LiteLLM Caching and Guardrails

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/caching ,
> https://docs.litellm.ai/docs/proxy/guardrails/quick_start ,
> https://docs.litellm.ai/docs/enterprise

This reference covers response caching backends and controls, the semantic-caching
stale-multi-turn caveat, and guardrail configuration with Presidio PII masking.
Scope: choosing and configuring these correctly for a workload; privacy defaults
live in [07-security-and-public-hosting.md](07-security-and-public-hosting.md).

## Response caching

```yaml
litellm_settings:
  cache: true
  cache_params:
    type: redis                       # production default for multi-instance
    host: os.environ/REDIS_HOST
    port: 6379
    password: os.environ/REDIS_PASSWORD
    namespace: "litellm.caching.caching"
    ttl: 600
    max_connections: 100
```

Backends: in-memory (per-process — wrong for >1 replica), disk, redis,
redis-cluster (`redis_startup_nodes`), sentinel, S3/GCS, and semantic variants
(`qdrant-semantic`, `redis-semantic`, `valkey-semantic`). Env alternatives:
`REDIS_URL` or `REDIS_HOST/PORT/PASSWORD/SSL` (+ arbitrary `REDIS_<kwarg>`);
docs recommend `REDIS_*` over `REDIS_URL` in production.

Controls that matter:

- Cacheable call types default to completion/embedding-style routes; scope via
  `cache_params.supported_call_types`.
- Per-request body controls: `"cache": {"ttl": 60, "s-maxage": 600, "no-cache":
  true, "no-store": true, "namespace": "..."}`. Opt-in mode
  (`cache_params.mode: default_off`) makes caching request-scoped only.
- Debug endpoints `/cache/ping` and `/cache/delete`; header `x-litellm-cache-key`
  exposes the key used.
- Provider-specific optional params are excluded from cache keys by default; opt in
  with `enable_caching_on_provider_specific_optional_params: true`.

### Semantic caching caveat

Semantic caches embed the **entire messages array** and serve nearest neighbors above
a similarity threshold. Consecutive agentic turns are often ~0.99 similar, so agents
get stale tool results replayed as cache hits — current docs warn against semantic
caching for multi-turn/agentic traffic outright. For agent workloads use exact-match
redis caching, exclude those keys from caching, or force `no-store` per request.

## Guardrails

```yaml
guardrails:
  - guardrail_name: "presidio-pii"
    litellm_params:
      guardrail: presidio
      mode: pre_call                    # pre_call | post_call | during_call | logging_only
      presidio_language: en
      pii_entities_config:
        CREDIT_CARD: MASK
        EMAIL_ADDRESS: MASK
        US_SSN: BLOCK
      presidio_score_thresholds:
        CREDIT_CARD: 0.8
        EMAIL_ADDRESS: 0.6

litellm_settings:
  guardrails: ["presidio-pii"]          # or per-request "guardrails": [...]
```

Modes are event hooks: `pre_call` (before the LLM call), `post_call` (after, on
input+output), `during_call` (parallel with the LLM call, blocking until the check
completes), `logging_only`. List form (`mode: [pre_call, post_call]`) is valid.
Older material describing a single `"all"` mode is outdated.

Behavior and invocation:

- Blocking providers fail the request with HTTP 400 embedding the provider verdict;
  masking providers (Presidio MASK) rewrite content instead of blocking.
- `default_on: true` runs a guardrail on every request regardless of client choice;
  otherwise clients pass `"guardrails": ["name"]` in the body.
- Applied guardrails surface in `x-litellm-applied-guardrails` and in the logging
  payload (`applied_guardrails`, `guardrail_information`, masked-entity counts) —
  feed these to your SIEM.
- OSS vs Enterprise: the framework, custom guardrails, Presidio PII masking, and
  always-on/request-scoped usage are free; several moderation integrations
  (llmguard, llamaguard, hide_secrets, openai/google moderations, lakera prompt
  injection, aporia prompt injection), per-key/per-team scoping, dynamic params,
  tag-based modes, model-level attach, and team lock-downs require an Enterprise
  license.
- `skip_system_message_in_guardrail` excludes system prompts on the unified path
  (Presidio, Bedrock, content filter, OpenAI Moderations, generic API, custom
  apply_guardrail); raw-hook providers are unaffected.

## Verification at the delivery boundary

- Send one identical request twice with caching enabled and confirm a cache hit
  (`x-litellm-cache-key` present; latency drops; spend not double-counted).
- Send one request containing a masked entity through the presidio guardrail and
  confirm the provider never sees the plaintext (check callback logs, bounded).
- Confirm `x-litellm-applied-guardrails` names what ran on each request.
