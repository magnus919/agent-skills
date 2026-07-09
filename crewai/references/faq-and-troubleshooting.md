# CrewAI FAQ and Troubleshooting

## Common Errors

**Q: Crew runs but produces no output?**
A: Check for delegation loops. Set `allow_delegation=False` and `max_iter=15` on agents.

**Q: Hierarchical crew doesn't work?**
A: `manager_llm` is required. Add `Crew(manager_llm=ChatOpenAI(model="gpt-4"))`. Without it, hierarchical mode fails silently.

**Q: Agent not calling tools?**
A: Ensure: (1) tool is added to agent's `tools` list, (2) tool has descriptive docstring, (3) tool uses type hints.

**Q: Tool error not caught?**
A: Tool failures don't raise exceptions. The task is marked as failed. Check task output for error messages.

**Q: Very long execution time?**
A: Sequential process with many agents. Each agent runs sequentially. Reduce agent count or use simpler tasks.

**Q: Token usage too high?**
A: Hierarchical mode — the manager processes all outputs. Use a cheaper model for `manager_llm`.

**Q: Memory not working across tasks?**
A: Set `memory=True` on the Crew level, not just individual agents.

**Q: Crew keeps running forever?**
A: Set `max_iter` on each agent (default is 15 but may need reducing).

## Installation

```bash
pip install crewai
# For built-in tools:
pip install crewai-tools
```
