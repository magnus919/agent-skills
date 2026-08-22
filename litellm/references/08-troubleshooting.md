# LiteLLM Troubleshooting: Error Taxonomy, Failure Modes, Debugging

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/error_diagnosis ,
> https://docs.litellm.ai/docs/exception_mapping ,
> https://docs.litellm.ai/docs/proxy/debugging ,
> https://docs.litellm.ai/docs/proxy/timeout

This reference is the evidence-led playbook for diagnosing proxy and SDK failures:
the provider-vs-gateway rule, the exception taxonomy, the common failure modes with
their exact error strings, and the debugging loop. Scope: diagnosis and fixes;
observability plumbing lives in [05-observability-and-logging.md](05-observability-and-logging.md).

## The master diagnostic rule

**If the error contains `<Provider>Exception`, it came from the provider — not the
gateway.** `AnthropicException`, `OpenAIException`, `AzureException`,
`BedrockException`, `VertexAIException` mean the upstream call happened; the
provider's response is your evidence. No provider name in the error means LiteLLM
itself rejected or failed the call (bad LiteLLM key, unknown model name, cooldowns,
budget).

- Provider example: `litellm.BadRequestError: BedrockException - {...validation...}`
- Gateway example: `Invalid API Key. Please check your LiteLLM API key.` with
  `"type": "auth_error"` — that is your **LiteLLM** key being wrong.
- An opaque gateway-side 500 often hides a provider auth failure (a key present in
  your shell but not in the container); read the proxy's debug logs rather than the
  client exception.

## Exception taxonomy (SDK + proxy surface)

All importable from `litellm`; all carry `.status_code`, `.message`, `.llm_provider`;
most inherit OpenAI exceptions so existing client handlers keep working.

| Status | Exception | Notes |
|---|---|---|
| 400 | `BadRequestError` | Base 400 |
| 400 | `UnsupportedParamsError` | Unsupported OpenAI param passed (drop via `drop_params`) |
| 400 | `ContextWindowExceededError` | Exists to enable context-window fallbacks |
| 400 | `ContentPolicyViolationError` | Enables content-policy fallbacks |
| 401 | `AuthenticationError` | Provider or gateway auth failure — apply the rule above |
| 403 | `PermissionDeniedError` | Includes EE route restrictions |
| 404 | `NotFoundError` | Invalid model name for the calling key |
| 408 | `Timeout` | Call exceeded timeout/stream_timeout |
| 422 | `UnprocessableEntityError` | Malformed request values |
| 429 | `RateLimitError` | Provider, key/team, or router cooldown exhaustion |
| 500 | `APIConnectionError` / `InternalServerError` | Unmapped errors incl. Anthropic's HTTP 529 overload |
| 503 | `ServiceUnavailableError` | Upstream unavailable |
| n/a | `BudgetExceededError` | Proxy-side budget exhausted |

Retryability helper: `litellm._should_retry(status_code)`.

## Failure modes: string → cause → fix

### A) "No deployments available for selected model, Try again in N seconds"

HTTP 429 from the router. Causes: every deployment of the group is in cooldown
(usually after upstream 429 storms), or a deployment is misconfigured so no valid
one exists. Fixes: check `/health?model=<name>` per deployment; correct missing
provider prefixes (`model: gemini/gemini-2.5-flash`, not bare names); raise
`cooldown_time`/tune `allowed_fails_policy`; do not reach for
`disable_cooldowns: true` — docs warn it routes over exhausted limits.

### B) "Invalid model name passed in model=X. Call /v1/models to view available models"

The requested alias is not registered or not granted to this key. Fixes: compare
with `GET /v1/models` **using the same key** (model grants are per key); add the
missing `model_name` entry; fix the client's model string. Related SDK variant:
`LLM Provider NOT provided...` means a missing `provider/` prefix on the model
string.

Gemini-specific gotcha: without the `gemini/` prefix a Gemini model string can route
to Vertex AI and demand GCP credentials — a classic first-config 401.

