# AutoGen Skill — Research Validation Audit

**Date:** 2026-07-09
**Sources:** microsoft.github.io/autogen/stable

## Claims Verified Correct

| Claim | Source | Status |
|-------|--------|--------|
| `AssistantAgent` with `name`, `system_message`, `model_client` | autogen docs | ✓ |
| `UserProxyAgent` with `human_input_mode`, `code_executor` | autogen docs | ✓ |
| `RoundRobinGroupChat` for fixed-order conversation | autogen docs | ✓ |
| `SelectorGroupChat` with `model_client` for speaker selection | autogen docs | ✓ |
| Docker execution via `DockerCommandLineCodeExecutor` | autogen docs | ✓ |
| Local execution via `LocalCommandLineCodeExecutor` | autogen docs | ✓ |
| Cancellation via `CancellationToken` | autogen docs | ✓ |
| MCP tool integration via `McpWorkbench` | autogen docs | ✓ |

## Claims Updated by Source Audit

- **AssistantAgent** is explicitly documented as a "kitchen sink agent for prototyping" — the skill should note its prototyping nature
- **CodeExecutorAgent** is the v0.4 separate agent for code execution, splitting the role that UserProxyAgent filled in v0.2
- **AgentTool** wraps an entire agent as a tool callable by another agent — important pattern for agent composition
- **Streaming** uses `.run_stream()` with `async for message in stream`, not the older callback approach
- **v0.2->v0.4 migration**: UserProxyAgent in v0.2 becomes `AssistantAgent` + `CodeExecutorAgent` + `RoundRobinGroupChat` in v0.4

## Missing from Skill (Addressed in This Enrichment)

- v0.2 to v0.4 migration patterns
- AgentTool for agent-as-tool composition
- v0.4 streaming via `run_stream()`
- Three human_input_mode behaviors documented with examples
- Validation audit file
