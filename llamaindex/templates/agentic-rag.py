#!/usr/bin/env python3
"""
Multi-source RAG with agent orchestration.
Demonstrates pattern 2: orchestrator agent with sub-agents as tools.
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-4o")

# --- Build query engines for different data sources ---
product_docs = SimpleDirectoryReader("./data/products").load_data()
product_index = VectorStoreIndex.from_documents(product_docs)
product_engine = product_index.as_query_engine(similarity_top_k=3)

support_tickets = SimpleDirectoryReader("./data/support").load_data()
support_index = VectorStoreIndex.from_documents(support_tickets)
support_engine = support_index.as_query_engine(similarity_top_k=3)

# --- Wrap as tools ---
product_tool = QueryEngineTool.from_defaults(
    query_engine=product_engine,
    name="product_search",
    description="Search product documentation for specifications and features.",
)

support_tool = QueryEngineTool.from_defaults(
    query_engine=support_engine,
    name="support_search",
    description="Search support tickets for known issues and solutions.",
)

# --- Agent with tools ---
agent = FunctionAgent(
    name="SupportAgent",
    system_prompt=(
        "You are a technical support agent. Use product_search for product info "
        "and support_search for known issues. Answer concisely based on the data."
    ),
    tools=[product_tool, support_tool],
)

# --- Run ---
response = await agent.run(
    user_msg="What are the known issues with the API rate limiting feature?"
)
print(f"Answer: {response}")
