#!/usr/bin/env python3
"""Two-agent chat with AssistantAgent and UserProxyAgent."""

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    model_client=model_client,
)

proxy = UserProxyAgent(
    name="proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content", "") or ""),
)

result = proxy.initiate_chat(assistant, message="What is AutoGen?", max_turns=2)
print(result.summary)
