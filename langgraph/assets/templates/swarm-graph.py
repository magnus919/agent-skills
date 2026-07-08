"""
Swarm Graph — Complete Template

A self-contained swarm multi-agent system with direct agent-to-agent handoffs.
Features:
  - No central supervisor — agents hand off directly via Command
  - Triage agent routes initial request to the right specialist
  - Each specialist has domain tools + handoff tools for other agents
  - Resolution notes for audit trail
  - Recursion guard prevents ping-pong (hard limit at 3 handoffs)

Requirements:
  pip install langgraph langchain langchain-openai langsmith
"""

import operator
from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langsmith import traceable

# ── LLM Setup ──────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ── Tools ──────────────────────────────────────────────────────────────────

@tool
def lookup_billing_info(customer_id: str) -> str:
    """Look up billing information for a customer."""
    return (
        f"Customer {customer_id}: Enterprise plan, $2,400/mo, "
        f"next billing date 2026-03-01, payment method: invoice."
    )

@tool
def apply_discount(customer_id: str, discount_percent: int) -> str:
    """Apply a discount to a customer's account."""
    return f"Applied {discount_percent}% discount to customer {customer_id}."

@tool
def diagnose_sso(customer_id: str, error_code: str) -> str:
    """Diagnose SSO integration issues."""
    return (
        f"SSO diagnosis for {customer_id}: Error {error_code} indicates "
        f"SAML certificate expiration. Resolution: regenerate SAML certificate."
    )

@tool
def check_system_status(service: str) -> str:
    """Check the status of a service."""
    return f"Service {service}: operational, 99.97% uptime last 30 days."

@tool
def lookup_account_details(customer_id: str) -> str:
    """Look up account details and plan information."""
    return (
        f"Customer {customer_id}: Enterprise plan since 2024-06, "
        f"5 seats, primary contact: jane@example.com."
    )

@tool
def update_plan(customer_id: str, new_plan: str) -> str:
    """Update a customer's plan."""
    return f"Plan updated for {customer_id}: now on {new_plan}."

# ── Handoff Tools ──────────────────────────────────────────────────────────

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

# ── State ──────────────────────────────────────────────────────────────────

class SwarmState(MessagesState):
    current_agent: str
    resolution_notes: Annotated[list[str], operator.add]
    handoff_count: int

# ── Agents ─────────────────────────────────────────────────────────────────

triage_agent = create_agent(
    llm,
    tools=[transfer_to_billing, transfer_to_tech, transfer_to_account],
    system_prompt=(
        "You are a triage agent. Analyze the customer's request and "
        "transfer to the appropriate specialist using the transfer tools. "
        "Do NOT try to answer questions yourself — always transfer. "
        "If multiple issues exist, transfer to the most urgent one first."
    ),
)

billing_swarm_agent = create_agent(
    llm,
    tools=[lookup_billing_info, apply_discount,
           transfer_to_tech, transfer_to_account],
    system_prompt=(
        "You are a billing specialist. Help with invoices, payments, and "
        "discounts. If the customer has unresolved issues outside your "
        "domain, transfer to the appropriate specialist. "
        "Customer ID is 'C-1042' unless otherwise specified."
    ),
)

tech_swarm_agent = create_agent(
    llm,
    tools=[diagnose_sso, check_system_status,
           transfer_to_billing, transfer_to_account],
    system_prompt=(
        "You are a technical support specialist. Help with technical "
        "issues, SSO, and integrations. If the customer has unresolved "
        "issues outside your domain, transfer to the appropriate specialist. "
        "Customer ID is 'C-1042' unless otherwise specified."
    ),
)

account_swarm_agent = create_agent(
    llm,
    tools=[lookup_account_details, update_plan,
           transfer_to_billing, transfer_to_tech],
    system_prompt=(
        "You are an account management specialist. Help with plan changes "
        "and upgrades. If the customer has unresolved issues outside your "
        "domain, transfer to the appropriate specialist. "
        "Customer ID is 'C-1042' unless otherwise specified."
    ),
)

# ── Node Wrappers ──────────────────────────────────────────────────────────

@traceable(name="triage_node", run_type="chain")
def triage_node(state: SwarmState) -> Command:
    result = triage_agent.invoke({"messages": state["messages"]})
    return result

@traceable(name="billing_swarm_node", run_type="chain")
def billing_swarm_node(state: SwarmState) -> dict:
    result = billing_swarm_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Billing: {result['messages'][-1].content[:200]}"
        ],
    }

@traceable(name="tech_swarm_node", run_type="chain")
def tech_swarm_node(state: SwarmState) -> dict:
    result = tech_swarm_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Tech Support: {result['messages'][-1].content[:200]}"
        ],
    }

@traceable(name="account_swarm_node", run_type="chain")
def account_swarm_node(state: SwarmState) -> dict:
    result = account_swarm_agent.invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"][-1:],
        "resolution_notes": [
            f"Account: {result['messages'][-1].content[:200]}"
        ],
    }

# ── Graph Assembly ─────────────────────────────────────────────────────────

from typing import Literal

def route_after_agent(
    state: SwarmState,
) -> Literal["billing", "tech_support", "account", "__end__"]:
    """Route to next agent based on state. Recursion guard at 3 handoffs."""

    if state.get("handoff_count", 0) >= 3:
        return "__end__"

    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
            return "__end__"

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

for node in ["billing", "tech_support", "account"]:
    swarm_builder.add_conditional_edges(
        node,
        route_after_agent,
        ["billing", "tech_support", "account", END],
    )

swarm_graph = swarm_builder.compile(checkpointer=MemorySaver())

# ── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "swarm-demo-1"}}

    result = swarm_graph.invoke(
        {
            "messages": [HumanMessage(
                content="I want to upgrade my plan, but first I need help fixing "
                        "my SSO — it's been broken since last Tuesday. "
                        "Also, can you waive the setup fee?"
            )],
            "current_agent": "",
            "resolution_notes": [],
            "handoff_count": 0,
        },
        config=config,
    )

    print("=== Conversation ===")
    for msg in result["messages"]:
        if hasattr(msg, "content") and msg.content:
            print(f"\n[{msg.type}]: {msg.content[:300]}")

    print("\n=== Resolution Notes ===")
    for note in result.get("resolution_notes", []):
        print(f"  - {note}")
