# Swarm Pattern — Direct Agent-to-Agent Handoffs

The swarm pattern eliminates the central supervisor. Agents hand off directly to each other using `Command` objects returned from handoff tools. When an agent calls a handoff tool, `Command(goto=target, graph=Command.PARENT)` tells LangGraph to navigate to a different node in the parent graph.

This pattern is the right choice when **latency is the primary constraint**, domain boundaries are clear, and agents rarely misroute on their own.

## Architecture

```
[User] → [Triage Agent] → [Billing Agent] → [Response]
                │                    │
                ├──→ [Tech Support] ─┘
                └──→ [Account Mgmt]
```

No central orchestrator. Each agent decides whether to handle the request itself or hand off to another specialist using a `Command`.

## Comparative Metrics

| Metric | Swarm | Supervisor |
|--------|-------|------------|
| Avg latency (single-domain) | ~2.8s | ~4.2s |
| Avg latency (handoff required) | ~5.4s | ~9.1s |
| LLM calls (single-domain) | 1 (specialist only) | 2 (route + specialist) |
| LLM calls (handoff required) | 2 (specialist×2) | 4 (route×2 + specialist×2) |
| Avg tokens per request | ~1,900 | ~2,800 |
| Routing accuracy | ~91% | ~94% |

## Implementation

### 1. Define State

```python
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState
import operator

class SwarmState(MessagesState):
    current_agent: str
    resolution_notes: Annotated[list[str], operator.add]
    handoff_count: int       # recursion guard — increment on each handoff
```

### 2. Create Handoff Tool Factory

The handoff tool returns a `Command` that tells LangGraph to navigate to a different node:

```python
from langgraph.types import Command
from langchain_core.tools import tool

def make_handoff_tool(target_agent: str, description: str):
    """Factory that creates a handoff tool for transferring to another agent."""

    @tool(f"transfer_to_{target_agent}")
    def handoff(reason: str) -> Command:
        """Transfer the conversation to another specialist agent."""
        return Command(
            goto=target_agent,
            update={"current_agent": target_agent},
            graph=Command.PARENT,
        )

    handoff.__doc__ = description
    return handoff
```

### 3. Create Handoff Tools

```python
transfer_to_billing = make_handoff_tool(
    "billing",
    "Transfer to the billing specialist for invoices, payments, or discounts.",
)
transfer_to_tech = make_handoff_tool(
    "tech_support",
    "Transfer to technical support for SSO, integrations, or system issues.",
)
transfer_to_account = make_handoff_tool(
    "account",
    "Transfer to account management for plan changes or upgrades.",
)
```

### 4. Create Agents with Handoff Tools

The **triage agent** has no domain tools — it only routes:

```python
from langchain.agents import create_agent

triage_agent = create_agent(
    llm,
    tools=[transfer_to_billing, transfer_to_tech, transfer_to_account],
    system_prompt="You are a triage agent. Analyze the customer's request and "
           "transfer to the appropriate specialist. Do not answer questions "
           "yourself — always transfer. If multiple issues exist, transfer "
           "to the most urgent one first.",
)
```

**Specialist agents** have domain tools PLUS handoff tools for other domains:

```python
billing_swarm_agent = create_agent(
    llm,
    tools=[lookup_billing_info, apply_discount,
           transfer_to_tech, transfer_to_account],
    system_prompt="You are a billing specialist. Help with invoices, payments, "
           "and discounts. If the customer has unresolved issues outside your "
           "domain, transfer to the appropriate specialist.",
)

tech_swarm_agent = create_agent(
    llm,
    tools=[diagnose_sso, check_system_status,
           transfer_to_billing, transfer_to_account],
    system_prompt="You are a technical support specialist. Help with technical "
           "issues, SSO, and integrations. If the customer has unresolved "
           "issues outside your domain, transfer to the appropriate specialist.",
)

account_swarm_agent = create_agent(
    llm,
    tools=[lookup_account_details, update_plan,
           transfer_to_billing, transfer_to_tech],
    system_prompt="You are an account management specialist. Help with plan "
           "changes and upgrades. If the customer has unresolved issues "
           "outside your domain, transfer to the appropriate specialist.",
)
```

