# Configuration Guide

## Environment Variables

| Env var | Required | Default | Description |
|---------|----------|---------|-------------|
| `AGENT_COUNCIL_API_KEY` | Yes | — | API key for your LLM provider |
| `AGENT_COUNCIL_MODEL` | No | `openai:gpt-5.6-luna` | Model string in `provider:model` format |
| `AGENT_COUNCIL_BASE_URL` | No | Provider default | Custom API endpoint |

## Provider Setup

### OpenAI

```bash
export AGENT_COUNCIL_API_KEY="sk-..."
export AGENT_COUNCIL_MODEL="openai:gpt-5.6-luna"
```

### Anthropic

```bash
export AGENT_COUNCIL_API_KEY="sk-ant-..."
export AGENT_COUNCIL_MODEL="anthropic/claude-sonnet-4-20250514"
```

### DeepSeek

```bash
export AGENT_COUNCIL_API_KEY="sk-..."
export AGENT_COUNCIL_MODEL="deepseek/deepseek-v4-flash"
export AGENT_COUNCIL_BASE_URL="https://api.deepseek.com/v1"
```

### OpenRouter

```bash
export AGENT_COUNCIL_API_KEY="sk-or-..."
export AGENT_COUNCIL_MODEL="openrouter/anthropic/claude-sonnet-4"
export AGENT_COUNCIL_BASE_URL="https://openrouter.ai/api/v1"
```

### Local / Ollama

```bash
export AGENT_COUNCIL_API_KEY="ollama"  # or any placeholder
export AGENT_COUNCIL_MODEL="ollama/llama-3.2"
export AGENT_COUNCIL_BASE_URL="http://localhost:11434/v1"
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Configuration error: AGENT_COUNCIL_API_KEY is not set` | Missing API key | `export AGENT_COUNCIL_API_KEY="..."` |
| `ImportError: No module named 'pydantic_ai'` | Missing dependency | `pip install pydantic-ai` |
| Model not found | Wrong model string format | Check PydanticAI provider convention: `provider:model-name` |
| Debate hangs or times out | Model too slow for N parallel calls | Reduce agents with `--agents 3`, or use a faster model |
| All agents agree immediately | False consensus (same-model blind spots) | Check synthesis diagnostic; consider richer persona definitions |
