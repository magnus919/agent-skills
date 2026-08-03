# vLLM OpenAI-Compatible API Surface

> **Last Updated:** 2026-08-03
> Source: https://docs.vllm.ai/en/latest/serving/online_serving/

## Basic endpoints

| Endpoint | Purpose |
|---|---|
| `/health` | Liveness; returns 200 only when the engine is ready to serve |
| `/version` | vLLM version information |
| `/v1/models` | List of served models (the `served-model-name`s clients must use) |
| `/load` | Server load metrics |
| `/metrics` | Prometheus-compatible metrics (`vllm:*` counters and gauges) |

## Inference endpoints

- `/v1/completions` — text generation (no chat template needed). Note: the
  `suffix` parameter is not supported.
- `/v1/chat/completions` — chat; requires the model to carry a chat template in
  its tokenizer config (or pass `--chat-template <file|string>`). The `user`
  parameter is ignored. `parallel_tool_calls` controls whether more than one
  tool call per response is allowed.
- `/v1/responses` (+ `/v1/responses/{id}/cancel`) — the OpenAI Responses API,
  for text-generation models.
- `/v1/embeddings` — for embedding/pooling models.
- `/v1/audio/transcriptions` and `/v1/audio/translations` — ASR models.
- Anthropic Messages API (`/v1/messages`, `/v1/messages/count_tokens`) and
  gRPC (`--grpc`) are also served on recent releases.

Chat models whose card lacks a template, and pooling/embedding models, will not
serve chat routes; a 404 on `/v1/chat/completions` while `/v1/models` works is
the classic symptom.

## Request/response facts

- The `model` field in requests must match a `--served-model-name` (or the
  `--model` value if none was set). `--served-model-name` accepts multiple names
  and aliases; the response echoes the first.
- Streaming (`"stream": true`) emits `choices[].delta` chunks with a terminal
  `finish_reason`. Tool calling requires server flags: `--enable-auto-tool-choice
  --tool-call-parser openai` (parser per model family). Structured outputs use
  xgrammar or guidance backends.
- Sampling parameters (temperature, top-p, top-k, max_tokens, stop, logprobs)
  are per-request; `--max-logprobs` caps logprobs server-wide.

## Exposure and security

- Start on loopback (`--host 127.0.0.1`) and verify with `vllm-health` and a
  bounded request before any wider bind. Exposing beyond loopback requires an
  explicit decision: bind address, API key (`--api-key`), TLS or a trusted
  reverse proxy, firewall, CORS, and rate limiting.
- Development-only and destructive routes must never be exposed in production:
  `/reset_prefix_cache`, `/reset_mm_cache`, weight-transfer endpoints
  (`/start_weight_update`, `/update_weights`), profiling (`/start_profile`),
  and `/collective_rpc`. vLLM gates some of these behind
  `VLLM_SERVER_DEV_MODE=1` — do not enable dev mode on production ingress.
- `--enable-log-requests` at debug level logs prompt text; keep it off or
  redacted in shared/audited sessions. Do not print or `tee` unredacted
  environment files, `.env` contents, or HF tokens.

## Verification checklist

1. `/health` returns 200.
2. `vllm-health --check models --json` lists the served model name(s).
3. A bounded chat/completion request returns generated tokens and a
   `finish_reason`.
4. Streaming and tool-calling paths are verified with the exact client that
   production uses (not assumed from endpoint existence).