### 5. Create Node Wrappers

```python
def triage_node(state: SwarmState) -> Command:
    result = triage_agent.invoke({"messages": state["messages"]})
    return result  # Command from the handoff tool

def billing_swarm_node(state: SwarmState) -> dict:
    result = billing_swarm_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Billing: {result['messages'][-1].content[:200]}"
        ],
    }

def tech_swarm_node(state: SwarmState) -> dict:
    result = tech_swarm_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Tech Support: {result['messages'][-1].content[:200]}"
        ],
    }

def account_swarm_node(state: SwarmState) -> dict:
    result = account_swarm_agent.invoke({"messages": state["messages"]})
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
from typing import Literal

def route_after_agent(
    state: SwarmState,
) -> Literal["billing", "tech_support", "account", "__end__"]:
    # If the last message is an AIMessage without tool_calls, we're done
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
            return "__end__"
    # Otherwise, continue with the current agent (handoff via Command)
    current = state.get("current_agent", "")
    if current in ("billing", "tech_support", "account"):
        return current
    return "__end__"

swarm_builder = StateGraph(SwarmState)

swarm_builder.add_node("triage", triage_node)
swarm_builder.add_node("billing", billing_swarm_node)
swarm_builder.add_node("tech_support", tech_swarm_node)
swarm_builder.add_node("account", account_swarm_node)

swarm_builder.add_edge(START, "triage")

# Each specialist can route to any other specialist or end
for node in ["billing", "tech_support", "account"]:
    swarm_builder.add_conditional_edges(
        node, route_after_agent,
        ["billing", "tech_support", "account", END],
    )

swarm_graph = swarm_builder.compile()
```

## Key Details

### Command-based Routing

The `Command` object is the key mechanism. When an agent calls a handoff tool, the tool returns `Command(goto=target_agent, graph=Command.PARENT)` which:
1. Updates `current_agent` in state
2. Tells LangGraph to navigate to the target node in the parent graph
3. Carries any additional state updates via `update=`

### Recursion Guard

The swarm pattern has no natural recursion limit. Two agents can ping-pong indefinitely. Add a handoff counter:

```python
from langgraph.types import Command

def make_handoff_tool(target_agent, description, max_handoffs=3):
    @tool(f"transfer_to_{target_agent}")
    def handoff(reason: str, _state: SwarmState = None) -> Command:
        """Transfer the conversation to another specialist agent."""
        # You'd need to access state — use ToolRuntime or inject via closure
        return Command(
            goto=target_agent,
            update={"current_agent": target_agent},
            graph=Command.PARENT,
        )
    handoff.__doc__ = description
    return handoff
```

Track `handoff_count` in state and check it in `route_after_agent` — after 3, force END.

### Context Propagation

When Agent A hands off to Agent B, the response from Agent A must be in the message history. The `Command.update` should carry the relevant messages. Without this, Agent B sees the original user message but has no context about what Agent A already did.

## Failure Modes

### Context Loss on Handoff
Agent A resolves part of the issue and hands off to Agent B. Agent B sees the original message but doesn't know what Agent A already did.

**Fix:** Ensure `Command.update` includes the resolution context. The `resolution_notes` accumulator is one approach; forwarding the last AIMessage is another.

### Swarm Ping-Pong
Agent A doesn't know the answer → hands off to Agent B. Agent B also doesn't know → hands off back to Agent A. Repeats until recursion limit.

**Fix:** Track `handoff_count` in state. Hard limit at 3, then escalate to human or fallback agent.

### Lost Messages During Handoff
The handoff tool returns a `Command(graph=Command.PARENT)`, but the specialist agent's internal tool-calling loop messages don't propagate to the parent graph.

**Fix:** Ensure your `Command.update` includes the relevant messages. LLMs expect tool calls to be paired with `ToolMessage` responses. If you break that pairing, the next agent sees malformed history.

## When to Use

- Latency is your primary constraint
- Domain boundaries are clear and agents rarely misroute
- Requests often span multiple domains (latency savings compound)
- You want agents to maintain conversational context through handoffs
- You have good per-agent evals to catch misroutes
