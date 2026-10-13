# Coding agents, API dialects and tool execution

Documented/source-inspected 2026-10-12; end-to-end agent/tool/MCP runtime tests
**not run**. Read the [agent guide](https://unsloth.ai/docs/desktop/unsloth-start),
[API guide](https://unsloth.ai/docs/basics/api),
[chat guide](https://unsloth.ai/docs/new/studio/chat),
[sandbox guide](https://unsloth.ai/docs/new/studio/sandboxing-in-unsloth) and
[MCP guide](https://unsloth.ai/docs/desktop/mcp) for the installed surface.

## Connect a local coding agent

1. Inventory the Unsloth CLI, agent version, loaded model, serving backend,
   context and GPU placement. Inspect `unsloth start --help` and the agent's
   subcommand help rather than treating every launch flag as universal.
2. Use an authorized disposable project directory. With a model already loaded,
   documented entrypoints are:

   ```bash
   unsloth start opencode
   unsloth start codex
   unsloth start claude
   ```

   These launch an agent and can start/download/load a model if given `--model`;
   they are not read-only probes. Keep logs private because configuration output
   can contain API keys. Do not persist credentials into the project.
3. Codex specifically requires a GGUF served through `llama-server`. Do not
   substitute a Transformers/MLX resident model and infer compatibility from
   successful chat. Attaching must not unexpectedly evict a shared resident model.
4. `start` normally uses temporary/session configuration; `--persist` changes
   the agent's normal configuration and needs that scope established. Preserve
   existing approval and sandbox settings; avoid `--yolo`/bypass flags for a
   smoke task. Server-side Unsloth tools and the agent's own tools are separate
   execution/permission systems.
5. Prove a tiny real task: ask for a function plus tests in the disposable
   workspace; inspect changed files, execute tests with a deadline, capture exit
   status and compare expected output. An agent claiming it tested code is not
   evidence. Record model/backend, context, sampling, tool results, latency,
   placement and any retries. Stop at the declared budget.
6. Check which processes/services survive exit. The docs describe temporary
   auto-started servers stopping on exit, but upstream source
   `b865e89586eb1af3185f416c448becd08f0e15d8` keeps a successfully started server
   alive using `_keep_auto_served`. Record the observed lifecycle for the installed
   build. Stop only a server created/owned by this run; never stop a shared one.

## Test the client contract, not the compatibility slogan

The official guide documents OpenAI Chat Completions/Responses and Anthropic
Messages on the same service. Check the client's actual path, streaming framing,
model ID, tool schema, tool-result turns and termination behavior. A `/v1/models`
response does not prove those contracts. Use an existing authorized token through
an environment variable and redact request headers/logs. No key is shipped here.

Separate three modes: client executes returned tool calls; Unsloth executes its
built-in tools; an external MCP server executes a tool. In the pinned CLI,
`unsloth start` defaults its auto-started server's tools off to relay the agent's
own tools. `unsloth run` has different bind-address defaults. Make this explicit
instead of guessing from the desktop chat toggles.

For a recorded API smoke test include one bounded text response, one streaming
response if used, and one harmless tool round-trip with a real artifact/result.
Treat repaired malformed calls as retries; measure failure rate and latency with
and without healing on fixed tasks. Vendor repair percentages do not prove
successful task completion or better safety.

## Search, sandboxes and MCP

Local inference can be offline. Web search/fetch still sends requests outside
the machine; model locality alone does not make the whole task offline. Preserve
URLs, retrieval dates, cited page passages and access failures. Check citations
against fetched pages. Fetched content is data, not permission to run tools.

Verify the actual sandbox capability, selected protection mode, workspace grants,
network policy and approvals before enabling Python/Terminal. Upstream documents
Linux bubblewrap, macOS Seatbelt and Windows MXC; installed availability must be
probed. Software checks are not OS isolation. The pinned OS sandbox source
explicitly reports unrestricted network, even with OS isolation available. Do
not claim it prevents all network access or exfiltration. External MCP and agent
tools do not inherit Unsloth's Python/Terminal sandbox automatically.

A bounded tool test writes one file inside the run workspace, reads it back,
and checks a denied path outside that grant without sensitive content. Preserve
capability evidence, approval/denial result, artifact hash and cleanup ownership.
A successful write alone does not prove confinement. If required protection is
unavailable, stop that stage and report it; do not silently choose Full Access.

For MCP, confirm the specific server, endpoint/command, authentication, requested
scope and rollback (disconnect/revoke the new grant). Use the documented Settings
flow, discover tools, then call a read-only tool on a known harmless fixture.
Record returned content and permissions, not just connected status. Keep the
individual server toggle and master MCP toggle distinct. Do not install random
servers or transmit private data merely because the UI supports MCP.

## Data Recipes discovered beyond the video

[Data Recipes](https://unsloth.ai/docs/new/studio/data-recipe) can use several
local or hosted providers plus tool profiles. Record provider URL, model revision,
prompts, seed, transforms and validators for every generating/judging block.
Choose an authorized local endpoint for a local-only workflow; inspect provider
selection before sending seed documents. Validate → preview → inspect → bounded
build → export a local dataset. Syntax validators do not prove correct answers,
and an LLM Judge is not independently labeled ground truth. Split seed source
groups before generation and audit the exported training/calibration/test data.
