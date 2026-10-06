#!/usr/bin/env python3
"""Group chat with RoundRobin speaker selection."""

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    try:
        researcher = AssistantAgent(name="researcher", model_client=model_client,
                                    system_message="You research and find information.")
        analyst = AssistantAgent(name="analyst", model_client=model_client,
                                 system_message="You analyze findings for insights.")
        writer = AssistantAgent(name="writer", model_client=model_client,
                                system_message="You write clear summaries.")

        team = RoundRobinGroupChat(
            [researcher, analyst, writer],
            termination_condition=MaxMessageTermination(max_messages=6),
        )
        result = await team.run(task="Research and report on AI agents")
        for message in result.messages:
            print(f"{message.source}: {message.content}")
    finally:
        await model_client.close()

asyncio.run(main())
