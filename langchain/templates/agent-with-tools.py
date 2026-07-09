#!/usr/bin/env python3
"""Agent with tool-calling using create_agent (v1.0+)."""
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Simulated results for: {query}"

model = ChatOpenAI(model="gpt-4o")
tools = [search_web]

agent = create_agent(
    model, tools,
    prompt="You are a research assistant. Use the search tool to answer questions."
)

# With persistence
config = {"configurable": {"thread_id": "session-1"}}
result = agent.invoke(
    {"messages": [("user", "Search for LangChain v1.0 features")]},
    config=config
)
print(result["messages"][-1].content)
