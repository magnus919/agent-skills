#!/usr/bin/env python3
"""Run an assistant and Docker-backed CodeExecutorAgent as a bounded team."""

import asyncio

from autogen_agentchat.agents import ApprovalRequest, ApprovalResponse, AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient


def approve_code(request: ApprovalRequest) -> ApprovalResponse:
    print("Code proposed for Docker execution:\n")
    print(request.code)
    answer = input("Run this code? [y/N] ").strip().lower()
    approved = answer in {"y", "yes"}
    return ApprovalResponse(approved=approved, reason="Approved by the operator" if approved else "Declined")


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    try:
        async with DockerCommandLineCodeExecutor(work_dir="coding") as executor:
            assistant = AssistantAgent(
                name="assistant",
                model_client=model_client,
                system_message="Solve the task with a short Python code block when calculation is useful.",
            )
            code_executor = CodeExecutorAgent(
                name="code_executor",
                code_executor=executor,
                approval_func=approve_code,
            )
            team = RoundRobinGroupChat(
                [assistant, code_executor],
                termination_condition=MaxMessageTermination(max_messages=4),
            )
            result = await team.run(task="Calculate pi to 10 decimal places using Python.")
            for message in result.messages:
                print(f"{message.source}: {message.content}")
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
