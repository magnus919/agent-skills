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

### D) 429 rate limits — identify the limiter and boundary

A 429 is not necessarily upstream. Classify the response and logs before changing
configuration: a provider 429 includes `<Provider>Exception`; a proxy-side limit
may name a key or team limiter; a router cooldown can report that no deployment is
available. Budget exhaustion is a separate Budget/TokenBudget error. Budgets can
fail open without a DB, and rate-limit checks may not apply to proxy admins, so use
an internal-user test key when verifying enforcement.

LiteLLM has multiple limiter scopes. Key-level `tpm_limit`, `rpm_limit`, and
`max_parallel_requests` apply to that key; per-model key limits use
`model_tpm_limit` and `model_rpm_limit`. Team limits apply to team membership,
while `general_settings.global_max_parallel_requests` is proxy-wide. A model or
deployment `rpm`/`tpm` value in `litellm_params` may guide weighted routing rather
than enforce a hard ceiling unless `enforce_model_rate_limits` is enabled. Do not
infer a global, model, or deployment limit from a key-level message, and treat any
future limiter or version-specific implementation as unverified until checked in
the pinned release.

A bounded v1.98.0 observation from 2026-08-25 included `Limit type: tokens`, a
`Current limit: 400000`, remaining tokens, and a reset timestamp. In that sample,
LiteLLM's `ProxyRateLimitError` was raised by
`proxy/hooks/parallel_request_limiter_v3.py` before the provider call, with logging
through `common_request_processing.py _handle_llm_api_exception`. These are
implementation details of that observation, not universal behavior, and no live
v1.98.0 reproduction was performed for this reference.

To investigate a suspected key limiter, first capture the complete response,
request ID, key identity without logging the secret, selected model/deployment,
and the configured key/team/model values. Verify with the same key through the
proxy: readiness, `/v1/models`, `/health?model=<name>`, response headers, and one
small representative request. Prefer these bounded API and gateway checks before
any authorized database inspection. If a change is approved, confirm the exact
key/team/deployment target, intended scope, and rollback owner; read and record
prior `tpm_limit`, `rpm_limit`, `max_parallel_requests`, and related values before
changing them. Preserve those values and restore them after the test. Use an
explicit, complete payload, for example:

```json
{
  "key": "<token>",
  "tpm_limit": null,
  "rpm_limit": null,
  "max_parallel_requests": null
}
```

Send that payload to `POST /key/update` only after the confirmation gate. Explicit
`null` requests clearing these key fields; omitting a field leaves its prior value
in place. Clearing key limits cannot prove that a team, global, model, deployment,
or provider limiter is absent. Re-read the effective configuration and restore the
recorded values through the same authorized API. Inspect Postgres directly only
when the API/gateway evidence is insufficient and the operator has approved the
specific read scope.

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
