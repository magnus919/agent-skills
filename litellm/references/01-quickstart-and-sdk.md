# LiteLLM Quickstart: Proxy Config and Python SDK

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/quick_start ,
> https://docs.litellm.ai/docs/proxy/configs , https://docs.litellm.ai/docs/completion/input ,
> https://docs.litellm.ai/docs/proxy/user_keys

This reference covers standing up a proxy with `config.yaml`, the config skeleton and
its top-level sections, endpoint surface, OpenAI-SDK drop-in usage, and the Python SDK
basics an operator needs. Scope: getting a correct deployment running and verified;
routing depth lives in [02-config-and-routing.md](02-config-and-routing.md).

## Install and first run

```bash
# The proxy server needs the [proxy] extra; bare litellm lacks websockets etc.
pip install 'litellm[proxy]'
litellm --version            # CLI reports its version
```

Python >=3.10 is required since 1.84.0 (on 3.9 pip silently installs <=1.83.9).
Packaging gotcha verified on 1.97.0: if startup fails with
`ImportError: cannot import name 'get_flat_dependant' from 'fastapi.dependencies.utils'`,
the installed fastapi is too new for this litellm — pin `fastapi==0.136.3`.

Three documented ways to start:

```bash
litellm --config /path/to/config.yaml [--port 4000] [--detailed_debug]
litellm --model huggingface/bigcode/starcoder          # single-model CLI mode
docker run -v $(pwd)/config.yaml:/app/config.yaml \
  -e LITELLM_MASTER_KEY=sk-<random> -p 4000:4000 \
  ghcr.io/berriai/litellm:v1.97.0 --config /app/config.yaml
```

Success line to look for in the logs: `LiteLLM: Proxy initialized with Config,
Set models:` — its absence means the config did not load. The default bind is
`0.0.0.0:4000`; set `--host` deliberately for anything network-reachable.

## Config skeleton and top-level sections

```yaml
model_list:
  - model_name: gpt-4o                     # name clients request (alias)
    litellm_params:
      model: azure/gpt-4o-eu              # string sent to the provider layer
      api_base: https://my-endpoint-europe.openai.azure.com/
      api_key: "os.environ/AZURE_API_KEY_EU"   # os.environ/ prefix => getenv at load
      rpm: 6                              # per-deployment limit informs weighted pick
  - model_name: "*"                       # wildcard catch-all (needs default creds in env)
    litellm_params:
      model: "*"

litellm_settings:                         # SDK-wide behavior
  drop_params: true                       # drop unsupported OPENAI params instead of erroring
  num_retries: 3
  request_timeout: 600                    # seconds; built-in default is 6000 on recent releases
  success_callback: ["langfuse"]

router_settings:                          # Router/load-balancer behavior
  routing_strategy: simple-shuffle        # default and recommended
  model_group_alias: {"gpt-4": "gpt-4o"}
  timeout: 30                             # whole-call timeout passed to completion()
  redis_host: os.environ/REDIS_HOST       # required when >1 proxy instance shares state

general_settings:                         # proxy-server settings
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL   # or DATABASE_URL env var; both accepted
  alerting: ["slack"]
  background_health_checks: true
  health_check_interval: 300

environment_variables:                    # extra env vars set inside the proxy process
  LANGFUSE_PUBLIC_KEY: ...
```

Details that matter:

- `os.environ/VARNAME` interpolation works for any value anywhere in the file.
  Resolution happens **inside the proxy process** — a variable present in your shell
  but not in the container produces opaque failures visible only via
  `--detailed_debug`.
- There is no standalone schema validator command; validation is at load time. YAML
  indentation/aliasing typos are the most common cause of "weird" behavior.
- Full spec is browsable as Swagger at `<proxy>/#/config.yaml`. `NO_DOCS="True"`
  disables that UI.
- With `store_model_in_db: true`, DB rows deep-merge over these YAML sections
  (`general_settings`, `router_settings`, `litellm_settings`, `environment_variables`)
  and win key conflicts; see [02-config-and-routing.md](02-config-and-routing.md).
- Enterprise license: `LITELLM_LICENSE` env var.

## Endpoint surface

