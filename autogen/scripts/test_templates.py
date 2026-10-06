"""Offline API smoke tests for the pinned AutoGen template dependencies."""

import asyncio
import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
HAS_AUTOGEN = all(importlib.util.find_spec(package) for package in ("autogen_agentchat", "autogen_ext"))


@unittest.skipUnless(HAS_AUTOGEN, "install autogen/requirements.txt to run API smoke tests")
class TemplateSmokeTests(unittest.TestCase):
    def test_human_chat_runs_with_replay_client_and_input_double(self):
        from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
        from autogen_agentchat.messages import TextMessage
        from autogen_core import CancellationToken
        from autogen_ext.models.replay import ReplayChatCompletionClient

        async def run():
            async def fake_input(_prompt, _cancellation_token=None):
                return "That helps."

            model_client = ReplayChatCompletionClient(["AutoGen is a multi-agent framework."])
            assistant = AssistantAgent("assistant", model_client=model_client)
            human = UserProxyAgent("human", input_func=fake_input)
            result = await assistant.run(task="What is AutoGen?")
            human_response = await human.on_messages(
                [TextMessage(content="Would you like an example?", source="assistant")],
                cancellation_token=CancellationToken(),
            )
            await model_client.close()
            return result, human_response

        result, human_response = asyncio.run(run())
        self.assertIn("multi-agent framework", result.messages[-1].content)
        self.assertEqual(human_response.chat_message.content, "That helps.")

    def test_code_executor_agent_runs_with_safe_executor_double(self):
        from autogen_agentchat.agents import ApprovalResponse, AssistantAgent, CodeExecutorAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_core.code_executor import CodeBlock, CodeExecutor, CodeResult
        from autogen_ext.models.replay import ReplayChatCompletionClient

        class SafeExecutor(CodeExecutor):
            def __init__(self):
                self.received = []

            async def start(self):
                pass

            async def stop(self):
                pass

            async def restart(self):
                pass

            async def execute_code_blocks(self, code_blocks, cancellation_token):
                self.received.extend(code_blocks)
                return CodeResult(exit_code=0, output="2\n")

        async def run():
            model_client = ReplayChatCompletionClient(["```python\nprint(1 + 1)\n```"])
            executor = SafeExecutor()
            assistant = AssistantAgent("assistant", model_client=model_client)
            code_agent = CodeExecutorAgent(
                "code_executor",
                code_executor=executor,
                approval_func=lambda _request: ApprovalResponse(approved=True, reason="safe test double"),
            )
            team = RoundRobinGroupChat(
                [assistant, code_agent],
                termination_condition=MaxMessageTermination(max_messages=3),
            )
            result = await team.run(task="Calculate 1 + 1 using Python.")
            await model_client.close()
            return result, executor

        result, executor = asyncio.run(run())
        self.assertEqual(executor.received, [CodeBlock(code="print(1 + 1)\n", language="python")])
        self.assertTrue(any(message.source == "code_executor" for message in result.messages))


if __name__ == "__main__":
    unittest.main()
