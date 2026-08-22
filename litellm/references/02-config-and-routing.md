# LiteLLM Config and Routing: model_list, Strategies, Reliability

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/routing ,
> https://docs.litellm.ai/docs/proxy/load_balancing ,
> https://docs.litellm.ai/docs/proxy/reliability ,
> https://docs.litellm.ai/docs/proxy/configs

This reference covers how `model_list` entries become load-balanced groups, the
routing strategies, and the reliability machinery — retries, fallbacks, cooldowns,
ordering, pre-call checks. Scope: making one gateway name resilient across many
provider deployments; keys/budgets live in [03-keys-teams-budgets-spend.md](03-keys-teams-budgets-spend.md).

## Model groups: same model_name = one LB group

Multiple entries sharing a `model_name` form a routing group; requests for that name
are distributed across deployments. Each entry is a distinct deployment with an
auto-generated deterministic `model_id` (hash of its `litellm_params`) used for
health, cooldown, and header forensics.

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      weight: 1
      rpm: 100
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o-eu              # Azure: DEPLOYMENT name, not model name
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      weight: 2                           # picked ~2x as often (simple-shuffle)
    model_info:
      base_model: openai/gpt-4o           # correct context/cost math for Azure aliases
```

Details that matter:

- `weight`, `rpm`, and `tpm` live under `litellm_params` and drive weighted picks.
- `model_info.base_model` fixes cost/context mapping when a provider alias echoes a
  generic model name (Azure especially).
- `router_settings.model_group_alias` maps extra request names onto a group;
  per-entry form supports `hidden: true` to keep aliases out of `/v1/models`.
- Wildcard entries (`model_name: "azure/*"`) expose whole provider families; pair
  with key-level model grants.

## Routing strategies

| Strategy | Behavior | Notes |
|---|---|---|
| `simple-shuffle` (default) | Weighted random by rpm/tpm/weight | Docs recommend it for production performance |
| `least-busy` | Fewest in-flight requests | Good at high concurrency |
| `latency-based-routing` | Lowest avg latency | Tune via `routing_strategy_args: {ttl, lowest_latency_buffer}` |
| `usage-based-routing` | Lowest TPM usage this minute | Redis-tracked; docs warn against prod use (latency) |
| `cost-based-routing` | Cheapest per cost map | Missing models assumed $1 unless priced |

There is no `routing_strategy: weighted` value — weighting rides on `simple-shuffle`
via `weight`/`rpm`. Newer releases add **routing groups** (`router_settings.routing_groups`)
to give specific groups their own strategy; group names are callable as model names,
appear in `/v1/models`, and must not collide with existing names.

## Retries

Precedence, highest first: request header `x-litellm-num-retries`, body
`num_retries`, per-deployment `num_retries` in `litellm_params`,
`litellm_settings.num_retries`. Rate-limit errors retry with exponential backoff;
a provider `retry-after` sets the minimum wait.

Critical distinction: LiteLLM's `num_retries` is its own loop; the provider SDK's
`max_retries` is pinned to 0 through the router so retries don't multiply
`(1+N)^2`. Setting `max_retries` in a request body has no effect through the router.

## Fallbacks

Three families plus a default, executed in list order:

```yaml
litellm_settings:
  fallbacks: [{"zephyr-beta": ["gpt-4o"]}]
  content_policy_fallbacks: [{"claude-2": ["my-fallback-model"]}]
  context_window_fallbacks: [{"gpt-4o-mini": ["gpt-4o"]}]
  default_fallbacks: ["claude-opus"]
```

- Fallback targets must be `model_name` aliases (or a specific deployment's
  `model_info.id`), not provider strings — pointing them at raw provider strings is a
  classic silent misconfig discovered mid-incident.
- Disable per request with `"disable_fallbacks": true` in the body.
- Context-window enforcement needs `router_settings.enable_pre_call_checks: true`;
  without it oversized prompts go to the provider regardless. With it, prompts over a
  deployment's limit raise ContextWindowExceededError locally before dispatch.
- Test fallback behavior by pointing one deployment at a deliberately bad key,
  observing failover, then restoring.

## Cooldowns

Per-deployment, not per-group. Triggers: immediate cooldown on upstream 429;
failure-rate threshold within the current minute (`allowed_fails`, default 3);
non-retryable 401/404/408. Duration via `cooldown_time`; deployments recover
automatically and counters reset. Per-error-class tuning:

```yaml
router_settings:
  allowed_fails_policy:
    RateLimitErrorAllowedFails: 100
    InternalServerErrorAllowedFails: 3
  cooldown_time: 30
```

When every deployment of a group is cooling down clients see
`No deployments available for selected model, Try again in N seconds...` (HTTP 429).
Docs do not recommend `disable_cooldowns: true` — it routes over exhausted limits.
Note `allowed_fails` belongs under `model_info`/policy blocks rather than loose
`litellm_params` (loose params leak into the provider request body).

## Deployment ordering and weighted failover

- `order: 1 / order: 2` in `litellm_params` gives priority tiers: tier 1 absorbs
  traffic until it fails/cools, then tier 2 serves; each tier gets its own retries
  before escalation, and configured `fallbacks` apply after all tiers.
- `router_settings.enable_weighted_failover: true` re-picks among same-group peers
  by weight on retryable failures, excluding already-failed ids (async calls only;
  not triggered for context-window or content-policy errors).

## Config-in-DB overlay semantics

With `store_model_in_db: true` (env `STORE_MODEL_IN_DB="True"`), writes from UI/API
land in Postgres and deep-merge over YAML for `general_settings`,
`router_settings`, `litellm_settings`, and `environment_variables` — DB wins key
conflicts. Editing those sections in YAML later has no effect while a DB row exists
(delete the row or the setting to restore YAML control). Models added via UI land in
a dedicated table and load-balance alongside same-named YAML models rather than
replacing them. Cross-pod config sync is polling
(`proxy_config_reload_interval_seconds`, default 30). Without `store_model_in_db`,
YAML is fully authoritative.

## Verification at the delivery boundary

- `/v1/models` lists each alias once per group; `/model/info` shows one entry per
  deployment with distinct `model_id`s.
- A representative request returns tokens and `x-litellm-model-id` identifies which
  deployment served it; repeat a few times to observe weighted distribution.
- Force one failure path (bad key on a low-weight deployment) and confirm the
  configured fallback/ordering actually fires before trusting it in production.
