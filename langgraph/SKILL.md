---
name: langgraph
description: >-
  Build multi-agent AI systems with LangGraph — the low-level orchestration
  framework for stateful, graph-based agent workflows. Covers supervisor, swarm,
  and hierarchical multi-agent patterns; subgraph composition; state management
  (checkpointers/stores); persistence; evals; and production debugging. Reach
  for this when designing agent architectures that need cycles, conditional
  branching, parallel execution, or human-in-the-loop patterns.
license: MIT
metadata:
  source: LangGraph by LangChain Inc — https://langchain.com/langgraph
  spec-version: "1.0"
---

# LangGraph

LangGraph is LangChain's low-level orchestration framework for building stateful, long-running, multi-agent AI workflows using directed graph architectures (inspired by Pregel/Beam and NetworkX). It models agents as **nodes** in a graph, with **edges** controlling flow — enabling cycles, conditional branching, parallel execution, human-in-the-loop, and subgraph composition that linear chains cannot express.

This skill covers all major patterns for building and deploying LangGraph systems: core graph architecture, the three canonical multi-agent patterns (supervisor, swarm, hierarchical), persistence and state management, production debugging, and evaluation methodology.

## When to Reach For This

| Context | What to load |
|---------|-------------|
| Building a new LangGraph workflow from scratch | `references/architecture.md` — core concepts first |
| Designing a multi-agent routing system | `references/multi-agent-supervisor.md` or `references/multi-agent-swarm.md` — compare patterns |
| Composing nested agent teams | `references/multi-agent-hierarchical.md` — subgraph composition |
| Adding persistence, interrupts, or long-term memory | `references/persistence.md` — checkpointers and stores |
| Deploying to production or debugging failures | `references/production.md` — deployment, observability, failure modes |
| Setting up eval pipelines for routing accuracy | `references/evals.md` — evaluation methodology |
| Diagnosing a specific failure (loop, context loss, crash) | `references/troubleshooting.md` — known failure modes |

## Pattern Selection Guide

| Your constraint | Prefer | Why |
|----------------|--------|-----|
| Routing accuracy > latency | **Supervisor** | Centralized routing node, focused prompt: ~94% accuracy |
| Latency is primary constraint | **Swarm** | Direct agent-to-agent handoffs, ~40% fewer LLM calls |
| Clear domain boundaries | **Swarm** | Agents rarely misroute, handoffs are crisp |
| Ambiguous domain boundaries | **Supervisor** | Overlapping concerns resolved by dedicated router |
| < 3 distinct domains | **Skip multi-agent** | A specialized single agent is simpler |
| Multi-domain requests common | **Swarm** | Latency savings compound across handoffs |
| Need centralized audit trail | **Supervisor** | Every routing decision visible in traces |
| Nested team structures | **Hierarchical** | Subgraphs as nodes, each team self-contained |

## Core Primitives

LangGraph uses two APIs:

| API | When to use | Pattern |
|-----|-------------|---------|
| **Graph API** (`StateGraph`) | Full control over graph structure, conditional edges, subgraphs | `add_node()` + `add_edge()`/`add_conditional_edges()` |
| **Functional API** (`@task` + `@entrypoint`) | Simpler linear workflows, less boilerplate | Decorator-based, Pythonic |

Both APIs produce the same compiled graph — choose based on how much control you need.

## Key Gotchas

- **Subgraph persistence defaults to per-invocation** — each subgraph call starts fresh. Set `checkpointer=True` for per-thread memory, `checkpointer=False` for fully stateless.
- **Per-thread subgraphs cannot run in parallel** — same-namespace checkpoint conflicts. Use `ToolCallLimitMiddleware` or disable parallel tool calls.
- **The supervisor bottleneck** — every interaction requires a routing LLM call, even for obvious intents. Add a fast-path classifier (keyword matching or small model) for unambiguous requests.
- **Swarm ping-pong** — no natural recursion guard. Track `handoff_count` in state and hard-limit at 3, then escalate to human or fallback agent.
- **Lost messages on handoff** — `Command.update` must include paired messages from the specialist's tool-calling loop, or the next agent sees malformed history.
- **State access from parent to subgraph** — subgraphs manage their own checkpoint namespace. Use Store for cross-graph-boundary data.
- **Checkpoint bloat** — long conversations accumulate checkpoints. Prune periodically or set retention policies on DB-backed checkpointers.
- **No auto-load-on-install** — skills aren't auto-discovered at session start by name mention. The agent must explicitly call `skill_view(name='langgraph')` to load this skill.

## Reference Files

| File | Load when |
|------|-----------|
| `references/architecture.md` | You need to understand LangGraph core concepts: graph structure, nodes, edges, state, the two APIs, and basic agent loop construction. Read this first if you're new to LangGraph. |
| `references/multi-agent-supervisor.md` | You're designing a supervisor-based multi-agent system with a central routing node. Contains architecture, structured output routing, specialist wrappers, and full code examples. |
| `references/multi-agent-swarm.md` | You're designing a swarm-based multi-agent system with direct agent-to-agent handoffs. Contains handoff tool patterns, Command-based routing, and comparative metrics vs supervisor. |
| `references/multi-agent-hierarchical.md` | You're composing nested agent teams using subgraphs. Covers subgraph wiring (shared vs different state schemas), persistence modes, namespace isolation, and hierarchical team structures. |
| `references/persistence.md` | You're adding checkpointer-based short-term memory or store-based long-term memory. Covers per-invocation vs per-thread vs stateless modes, checkpoint backends, and cross-thread memory patterns. |
| `references/production.md` | You're deploying a LangGraph system to production. Covers Agent Server deployment, LangSmith observability, streaming patterns, and common production failure modes with fixes. |
| `references/evals.md` | You're setting up evaluation pipelines for multi-agent systems. Covers routing accuracy, resolution coverage, LangSmith eval datasets, and LLM-as-judge evaluators. |
| `references/troubleshooting.md` | You're debugging a specific LangGraph failure. Covers routing loops, context loss, checkpointer conflicts, token waste, and state inspection techniques. |

## Scripts

| Script | What it does |
|--------|-------------|
| `scripts/lg-supervisor-scaffold.py` | Generates a complete supervisor pattern project with state schema, routing agent, specialist nodes, and graph assembly |
| `scripts/lg-swarm-scaffold.py` | Generates a complete swarm pattern project with handoff tools, triage agent, specialist agents, and conditional routing |
| `scripts/lg-eval-generator.py` | Generates evaluation datasets and runs LangSmith evaluators for routing accuracy and resolution coverage |