### C) Authentication errors — disambiguate first

Gateway 401 (`auth_error`, no provider name): bad or absent LiteLLM key. Verify
which value actually resolved — `general_settings.master_key` in config overrides
the `LITELLM_MASTER_KEY` env var. Provider 401 (`<Provider>Exception ... Incorrect
API key provided`): the provider credential in the proxy process is wrong or absent;
confirm inside the container (`printenv`), not in your shell.

Master-key rotation hazard: with `LITELLM_SALT_KEY` set, rotate by changing the
secret and restarting; the regenerate flow re-encrypts stored credentials under an
unusable key and bricks the deployment. Symptom of salt-key trouble at startup:
`Error decrypting value`.

### D) 429 rate limits — three different sources

Read the wording: key/team rpm/tpm rejections come before any provider call and
name the limit; budget exhaustion raises Budget/TokenBudget errors naming spend vs
max (check `GET /key/info`); provider 429 carries `<Provider>Exception`, gets retried
with backoff, then cools the deployment down (mode A). Remember budgets fail open
without a DB and rate limits don't apply to admins.

### E) ContextWindowExceededError

Mapping to this exception is best-effort across providers — some overflows surface
as generic BadRequestError. Prefer preventing dispatch entirely:
`router_settings.enable_pre_call_checks: true` enforces context windows pre-call;
per-deployment `model_info.max_input_tokens` overrides detection; Azure needs
`model_info.base_model` set for correct window/cost mapping. Remedies ladder:
context-window fallbacks → client-side truncation/summarization → larger-context
deployment.

### F) Timeouts and hanging streams

Knobs: `router_settings.timeout` (whole call),
`litellm_settings.request_timeout` (recent releases default to 6000s — bound it),
per-deployment `timeout` and `stream_timeout` (time-to-first-chunk guard).
Idle load-balancers killing silent streams are mitigated by SSE keepalive pings
(`keepalive_seconds`). Known sharp edges around stream_timeout enforcement have been
reported on specific versions — pin and verify on yours. Long non-streaming calls
behind LBs can hit 504s; prefer streaming for long generations.

### G) Connection errors and startup failures

`APIConnectionError` is the catch-all unmapped mapping. Diagnosis order:
`--detailed_debug` shows the resolved outbound curl (masked); verify egress/DNS/
proxy env vars from inside the pod; if no provider request-id appears anywhere, the
call never left the proxy. Startup `ImportError: cannot import name
'get_flat_dependant'` = fastapi too new for the pinned litellm (pin
`fastapi==0.136.3` on 1.97.0). Startup `Error decrypting value` = salt-key problem
(see C).

### H) Streaming failures

Mid-stream stalls can be misclassified as read timeouts; partial-chunk decode errors
have appeared on specific provider paths in specific versions. Fallbacks fire on
stream *start* failures reliably but mid-stream fallback behavior has varied across
releases — test your pinned version. Client disconnects mid-stream can leave
incomplete spend records; reconcile against callbacks if billing-grade accuracy
matters.

## Debugging workflow

1. Reproduce through the proxy with `--detailed_debug` or `LITELLM_LOG=DEBUG`; the
   log shows the outbound request (masked) and raw response. Per-request:
   `"litellm_request_debug": true`.
2. Classify with the master rule; capture the full error string, status, and
   `x-litellm-call-id`.
3. Inspect router state: `/v1/models` (same key!), `/model/info`,
   `/health?model=<name>`, `/health/readiness/details`.
4. Read response headers: which deployment served (`x-litellm-model-id`), what
   api_base was used, retries/fallbacks attempted.
5. Fix the smallest thing consistent with the evidence; verify with the health probe
   plus one representative request; record the incident in the config/deployment
   template so the next operator inherits the knowledge.

## Verification at the delivery boundary

A diagnosis counts as sound only when the fix was observed working through the same
boundary the client uses: probe green, one bounded chat request returning tokens,
and the original failing request shape succeeding again.
