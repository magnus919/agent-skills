"""Offline API smoke tests for the pinned AutoGen template dependencies."""

import asyncio
import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[2]
SKILL_ROOT = Path(__file__).resolve().parents[1]
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


@unittest.skipUnless(HAS_AUTOGEN, "install autogen/requirements.txt to run template tests")
class TemplateEntrypointTests(unittest.TestCase):
    def load_template(self, filename):
        path = SKILL_ROOT / "templates" / filename
        spec = importlib.util.spec_from_file_location(f"template_{path.stem.replace('-', '_')}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def fake_model_factory(self, completions):
        from autogen_ext.models.replay import ReplayChatCompletionClient

        client = ReplayChatCompletionClient(completions)
        return lambda **_kwargs: client, client

    def test_two_agent_template_executes_with_fake_model_and_human_input(self):
        from autogen_agentchat.agents import UserProxyAgent

        module = self.load_template("two-agent-chat.py")
        model_factory, model_client = self.fake_model_factory(
            ["AutoGen connects agents through messages.", "A useful next step is to try a small team."]
        )

        async def fake_input(_prompt, _cancellation_token=None):
            return "Show me a simple example."

        def user_proxy_with_fake_input(*args, **kwargs):
            return UserProxyAgent(*args, **{**kwargs, "input_func": fake_input})

        output = io.StringIO()
        try:
            with patch.object(module, "OpenAIChatCompletionClient", model_factory), patch.object(
                module, "UserProxyAgent", user_proxy_with_fake_input
            ), contextlib.redirect_stdout(output):
                asyncio.run(module.main())
        finally:
            asyncio.run(model_client.close())

        self.assertIn("assistant: AutoGen connects agents through messages.", output.getvalue())
        self.assertIn("human: Show me a simple example.", output.getvalue())

    def test_code_execution_template_uses_agent_and_safe_executor_double(self):
        from autogen_core.code_executor import CodeBlock, CodeExecutor, CodeResult

        module = self.load_template("code-execution.py")

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
                return CodeResult(exit_code=0, output="3.1415926536\n")

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                await self.stop()

        executor = SafeExecutor()
        model_factory, model_client = self.fake_model_factory(
            ["```python\nprint(3.1415926536)\n```", "The result is 3.1415926536."]
        )
        output = io.StringIO()
        try:
            with patch.object(module, "OpenAIChatCompletionClient", model_factory), patch.object(
                module, "DockerCommandLineCodeExecutor", lambda **_kwargs: executor
            ), patch("builtins.input", return_value="y"), contextlib.redirect_stdout(output):
                asyncio.run(module.main())
        finally:
            asyncio.run(model_client.close())

        self.assertEqual(executor.received, [CodeBlock(code="print(3.1415926536)\n", language="python")])
        self.assertIn("code_executor: 3.1415926536", output.getvalue())

    def test_group_chat_template_executes_with_replay_client(self):
        module = self.load_template("group-chat.py")
        model_factory, model_client = self.fake_model_factory(
            ["Facts gathered.", "The key pattern is delegation.", "AutoGen supports conversations.",
             "A second finding.", "This confirms the pattern.", "Teams provide the orchestration."]
        )
        output = io.StringIO()
        try:
            with patch.object(module, "OpenAIChatCompletionClient", model_factory), contextlib.redirect_stdout(output):
                asyncio.run(module.main())
        finally:
            asyncio.run(model_client.close())

        self.assertIn("researcher: Facts gathered.", output.getvalue())
        self.assertIn("writer:", output.getvalue())


if __name__ == "__main__":
    unittest.main()
