---
name: autogen
description: >-
  Build conversational multi-agent systems with Microsoft AutoGen. AssistantAgent,
  UserProxyAgent, GroupChat, code execution, nested chats, cancellation tokens, tool
  integration, and MCP support. Use when building conversation-driven multi-agent systems
  or comparing agent frameworks. Do not use this skill for unrelated requests; route to
  the nearest named specialist.
license: MIT
metadata:
  author: Magnus Hedemark
  version: 1.2.0
  source: https://microsoft.github.io/autogen
---

# AutoGen Expert Skill

This skill targets the AutoGen AgentChat 0.7.5 API on Python 3.10+. AutoGen (by Microsoft Research) is a framework for **conversational multi-agent AI**. Unlike LangGraph's explicit graph topology or CrewAI's role-based crews, AutoGen uses **agent-to-agent conversations as the orchestration primitive**. Agents communicate through structured chat, with built-in patterns for group chat routing, human input, and code execution.

## Core Paradigm

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    model_client=model_client,
)
```

> **Role split in AgentChat 0.7.5:** `UserProxyAgent` represents a human and obtains replies through `input_func`. `CodeExecutorAgent` executes code blocks using a `CodeExecutor`. They are separate agents; neither accepts the legacy `human_input_mode` option.

## Core Principles

1. **Conversations are the orchestration primitive.** Agents send messages, receive replies, and the conversation structure determines the workflow.
2. **Keep human input and code execution separate.** Use `UserProxyAgent` for a human participant; use `CodeExecutorAgent` with a `CodeExecutor` for code.
3. **GroupChat routes between agents.** RoundRobinGroupChat cycles fixed-order. SelectorGroupChat uses an LLM to pick the next speaker.
4. **Nested chats delegate work.** An agent can spawn a sub-conversation between specialist agents and return the result.
5. **Docker is the safe code execution mode.** Local code execution (`LocalCommandLineCodeExecutor`) runs LLM-generated code on your machine — use Docker in production.
6. **Cancellation tokens stop runaway agents.** Always pass `CancellationToken` for long-running tasks.

## Where to Start

| You already have... | Start here |
|---|---|
| Nothing — exploring AutoGen | Create an assistant chat or a team with a human `UserProxyAgent` |
| Agents that need to coordinate | Build a GroupChat with multiple agents |
| Agents that need code execution | Configure Docker code executor |
| A complex multi-step task | Use nested chats for sub-tasks |

## Quick Reference

| Task | Approach | Reference |
|------|----------|-----------|
| Human-in-the-loop chat | AssistantAgent + UserProxyAgent | `references/agent-types.md` |
| Multi-agent group | GroupChat with RoundRobinGroupChat | `references/group-chat.md` |
| Code execution | DockerCommandLineCodeExecutor | `references/code-execution.md` |
| Tool integration | `register_function()` or @tool | `references/tool-integration.md` |
| Nested chat | `AgentTool` or a team run from a tool | `references/conversation-patterns.md` |
| Cancellation | `CancellationToken` | `references/conversation-patterns.md` |
| MCP tools | `McpWorkbench` | `references/tool-integration.md` |

## Framework Routing Guide

| Scenario | Reach for | Why |
|----------|-----------|-----|
| Conversation-driven multi-agent | **AutoGen** | Native agent-to-agent chat as orchestration |
| Role-based multi-agent teams | **CrewAI** | Role/Goal/Backstory is the native abstraction |
| State-machine multi-agent | **LangGraph** | Graph topology, subgraphs, human-in-the-loop |
| Chain/agent composition | **LangChain** | LCEL pipe operator for general chains |

## Reference Files

| Reference | Load when | File |
|-----------|-----------|------|
| Agent Types | AssistantAgent, UserProxyAgent | `references/agent-types.md` |
| Conversation Patterns | Send/receive, nested chats, cancellation | `references/conversation-patterns.md` |
| Group Chat | RoundRobin, Selector, MagenticOne | `references/group-chat.md` |
| Code Execution | Docker, local, cancellation tokens | `references/code-execution.md` |
| Tool Integration | register_function, @tool, MCP integration | `references/tool-integration.md` |
| v0.4 Migration | v0.2->v0.4 migration, AgentTool, streaming, termination | `references/v04-migration.md` |
| Validation Audit | Research validation of all API claims | `references/validation-audit.md` |
| FAQ & Troubleshooting | Common errors and fixes | `references/faq-and-troubleshooting.md` |

Install the exact package versions used by the templates with `python -m pip install -r requirements.txt` from this skill directory. The code-execution example uses Docker and requires a working Docker daemon.

## Templates

| Template | When to use | File |
|----------|-------------|------|
| Two-Agent Chat | Assistant + human input | `templates/two-agent-chat.py` |
| Group Chat | Multi-agent team with speaker routing | `templates/group-chat.py` |
| Code Execution Agent | Assistant + Docker-backed code executor | `templates/code-execution.py` |

## Troubleshooting

| Symptom | Likely cause | Fix | Reference |
|---------|-------------|-----|-----------|
| Agent loops forever | No team termination condition | Add a `TerminationCondition` such as `MaxMessageTermination` | `references/conversation-patterns.md` |
| Code execution fails | Docker not running | Start Docker or use LocalCommandLineCodeExecutor | `references/code-execution.md` |
| Nested chat never returns | Cancellation token not passed | Pass `CancellationToken` with timeout | `references/conversation-patterns.md` |
| v0.2 code doesn't work | v0.4 API changed | Follow migration guide | `references/faq-and-troubleshooting.md` |
| GroupChat speaker selection loops | SelectorGroupChat with no clear next | Use RoundRobinGroupChat for fixed order | `references/group-chat.md` |
| UserProxyAgent waits for input | It is a human participant and its `input_func` is waiting | Supply an appropriate input function or use an automated agent | `references/agent-types.md` |

## When NOT to Use AutoGen

- Simple single-agent task — overkill, use direct API call
- Need fine-grained graph control — use LangGraph
- Need role-based teams with fixed processes — use CrewAI
- Need chain composition — use LangChain LCEL
