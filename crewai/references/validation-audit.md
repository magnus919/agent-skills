# CrewAI Skill — Research Validation Audit

**Date:** 2026-07-09
**Sources:** docs.crewai.com

## Claims Verified Correct

| Claim | Source | Status |
|-------|--------|--------|
| Agent: role, goal, backstory, llm, tools, verbose, allow_delegation, max_iter | docs.crewai.com | ✓ |
| Task: description, expected_output, agent, tools, context, human_input, callback | docs.crewai.com | ✓ |
| Crew: agents, tasks, process, manager_llm, verbose, memory, cache, planning | docs.crewai.com | ✓ |
| Sequential process: tasks run in order | docs.crewai.com | ✓ |
| Hierarchical process: manager delegates and validates, requires manager_llm | docs.crewai.com | ✓ |
| max_iter default: 15 | docs.crewai.com | ✓ |
| @tool decorator with type hints | docs.crewai.com | ✓ |
| crewai-tools package for built-in tools | docs.crewai.com | ✓ |

## Claims Updated by Source Audit

- **Memory:** CrewAI v1.15+ uses a unified `Memory` class replacing separate short-term, long-term, entity, and external memory types. The skill mentioned `memory=True` without documenting the unified system.
- **Flows:** Event-driven with `@listen` decorator, state management via `@persist`, resumption via `restore_from_state_id`. The skill mentioned Flows in one sentence.

## Missing from Skill (Addressed in This Enrichment)

- Unified Memory class documentation
- Flows system: @listen decorator, state management, event-driven patterns
- Crew training patterns
