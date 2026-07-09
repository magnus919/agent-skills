#!/usr/bin/env python3
"""Agent with Docker code execution."""

import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    async with DockerCommandLineCodeExecutor(work_dir="coding") as executor:
        assistant = AssistantAgent(name="assistant", model_client=model_client,
                                   system_message="Write Python code to solve problems.")
        proxy = UserProxyAgent(name="proxy", code_executor=executor,
                               human_input_mode="NEVER")

        team = RoundRobinGroupChat([assistant, proxy])
        result = await team.run(task="Calculate pi to 10 decimal places using Python")
        print(result.messages[-1].content)

asyncio.run(main())
