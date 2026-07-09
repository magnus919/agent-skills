# LangChain Architecture

## Package Structure

| Package | Purpose |
|---------|---------|
| `langchain-core` | Base abstractions: Runnable, prompts, messages, LLMs, tools |
| `langchain` | Meta-package with prebuilt chains, agents, retrieval |
| `langchain-community` | Third-party integrations (optional deps) |
| `langchain-openai` | OpenAI/ChatOpenAI wrapper |
| `langchain-anthropic` | Anthropic Claude wrapper |
| `langchain-google` | Google Gemini wrapper |
| `langchain-mcp-adapters` | MCP server tool integration |

## The Runnable Protocol

Every LangChain component implements `Runnable`, a standardized protocol enabling:

```
chain = prompt | model | parser
```

All Runnables support `invoke`, `ainvoke`, `stream`, `batch`, and `astream_events`.

## v1.0 Changes (October 2025)

- Agents now run on LangGraph runtime via `create_agent`
- AgentExecutor in maintenance mode until Dec 2026
- LCEL is the sole recommended chain composition method
- Legacy `LLMChain` fully deprecated
- Enhanced streaming API with event types

## Installation

```bash
pip install langchain langchain-openai python-dotenv
# For specific integrations:
pip install langchain-anthropic langchain-google
pip install langchain-community
pip install langchain-mcp-adapters
```

Requires Python 3.10+. Python 3.11+ recommended.
