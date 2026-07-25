# Inference and serving

Use this reference for `llama-cli`, `llama-server`, chat templates, structured output, embeddings, reranking, function calling, and network exposure.

## Bounded CLI smoke test

Start with one model, one short prompt, a bounded output, and explicit sampling where reproducibility matters:

```sh
llama-cli -m /path/to/model.gguf \
  -p "Reply with exactly: llama.cpp ready" \
  -n 16 -s 42
```

Confirm against the installed help that each option still has the intended meaning. Capture startup logs separately from generated output. Pass criteria are not merely exit code zero: the expected model and backend load, memory remains stable, output is usable for the intended mode, and timings are recorded.

For chat models, inspect the embedded `tokenizer.chat_template`, original model card, and llama.cpp logs. Conversation mode may auto-enable when a template exists. Test the real system/user message behavior needed by the application. A plain prompt completion does not prove chat-template correctness.

## Template diagnosis and overrides

Use this order:

1. identify the exact base/fine-tune model and source template;
2. inspect GGUF template metadata and server `/props` when available;
3. check logs for the selected chat/tool format;
4. render or send a minimal representative conversation;
5. compare special tokens, role boundaries, stop behavior, reasoning fields, and tool-call shape with the model documentation;
6. only then test a current built-in or file-based template override.

Preserve the original launch and model. Do not apply a familiar template merely because the model family name looks similar. Tool-use variants can differ from default chat variants, and aggressive KV-cache quantization can damage structured or tool-calling behavior.

## Local server proof

First bind to loopback:

```sh
llama-server -m /path/to/model.gguf --host 127.0.0.1 --port 8080
```

In another shell:

```sh
curl --fail-with-body http://127.0.0.1:8080/health
curl --fail-with-body http://127.0.0.1:8080/v1/models
```

The health endpoint can return 503 while the model loads and 200 when ready. Select a model identifier reported by the running server, then make a representative request:

```sh
curl --fail-with-body http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "<reported-model-id>",
    "messages": [{"role": "user", "content": "Reply with exactly: server ready"}],
    "max_tokens": 16,
    "temperature": 0
  }'
```

Verify status, response schema, finish reason, content, usage/timings when exposed, and server logs. Do not claim complete OpenAI API parity; test the exact routes and fields the client needs and review the REST API changelog before upgrades.

## External exposure gate

Changing from loopback is a consequential operation. Confirm:

- intended clients and network boundary;
- bind address, firewall/security group, and reverse-proxy path;
- API-key source, rotation, and log redaction;
- TLS termination and forwarded headers;
- CORS origins, methods, headers, and credential behavior;
- request/body/time limits, concurrency, rate limiting, and denial-of-service controls;
- prompt/response logging policy and data retention;
- monitoring, restart policy, rollback binary/model/config, and external smoke test.

Prefer an API-key file or supported secret injection over a literal key in a command. A public health endpoint and an authenticated inference endpoint have different exposure properties. Test from both an allowed client and a denied/untrusted path.

The server includes experimental built-in filesystem and shell tools. Do not enable them in untrusted environments. If explicitly required, isolate the process, constrain filesystem/network permissions, enumerate only needed tools, and verify the trust boundary separately.

## Structured output and grammars

Use the installed help and current server docs to choose JSON Schema or grammar support. Validate both syntactic conformance and task semantics. A grammar can make invalid output impossible while still producing a semantically wrong value. Keep schema complexity within currently supported features and test error behavior.

## Embeddings and reranking

Use a model designed for the requested task and start the server in the corresponding mode. Check `/v1/models` or current capability reporting, pooling configuration, vector dimension, normalization, input limits, and batch behavior. Verify with a small known-similarity or ranking fixture; an endpoint returning numbers is not semantic proof.

## Function calling

Function calling depends on the model, template, parser/handler, and request schema. Inspect `/props` and logs, use a tools-aware template, and test a minimal deterministic function with required arguments. Verify tool name, JSON arguments, finish reason, parallel-call behavior if requested, and the follow-up message flow. Do not execute model-proposed tools as part of protocol verification.

## Service completion criteria

A service is ready only when the selected model reaches readiness, a representative request succeeds through the intended network boundary, authentication and denial paths behave as designed, response shape matches the actual client contract, resource use is within budget, and rollback is available.
