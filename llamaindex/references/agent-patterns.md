# LlamaIndex Agent Patterns

## Agent Types

| Agent | Tool Calling | When to Use |
|-------|-------------|-------------|
| `FunctionAgent` | Native function calling API | Models with tool-calling support |
| `ReActAgent` | ReAct prompting pattern | Models without native tool support |

## Pattern 1: AgentWorkflow (Built-in Multi-Agent)

```python
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent

research_agent = FunctionAgent(
    name="ResearchAgent",
    description="Searches and records notes",
    system_prompt="You are a researcher. Hand off to WriteAgent when ready.",
    tools=[search_web, record_notes],
    can_handoff_to=["WriteAgent"],
)

write_agent = FunctionAgent(
    name="WriteAgent",
    description="Writes reports from notes",
    can_handoff_to=["ReviewAgent"],
)

workflow = AgentWorkflow(
    agents=[research_agent, write_agent],
    root_agent=research_agent.name,
    initial_state={"report_content": "Not written yet."},
)

response = await workflow.run(user_msg="Write a report on the history of the web...")
```

## Pattern 2: Orchestrator Agent (Sub-Agents as Tools)

Centralized control: one orchestrator calls sub-agents via tools.

```python
orchestrator = FunctionAgent(
    name="Orchestrator",
    system_prompt="You orchestrate research, writing, and review...",
    tools=[call_research_agent, call_write_agent, call_review_agent],
)
response = await orchestrator.run(user_msg="Write a report...")
```

## Pattern 3: Custom Planner (DIY Orchestration)

```python
# LLM outputs structured plan in XML/JSON
# Python code parses and executes
for step in parse_plan(llm_response):
    agent = agents[step.agent_name]
    result = await agent.run(user_msg=step.input)
```

## Streaming Events

AgentWorkflow emits five event types:

```python
handler = workflow.run(user_msg="Your query")
async for event in handler.stream_events():
    if isinstance(event, AgentStream):
        print(event.delta, end="")  # Real-time output
    elif isinstance(event, AgentOutput):
        print(f"{event.current_agent_name}: {event.response.content}")
```

## Known Bug: Agent Handoff

After handoff, the receiving agent may lose the user's original request because handoff messages push it out of ChatMemory.

**Fix**: Extend `FunctionAgent.take_step()`:

```python
class MyFunctionAgent(FunctionAgent):
    async def take_step(self, ctx, llm_input, tools, memory):
        last_msg = llm_input[-1].content if llm_input else ""
        if "handoff_result" in last_msg:
            for message in llm_input[::-1]:
                if message.role == MessageRole.USER:
                    llm_input.append(message)
                    break
        return await super().take_step(ctx, llm_input, tools, memory)
```

Also customize `handoff_output_prompt` with a `handoff_result` tag for reliable detection.
