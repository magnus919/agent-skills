"""Run with LangChain installed; the suite is offline and needs no API key."""

import pytest

pytest.importorskip("langchain.agents")

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from decision_middleware import DecisionUnavailable, make_agent


class ToolReadyFake(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def models(responses=None):
    return {
        "standard": ToolReadyFake(responses=responses or [AIMessage(content="standard reply")]),
        "specialist": ToolReadyFake(responses=[AIMessage(content="specialist reply")]),
    }


def invoke(agent, message="work", thread="one"):
    return agent.invoke({"messages": [HumanMessage(message)]}, {"configurable": {"thread_id": thread}})


def unavailable(_):
    raise DecisionUnavailable()


def test_route_is_sticky_and_a_new_thread_can_reclassify():
    seen = []
    def classify(text):
        seen.append(text)
        return "specialist" if text == "design" else "standard"

    agent = make_agent(models(), classify, unavailable, [])
    assert invoke(agent, "design")["messages"][-1].content == "specialist reply"
    assert invoke(agent, "small change")["route"] == "specialist"
    assert invoke(agent, "small change", "two")["messages"][-1].content == "standard reply"
    assert seen == ["design", "small change"]


@pytest.mark.parametrize("selector", [unavailable, lambda _: "invented", lambda _: []])
def test_invalid_or_unavailable_route_uses_approved_baseline(selector):
    assert invoke(make_agent(models(), selector, unavailable, []))["route"] == "standard"


@pytest.mark.parametrize(
    ("destination", "risk_result", "expected", "assessment_calls"),
    [
        ("sandbox", "clear", ["sample"], ["sample"]),
        ("sandbox", "review", [], ["sample"]),
        ("sandbox", None, [], ["sample"]),
        ("sandbox", "unavailable", [], ["sample"]),
        ("external", "clear", [], []),
    ],
)
def test_tool_boundary_separate_from_route(destination, risk_result, expected, assessment_calls):
    call = AIMessage(content="", tool_calls=[{
        "name": "save_draft", "id": "draft-1",
        "args": {"destination": destination, "text": "sample"},
    }])
    drafts, seen = [], []

    def assess(text):
        seen.append(text)
        if risk_result == "unavailable":
            raise DecisionUnavailable()
        return risk_result

    agent = make_agent(models([call, AIMessage(content="done")]), lambda _: "standard", assess, drafts)
    result = invoke(agent)
    tool_result = next(m for m in result["messages"] if isinstance(m, ToolMessage))
    assert (tool_result.status, drafts, seen) == (
        "success" if expected else "error", expected, assessment_calls
    )
