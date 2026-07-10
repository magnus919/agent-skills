# Agent Council

Multi-agent structured debate system — spawn a panel of expert agents to debate any question with convergence-aware iteration.

```bash
pip install agent-council
agent-council "Should we migrate from SQLite to Postgres?"
```

## Quick Start

```bash
export AGENT_COUNCIL_API_KEY="sk-..."
export AGENT_COUNCIL_MODEL="openai/gpt-4o-mini"

agent-council "Should we use WebSockets or SSE for real-time notifications?"
```

## Features

- **Structured debate protocol** — compose, premortem, position, cross-examine (iterative), synthesis
- **Convergence-aware iteration** — the protocol measures confidence dispersion and stops when diminishing returns set in, not at a hardcoded round count
- **Typed outputs** — every phase produces validated Pydantic models, consumable as JSON or human-readable markdown
- **Custom personas** — supply your own agent definitions, or let the compose phase generate them from the question
- **Convergence diagnostics** — confidence dispersion, position overlap, argument novelty — surfaced in every synthesis report
- **Cross-platform** — works with any AI harness that supports agentskills.io skills (Claude Code, Cursor, Hermes Agent, OpenHands, etc.)

## Installation

```bash
pip install pydantic-ai
pip install agent-council
```

Or install from the skill directory:

```bash
pip install -e /path/to/agent-council/
```

## Usage

```bash
# Quick debate (3 agents, 1 cross-examine round)
agent-council --mode quick "Should we use Postgres or SQLite?"

# Standard debate (5 agents, iterative cross-examination)
agent-council "What architecture should we choose for this service?"

# Deep debate (7 agents, full protocol with assumption mapping)
agent-council --mode deep --agents 7 "Should we migrate to microservices?"

# With custom personas
agent-council --persona-file personas.json "Evaluate our cloud strategy"

# JSON output for programmatic consumption
agent-council --json "Which cloud provider should we choose?"
```

## Output

The synthesis report includes:
- **Confidence dispersion table** — agent-by-agent confidence before and after debate
- **Shared risks** — failure modes identified in the pre-mortem (before positional commitment)
- **Shared concerns** — what survived cross-examination as genuine shared risk
- **Genuine disagreements** — positions that remained unresolved after debate
- **Assumptions per position** — what would need to be true for each position to be correct
- **Principal's path** — narrative synthesis of the decision landscape

## Configuration

| Env var | Required | Default | Description |
|---------|----------|---------|-------------|
| `AGENT_COUNCIL_API_KEY` | Yes | — | API key for your LLM provider |
| `AGENT_COUNCIL_MODEL` | No | `openai/gpt-4o-mini` | Model string (provider/model) |
| `AGENT_COUNCIL_BASE_URL` | No | Provider default | Custom API endpoint |

## License

MIT
