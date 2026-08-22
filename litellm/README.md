# LiteLLM — AI Gateway Operations Skill

Operate, configure, secure, and troubleshoot the LiteLLM AI gateway (proxy) and Python SDK: one config that routes to 100+ LLM providers through an OpenAI-compatible API, with virtual keys, teams, budgets and rate limits, caching, guardrails, observability, spend tracking, and evidence-led failure diagnosis.

## Why Install This Skill

Your agent can run the gateway instead of guessing. Teams that put an LLM gateway in front of OpenAI, Anthropic, Bedrock, Azure, Vertex, and local engines need someone (or something) that knows how to write a `config.yaml` whose duplicate `model_name` entries load-balance a group, why budgets silently fail open without Postgres, which response header tells you which deployment served a request, why `AnthropicException - Overloaded` is not a gateway bug, and how to harden a public-facing proxy against the 2026 CVE wave — without leaking keys or prompt content.

This skill ships that operating knowledge plus two fillable templates — a proxy config record (so every deployment is reproducible) and a deployment record (image digest, ports, data stores, rollback path) — and a read-only `litellm-health` probe that checks a running proxy's liveness, readiness, registered models, and model info over HTTP without changing anything. The references are distilled from the official LiteLLM documentation and verified against litellm 1.97.0 with dated sources. Engine-selection methodology deliberately routes up to `ml-engineering`; single-engine operation routes to `vllm` and `llama-cpp`; this skill owns the day-to-day operation of LiteLLM itself.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating contract, operating loop, verification boundaries, hard boundaries |
| `references/` | Nine dated, source-indexed references: source index, quickstart + SDK, config & routing, keys/teams/budgets/spend, caching & guardrails, observability & logging, deployment, security & public hosting, troubleshooting |
| `templates/proxy-config-record.md` | Fillable record of every model entry, routing knob, budget, and secret reference — the rollback unit |
| `templates/proxy-deployment.md` | Fillable record of the runtime: pinned image, ports, env vars, Postgres/Redis endpoints, probes, rollback path |
| `scripts/litellm-health` | Read-only probe: liveliness, readiness, `/v1/models`, `/model/info`; stdlib-only, `--json`, `--help` without a server |
| `tests/` | Deterministic tests against a local stub HTTP server, including the read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no LiteLLM proxy running
scripts/litellm-health --help

# Probe a running proxy, machine-readable
scripts/litellm-health --url http://127.0.0.1:4000 --json

# Model routes need the master key or a virtual key
scripts/litellm-health --check health --check readiness \
  --check models --key "$LITELLM_MASTER_KEY" --json

# Minimal multi-provider config, then start it
cat > config.yaml <<'YAML'
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
YAML
litellm --config config.yaml --port 4000

# Verify at the delivery boundary
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "ping"}]}' | head -c 400
```

The `litellm-health` script uses only Python's standard library and issues GET requests only. Exit codes: 0 all checks passed, 1 issues found or a fatal error, 2 usage error, 124 timeout. Health probes (`/health/liveliness`, `/health/readiness`) are unauthenticated by design; `models` and `model_info` require a bearer key. Before changing any production setting, fill in `templates/proxy-config-record.md` — it is the rollback unit.

## Triggers

Load this skill for LiteLLM operations: deploying or updating a proxy (`litellm --config`, the `ghcr.io/berriai/litellm` image, Helm charts), writing or debugging `config.yaml` (`model_list`, `router_settings`, `litellm_settings`, `general_settings`), routing to multiple providers through one OpenAI-compatible endpoint, configuring virtual keys, teams, budgets, or rate limits, response caching or guardrails (Presidio PII masking), observability callbacks (Langfuse, OpenTelemetry, Prometheus `/metrics`), spend tracking, hardening a public-facing gateway, or diagnosing request failures (401 vs provider auth errors, `No deployments available`, context-window fallbacks, timeouts). Do not load it for engine selection or serving methodology (`ml-engineering`), for operating vLLM or llama.cpp themselves (`vllm`, `llama-cpp`), or for generic Docker/Kubernetes administration (`docker-compose`, `kubernetes`).

## Requirements

- A LiteLLM release: `pip install 'litellm[proxy]'` (the `[proxy]` extra is required for the server; Python >=3.10 since 1.84.0) or the pinned container image `ghcr.io/berriai/litellm:vX.Y.Z`.
- For keys, teams, budgets, spend, and the admin UI: PostgreSQL (`DATABASE_URL`). For more than one replica: Redis >=7.
- Public deployments must run >=1.83.7 (CVE-2026-42208/42203/42271 fix floor; Starlette >=1.0.1).
- Python 3.9+ for the `litellm-health` script (`--help` needs nothing else); live probes need HTTP(S) access to the running proxy, and model routes require the master key or a virtual key.
