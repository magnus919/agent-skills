#!/usr/bin/env python3
"""Group chat with RoundRobin speaker selection."""

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    researcher = AssistantAgent(name="researcher", model_client=model_client,
                                system_message="You research and find information.")
    analyst = AssistantAgent(name="analyst", model_client=model_client,
                             system_message="You analyze findings for insights.")
    writer = AssistantAgent(name="writer", model_client=model_client,
                            system_message="You write clear summaries.")

    team = RoundRobinGroupChat([researcher, analyst, writer])
    result = await team.run(task="Research and report on AI agents")
    print(result.messages[-1].content)

asyncio.run(main())
