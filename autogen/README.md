# AutoGen — Build conversational multi-agent systems

Give your agent practical guidance for Microsoft's AgentChat framework, including teams, human input, code execution, tools, and migration from legacy code.

## Why Install This Skill

AutoGen has distinct APIs for assistant agents, human participants, teams, and code execution. This skill helps you choose the right role and wire agents into a bounded conversation, so examples use compatible constructors and return handling.

After installing it, your agent can build modern `AssistantAgent` workflows, add human input through `UserProxyAgent`, route code blocks to `CodeExecutorAgent`, and diagnose common migration and runtime issues. The included examples target one pinned AgentChat release.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Quick start, framework routing, and topic guide |
| `templates/` | Human conversation, group chat, and Docker code execution examples |
| `references/` | API roles, code execution, conversation patterns, migration notes, and validation sources |
| `requirements.txt` | Exact package versions used by the templates |
| `scripts/test_templates.py` | Offline smoke tests with a fake model and safe executor double |

## Quick Start

Python 3.10+ is required. From this directory, create and activate a virtual environment, install the pinned packages, then run the human conversation example:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
python templates/two-agent-chat.py
```

The code execution template additionally requires Docker to be installed and running. Run the offline API smoke tests with `python scripts/test_templates.py`.

## Triggers

- Building with Microsoft AutoGen or its AgentChat API.
- Choosing between assistant, human input, and code execution agent roles.
- Creating a bounded multi-agent team or adding an agent as a tool.
- Migrating code from legacy `pyautogen` 0.2 to AgentChat.

## Requirements

- Python 3.10 or newer.
- `autogen-agentchat==0.7.5` and `autogen-ext[docker,openai]==0.7.5` (installed from `requirements.txt`).
- An OpenAI API key for model-backed examples.
- Docker Engine or Docker Desktop for the Docker code execution example.
