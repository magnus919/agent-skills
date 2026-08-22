# LiteLLM Operations — Source Index

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/ and https://github.com/BerriAI/litellm

This index tracks the authoritative upstream sources behind the LiteLLM operational
skill and the refresh procedure for keeping it current. LiteLLM releases weekly;
flags, defaults, endpoint behavior, and Enterprise boundaries change between
releases. Treat any claim in this skill as version-sensitive and re-verify against
the installed release.

## Canonical sources

| Topic | Source |
|---|---|
| Documentation home | https://docs.litellm.ai/docs/ |
| Releases and release notes | https://github.com/BerriAI/litellm/releases |
| Release cycle (weekly cadence, versioning) | https://docs.litellm.ai/docs/proxy/release_cycle |
| Proxy quickstart | https://docs.litellm.ai/docs/proxy/quick_start |
| Docker quickstart (UI-first flow, DB-less caveats) | https://docs.litellm.ai/docs/proxy/docker_quick_start |
| Config reference (`config.yaml` settings) | https://docs.litellm.ai/docs/proxy/configs and https://docs.litellm.ai/docs/proxy/config_settings |
| Routing / load balancing | https://docs.litellm.ai/docs/routing and https://docs.litellm.ai/docs/proxy/load_balancing |
| Reliability (retries, fallbacks, cooldowns) | https://docs.litellm.ai/docs/proxy/reliability |
| Virtual keys | https://docs.litellm.ai/docs/proxy/virtual_keys |
| Budgets / rate limits / teams | https://docs.litellm.ai/docs/proxy/users |
| Caching | https://docs.litellm.ai/docs/proxy/caching |
| Guardrails | https://docs.litellm.ai/docs/proxy/guardrails/quick_start |
| Logging / observability | https://docs.litellm.ai/docs/proxy/logging |
| Prometheus metrics | https://docs.litellm.ai/docs/proxy/prometheus |
| Health endpoints | https://docs.litellm.ai/docs/proxy/health |
| Response headers | https://docs.litellm.ai/docs/proxy/response_headers |
| Exception mapping | https://docs.litellm.ai/docs/exception_mapping |
| Error diagnosis (provider vs gateway rule) | https://docs.litellm.ai/docs/proxy/error_diagnosis |
| Debugging | https://docs.litellm.ai/docs/proxy/debugging |
| Timeouts | https://docs.litellm.ai/docs/proxy/timeout |
| Production checklist | https://docs.litellm.ai/docs/proxy/prod |
| Deployment (Docker/Helm/K8s/Terraform) | https://docs.litellm.ai/docs/proxy/deploy |
| Security best practices | https://docs.litellm.ai/docs/proxy/security_best_practices |
| Public/private routes (Enterprise) | https://docs.litellm.ai/docs/proxy/public_routes |
| Master key rotations / salt key | https://docs.litellm.ai/docs/proxy/master_key_rotations |
| Image security / cosign | https://docs.litellm.ai/docs/proxy/docker_image_security |
| Enterprise features and support policy | https://docs.litellm.ai/docs/enterprise |
| Python SDK input params | https://docs.litellm.ai/docs/completion/input |
| Provider pages (env vars, model strings) | https://docs.litellm.ai/docs/providers |
| Model cost map (community-maintained) | `model_prices_and_context_window.json` at the BerriAI/litellm repo root |

## Version observations (as of this refresh)

- Latest stable release: **litellm 1.97.0** (published 2026-08-16), checked live on
  2026-08-22 via `importlib.metadata.version("litellm")`. Pre-releases v1.98.0-rc.1
  and v1.99.0-dev.* were visible upstream. Stable cadence is weekly since 1.84.0.
- The proxy requires the `[proxy]` extra (`pip install 'litellm[proxy]'`); a bare
  install lacks websockets and friends. Python >=3.10 is required since 1.84.0.
- Known packaging gotcha verified on 1.97.0: the declared fastapi range admits a
  breaking 0.141.x where the proxy fails at startup with
  `ImportError: cannot import name 'get_flat_dependant'`; pinning
  `fastapi==0.136.3` fixes it.
- Endpoint behavior verified live against a 1.97.0 proxy with a master key set:
  `GET /health/liveliness` → 200 "I'm alive!" unauthenticated; `GET /health/readiness`
  → 200 unauthenticated; `GET /v1/models` → 500 without auth, 200 with a bearer key,
  returning `{"data": [...]}`; `GET /model/info` → 200 with a key and api_key values
  redacted as `"*************"`. The proxy binds 0.0.0.0 by default.
- `litellm.__version__` no longer exists (lazy module attrs); use
  `importlib.metadata.version("litellm")` or `litellm --version` for the CLI.
- Image tags are plain semver (`vX.Y.Z`) since 1.84.0: `-stable`/`-nightly` suffixes
  are gone, `main-latest` is deprecated and no longer updated. GHCR images are
  cosign-signed; docs also publish to docker.litellm.ai.
- Support policy (effective June 2026): only the four most recent stable minor lines
  receive updates.
- Route lockdown (`public_routes`, `admin_only_routes`, `allowed_routes`) is an
  Enterprise feature as of this refresh; JWT principals carry their own route lists.

## Refresh procedure

1. Check the releases page for the new stable; read its release notes for breaking
   changes (`!` markers), changed defaults, and security fixes.
2. Re-install into a scratch venv (`pip install 'litellm[proxy]'==<new>` plus the
   fastapi pin if needed), start a proxy with a dummy-key config, and re-verify the
   health endpoints with the bundled probe:
   `scripts/litellm-health --url http://127.0.0.1:<port> --check health --check readiness --check models --key <master> --json`.
3. Update the version observations above and any version-pinned claims in SKILL.md
   and references (CVE floor, `/metrics` auth, budget semantics, EE boundaries).
4. Re-run the bundled tests: `.venv/bin/python -m pytest litellm/tests/`.

## Related skill sources

- `ml-engineering` owns engine selection, quantization decisions, serving
  methodology, and evaluation design — the layer above gateway operations.
- `vllm` and `llama-cpp` own operating those inference engines themselves; LiteLLM
  routes to them via `openai/...`-style prefixes or dedicated ones (`hosted_vllm/`,
  `vllm/`, `lm_studio/`).
- `kubernetes`, `docker-compose`, and `traefik` own the infrastructure and TLS
  termination layers beneath a public proxy deployment.
