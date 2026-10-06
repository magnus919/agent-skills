#!/usr/bin/env python3
"""Chat between an assistant and a human represented by UserProxyAgent."""

import asyncio

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. Ask the user a question when useful.",
        model_client=model_client,
    )
    human = UserProxyAgent(
        name="human",
        description="A human participant who can answer the assistant.",
        input_func=lambda prompt: input(prompt),
    )
    team = RoundRobinGroupChat(
        [assistant, human],
        termination_condition=MaxMessageTermination(max_messages=4),
    )

    try:
        result = await team.run(task="What is AutoGen? Give a short explanation, then ask me one question.")
        for message in result.messages:
            print(f"{message.source}: {message.content}")
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
