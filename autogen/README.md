# AutoGen — Conversational Multi-Agent AI (Microsoft Research)

An expert-level skill for building **conversational multi-agent systems** with Microsoft's AutoGen framework. Unlike graph-based or role-based orchestration, AutoGen uses **agent-to-agent conversations** as the orchestration primitive.

## Why Install This Skill

When your agent loads this skill, it becomes an AutoGen expert who can:

- **Design agent topologies** — AssistantAgent, UserProxyAgent, GroupChat configurations
- **Build group chat systems** — RoundRobinGroupChat and SelectorGroupChat patterns
- **Implement nested chats** — agent-to-agent delegation for sub-tasks
- **Configure code execution** — Docker-safe code execution for LLM-generated code
- **Handle production concerns** — cancellation tokens, termination conditions, error recovery

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Quick-start guide, core paradigm explanation, and pattern selection |
| `references/` | Deep dives into agent types, group chat, nested chats, code execution, tool integration, and MCP support |

## Triggers

Load this skill when working with AutoGen, building multi-agent chat systems, or comparing agent frameworks. Use when you need conversation-driven agent orchestration.

## Framework Comparison

AutoGen differs from other frameworks in the portfolio: it's conversation-driven (vs LangGraph's graph topology), uses autonomous agent-to-agent messaging (vs CrewAI's explicit role-based crews), and has built-in group chat routing (vs PydanticAI's direct delegation).

## Requirements

Python 3.8+ with `autogen-agentchat` and `autogen-ext` packages.
