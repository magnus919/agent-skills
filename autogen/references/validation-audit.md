# AutoGen Skill — API Validation Audit

**Checked:** 2026-10-06

**Pinned API:** `autogen-agentchat==0.7.5`, `autogen-ext==0.7.5`

**Python:** 3.10 or later
**Sources:** Microsoft's current AgentChat and package documentation; PyPI package metadata.

## Verified current API

| Claim | Evidence |
|---|---|
| `AssistantAgent` accepts a name, model client, and optional system message; use async `run()` or `run_stream()` | [Agent reference](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html) |
| `UserProxyAgent` represents a human and accepts `name`, `description`, and `input_func` | [Agent reference](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent) |
| `UserProxyAgent` is not the code executor and has no `human_input_mode` or `is_termination_msg` parameter | [Agent reference](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent) |
| `CodeExecutorAgent` accepts a `code_executor`; Docker and local executors are supplied by `autogen-ext` | [Agent reference](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.CodeExecutorAgent), [executor guide](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/command-line-code-executors.html) |
| Teams use `run()` / `run_stream()` and termination conditions | [Teams and agents guide](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html), [base API](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html) |
| Docker executor is installed with the `docker` extra; OpenAI model client with the `openai` extra | [Installation guide](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/installation.html), [executor guide](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/command-line-code-executors.html) |
| AgentChat requires Python 3.10 or newer; package version 0.7.5 is available | [PyPI metadata](https://pypi.org/project/autogen-agentchat/0.7.5/) |

## Legacy API boundary

`human_input_mode`, `is_termination_msg`, `code_executor` on `UserProxyAgent`, `initiate_chat()`, and `result.summary` belong to the separate `pyautogen` 0.2 API. They must not appear in examples importing `autogen_agentchat`. The current human participant is `UserProxyAgent(input_func=...)`; code execution belongs to `CodeExecutorAgent(code_executor=...)`.

## Offline runtime validation

`scripts/test_templates.py` runs against the pinned 0.7.5 packages with `ReplayChatCompletionClient`, a deterministic model client, a human-input double, and a safe executor double. It imports and runs each shipped template's `main()` function, checks conversation output and code-block dispatch, and exercises team result handling. It uses no API key, network model, or Docker daemon. This verifies local package/API compatibility; it is not a live model or Docker execution test.
