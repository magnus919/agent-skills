"""Offline example: route once per thread and gate a synthetic draft tool."""

from typing import Literal

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

Tier = Literal["standard", "specialist"]


class RoutingState(AgentState, total=False):
    route: Tier


class DecisionUnavailable(Exception):
    """Adapter's timeout/unavailability signal."""


class ThreadRouter(AgentMiddleware):
    state_schema = RoutingState

    def __init__(self, models, select):
        super().__init__()
        self.models = models
        self.select = select

    def before_agent(self, state, runtime):
        if state.get("route") in self.models:
            return None
        first = next((m for m in state["messages"] if isinstance(m, HumanMessage)), None)
        try:
            candidate = self.select(first.content) if first and isinstance(first.content, str) else None
        except DecisionUnavailable:
            candidate = None
        return {"route": candidate if candidate in ("standard", "specialist") else "standard"}

    def wrap_model_call(self, request, handler):
        return handler(request.override(model=self.models[request.state["route"]]))


class DraftGate(AgentMiddleware):
    def __init__(self, assess):
        super().__init__()
        self.assess = assess

    def wrap_tool_call(self, request, handler):
        call = request.tool_call
        if call["name"] != "save_draft":
            return handler(request)
        args = call["args"]
        text = args.get("text")
        # Deterministic, illustrative boundary. The classifier sees only the
        # relevant argument and cannot open a different destination.
        if args.get("destination") == "sandbox" and isinstance(text, str) and text.strip():
            try:
                if self.assess(text) == "clear":
                    return handler(request)
            except DecisionUnavailable:
                pass
        # This reply does not enqueue a review or claim an effect.
        return ToolMessage(
            content="Draft not saved. Human review required before proceeding.",
            tool_call_id=call["id"],
            status="error",
        )


def make_agent(models, select, assess, drafts):
    @tool
    def save_draft(destination: str, text: str) -> str:
        """Save a synthetic draft into the example's in-memory sandbox."""
        drafts.append(text)
        return "Draft saved."

    return create_agent(
        models["standard"],
        tools=[save_draft],
        middleware=[ThreadRouter(models, select), DraftGate(assess)],
        checkpointer=InMemorySaver(),
    )


if __name__ == "__main__":
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    class ToolReadyFake(FakeMessagesListChatModel):
        def bind_tools(self, tools, **kwargs):
            return self

    models = {
        "standard": ToolReadyFake(responses=[AIMessage(content="Standard route")]),
        "specialist": ToolReadyFake(responses=[AIMessage(content="Specialist route")]),
    }
    agent = make_agent(models, lambda _: "specialist", lambda _: "review", [])
    result = agent.invoke(
        {"messages": [HumanMessage("Review this design")]},
        {"configurable": {"thread_id": "demo"}},
    )
    print(result["route"], result["messages"][-1].content)