| Route | Purpose |
|---|---|
| `/v1/chat/completions`, `/chat/completions` | Chat (OpenAI-compatible) |
| `/v1/completions` | Text completion |
| `/v1/embeddings`, `/embeddings` | Embeddings |
| `/v1/images/generations` | Image generation |
| `/v1/audio/transcriptions`, `/v1/audio/speech` | Transcription / TTS |
| `/responses` | OpenAI Responses API surface |
| `/messages`, `/anthropic/v1/messages` | Anthropic-compatible messages |
| `/v1/models` | Model aliases visible to the calling key (auth required when master_key set) |
| `/model/info` | Per-deployment detail incl. cost/max-token info (auth required) |
| `/health/liveliness` | Unauthenticated liveness → `"I'm alive!"` (spelling: liveliness) |
| `/health/readiness` | Unauthenticated readiness; 503 when the configured DB is unreachable |

Verified against a live 1.97.0 proxy: with `master_key` set, `/v1/models` returns 500
without auth and 200 with `Authorization: Bearer <key>`; `/health/liveliness` and
`/health/readiness` are unauthenticated by design. A representative call:

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_VIRTUAL_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Say hello"}]}'
```

The response carries `_response_ms` plus `x-litellm-*` headers (call id, model id,
resolved api_base, version) useful for forensics.

## OpenAI-SDK drop-in (any OpenAI-compatible client)

```python
import openai
client = openai.OpenAI(
    api_key="sk-virtual-key",             # virtual or master key, NOT a provider key
    base_url="http://localhost:4000",     # or https://gateway.example.com
)
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "hello"}],
    extra_body={"metadata": {"tags": ["production"]}},   # optional pass-through metadata
)
```

The same base-url swap works for LangChain (`ChatOpenAI`), LlamaIndex, Instructor,
Aider/LibreChat-style tools, and the Anthropic SDK pointed at the proxy's
`/messages` surface. Pass-through `metadata.tags` feed cost tracking and tag-based
features downstream.

## Python SDK essentials

```python
from litellm import completion, acompletion, embedding

resp = completion(
    model="openai/gpt-4o",                # provider/prefixed model string
    messages=[{"role": "user", "content": "hello"}],
    # timeout defaults to 600s; unsupported OpenAI params raise unless dropped:
    # drop_params=True here, or litellm.drop_params=True module-wide
)
resp.choices[0].message.content           # dict-style access also works
resp.usage.total_tokens
resp._hidden_params["response_cost"]      # USD cost from the model cost map

async for chunk in await acompletion(model="gpt-4o", messages=msgs, stream=True):
    print(chunk.choices[0].delta.content or "", end="")
```

Operator-relevant SDK facts:

- Model strings carry a provider prefix (`openai/`, `anthropic/`, `azure/<deployment>`,
  `bedrock/`, `vertex_ai/`, `gemini/`); bare names are inferred only for well-known
  families. Azure uses the **deployment name**, not the model name.
- Streaming chunks expose reasoning fields for reasoning models
  (`delta.reasoning_content`, `thinking_blocks`); Anthropic thinking maps differ by
  model generation — verify against the installed release.
- Cost/token helpers: `token_counter(model=..., messages=...)`,
  `completion_cost(response)`, `get_max_tokens(model)`, and the `litellm.model_cost`
  dict loaded from the community-maintained
  `model_prices_and_context_window.json` (there is no file named `model_cost.json`).
  Set `LITELLM_LOCAL_MODEL_COST_MAP="True"` to use the bundled copy offline.
- Check the installed version with `importlib.metadata.version("litellm")`;
  `litellm.__version__` raises AttributeError on current releases.
- Prefer `get_model_info(model=...)` over the partial `litellm.supports_*()` exports
  for capability flags like prompt caching.

## Verification at the delivery boundary

- Startup log shows `Proxy initialized with Config, Set models:`.
- `scripts/litellm-health --check health --check readiness --json` passes; readiness
  failing with 503 means a configured DB is unreachable.
- `/v1/models` with the calling key lists the expected alias.
- One bounded chat request returns tokens and the expected `x-litellm-model-id`.
