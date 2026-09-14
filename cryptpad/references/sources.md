# Research evidence and maintenance

Reviewed 2026-09-14. Original guidance and example code in this skill are MIT licensed.
Upstream sources retain their own licenses; no upstream implementation is vendored.

## Primary sources

| Source | What it establishes |
|---|---|
| [Official API examples README](https://github.com/cryptpad/cryptpad-api-examples/blob/bebfa6ca5ef0f61d9d2fdeb267ac04ffdeaf9bae/README.md) | Browser API, configuration, save callbacks, generated/application-managed keys, view keys, concurrent key replacement and transient sessions |
| [API loader source](https://github.com/cryptpad/cryptpad/blob/9808cf25c1091d6cf532df13bf5a70ba332f8d4d/www/cryptpad-api.js) | Actual argument handling, iframe integration, callback dispatch, browser file fetch and compatibility paths |
| [HTTP worker source](https://github.com/cryptpad/cryptpad/blob/9808cf25c1091d6cf532df13bf5a70ba332f8d4d/lib/http-worker.js) | Public AMD config/instance routes and internal auth surface |
| [Architecture source](https://github.com/cryptpad/cryptpad/blob/9808cf25c1091d6cf532df13bf5a70ba332f8d4d/docs/ARCHITECTURE.md) | ChainPad, history and transport concepts; some details are historical |
| [Store experiment](https://github.com/cryptpad/cryptpad/blob/9808cf25c1091d6cf532df13bf5a70ba332f8d4d/scripts/api/testapi.js) | Source-level store access example, not a documented stable external SDK |
| [Developer guide](https://docs.cryptpad.org/en/dev_guide/index.html) | Development, database and code entry points |
| [Installation guide](https://docs.cryptpad.org/en/admin_guide/installation.html) | Main/sandbox origins, deployment, OnlyOffice assets, retention and maintenance |
| [User security guide](https://docs.cryptpad.org/en/user_guide/security.html) | User-facing security model and limits |
| [Release history](https://github.com/cryptpad/cryptpad/releases) | Version-dependent integration features and upgrade constraints |
| [2025 recap](https://blog.cryptpad.org/2026/02/16/cryptpad-overview-2025/) | Integration API scope and distinction from planned broader JavaScript access |

The API examples revision is `bebfa6ca5ef0f61d9d2fdeb267ac04ffdeaf9bae`.
The core source revision is `9808cf25c1091d6cf532df13bf5a70ba332f8d4d`; its package
version is 2026.5.1. Documentation pages displayed 2026.5.0 during research.
These are independently observed values, not a universal deployment version.

## Revalidation procedure

1. Identify the target release and compare its loader against the examples contract.
2. Recheck embedding policy, supported file types, callbacks and view-key behavior.
3. Recheck source-level APIs before any headless integration; do not treat experiments
   or a CommonJS export as proof of browser-free support.
4. Run the offline tests, then the integration-plan acceptance checks in a disposable
   authorized document. Record actual results separately from proposed tests.

## Evidence scope

The Python tests exercise the CLI and the JavaScript adapter contract (when Node is installed).
They do not start CryptPad, authenticate, validate browser policies, or provide encrypted
application storage. Eval manifests are representative output-quality cases, not executed
agent benchmark results. Trigger-query labels have been manually checked against the skill's
positive/negative routing boundary; they are not measured harness activation rates.

### Observed discovery smoke test

On 2026-09-14, `probe --origin https://cryptpad.fr` returned recognized config and
integration-loader resources. Its public config reported embedding enabled, sandbox origin
`https://sandbox.cryptpad.info`, and WebSocket URL `wss://api.cryptpad.fr/cryptpad_websocket`.
These are dated observations, not pinned defaults; discover the actual target each time.
No document was opened or changed, and no browser collaboration or durable-save result is
claimed by this smoke test.
