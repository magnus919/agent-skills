# Supervisor Pattern — Centralized Multi-Agent Routing

The supervisor pattern uses a dedicated routing node to coordinate specialist agents. Every message passes through the supervisor, which classifies intent and routes to the appropriate specialist. After the specialist responds, control returns to the supervisor for the next routing decision.

This pattern is the right choice when **accuracy matters more than latency**, domain boundaries are ambiguous, and you need a centralized audit trail of every routing decision.

## Architecture

```
[User] → [Supervisor] → [Billing Agent] → [Supervisor] → [Response]
                    ↘ [Tech Support] → ↗
                    ↘ [Account Mgmt] → ↗
```

The supervisor is a dedicated LLM node with **structured output** (`with_structured_output(RoutingDecision)`) — no regex, no string parsing, just typed routing decisions.

## Comparative Metrics

| Metric | Supervisor | Swarm |
|--------|------------|-------|
| Avg latency (single-domain) | ~4.2s | ~2.8s |
| Avg latency (handoff required) | ~9.1s | ~5.4s |
| LLM calls (single-domain) | 2 (route + specialist) | 1 (specialist only) |
| LLM calls (handoff required) | 4 (route×2 + specialist×2) | 2 (specialist×2) |
| Avg tokens per request | ~2,800 | ~1,900 |
| Routing accuracy | ~94% | ~91% |

## Implementation

### 1. Define State

```python
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState
import operator

class MultiAgentState(MessagesState):
    current_agent: str                           # which specialist is active
    resolution_notes: Annotated[list[str], operator.add]  # audit trail
    handoff_count: int                           # recursion guard
```

### 2. Define Routing Schema (Pydantic)

```python
from pydantic import BaseModel, Field

class RoutingDecision(BaseModel):
    next_agent: str = Field(
        description="Next agent: 'billing', 'tech_support', 'account', or 'DONE'"
    )
    reasoning: str = Field(description="Why this agent was chosen")
```

### 3. Create the Supervisor Node

```python
routing_llm = llm.with_structured_output(RoutingDecision)

def supervisor(state: MultiAgentState) -> dict:
    notes = "\n".join(state.get("resolution_notes", []))
    history_context = f"\n\nAlready resolved:\n{notes}" if notes else ""

    response = routing_llm.invoke([
        SystemMessage(
            content="You are a multi-agent supervisor. Analyze the conversation "
                    "and decide which specialist should handle the next step.\n\n"
                    "Available agents:\n"
                    "- billing: invoices, payments, discounts, pricing\n"
                    "- tech_support: technical issues, SSO, integrations, bugs\n"
                    "- account: plan changes, upgrades, account administration\n"
                    "- DONE: the customer's request has been fully addressed\n\n"
                    "Do NOT re-route to an agent that has already handled "
                    "its portion of the request." + history_context
        ),
        *state["messages"],
    ])
    return {"current_agent": response.next_agent}
```

### 4. Create Specialist Agents

Each specialist has a focused system prompt and domain-specific tools. Using `create_agent` from `langchain.agents`:

```python
from langchain.agents import create_agent

billing_agent = create_agent(
    llm,
    tools=[lookup_billing_info, apply_discount],
    system_prompt="You are a billing specialist. Help customers with invoices, "
           "payments, discounts, and plan pricing. "
           "Customer ID is 'C-1042' unless otherwise specified.",
)

tech_support_agent = create_agent(
    llm,
    tools=[diagnose_sso, check_system_status],
    system_prompt="You are a technical support specialist. Help customers "
           "diagnose and resolve technical issues.",
)

account_agent = create_agent(
    llm,
    tools=[lookup_account_details, update_plan],
    system_prompt="You are an account management specialist. Help customers "
           "with plan changes, upgrades, and account administration.",
)
```

### 5. Specialist Node Wrappers

```python
def billing_node(state: MultiAgentState) -> dict:
    result = billing_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Billing: {result['messages'][-1].content[:200]}"
        ],
    }

def tech_support_node(state: MultiAgentState) -> dict:
    result = tech_support_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Tech Support: {result['messages'][-1].content[:200]}"
        ],
    }

def account_node(state: MultiAgentState) -> dict:
    result = account_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Account: {result['messages'][-1].content[:200]}"
        ],
    }
```

### 6. Wire the Graph

```python
from langgraph.graph import StateGraph, START, END

def route_to_agent(state: MultiAgentState) -> str:
    agent = state.get("current_agent", "DONE")
    if agent == "DONE":
        return "end"
    return agent

builder = StateGraph(MultiAgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("billing", billing_node)
builder.add_node("tech_support", tech_support_node)
builder.add_node("account", account_node)

builder.add_edge(START, "supervisor")

builder.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "billing": "billing",
        "tech_support": "tech_support",
        "account": "account",
        "end": END,
    },
)

# Each specialist returns to supervisor
builder.add_edge("billing", "supervisor")
builder.add_edge("tech_support", "supervisor")
builder.add_edge("account", "supervisor")

supervisor_graph = builder.compile()
```

## Failure Modes

### Routing Loops
The supervisor routes to billing → billing responds → supervisor routes to billing again → repeats.

**Fix:** Include resolution notes in the supervisor's context so it can see what's already been addressed. The `resolution_notes` accumulator (with `operator.add` reducer) tracks what each specialist has done.

### Supervisor Bottleneck
Every interaction requires a routing LLM call — even when the intent is obvious ("I need to change my password" doesn't need a routing decision).

**Fix:** Add a fast-path classifier before the supervisor:

```python
FAST_PATH = {
    "password": "tech_support",
    "invoice": "billing",
    "upgrade": "account",
    "downgrade": "account",
}

def fast_path_or_supervisor(state: MultiAgentState) -> dict:
    last_msg = state["messages"][-1].content.lower()
    for keyword, agent in FAST_PATH.items():
        if keyword in last_msg:
            return {"current_agent": agent}
    return supervisor(state)
```

### Token Waste on Re-routing
The supervisor pattern doubles token spend on routing calls compared to swarm.

**Fix:** Track total tokens per pattern across sessions in LangSmith. If token costs exceed the value of the routing accuracy gain, consider switching to swarm.

## When to Use

- Routing accuracy is the most important metric
- Domain boundaries are ambiguous (billing vs account overlap)
- You need a centralized audit trail of every decision
- You're iterating on routing logic and want to change it in one place
- You have fewer than 5 specialists and latency is acceptable
