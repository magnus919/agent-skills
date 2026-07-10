---
name: agent-council
description: >-
  Multi-agent structured debate system. Spawn a panel of expert agents
  to debate any question, with convergence-aware iteration and typed
  synthesis output. Run via `agent-council` CLI. Compatible with any
  AI agent harness that supports agentskills.io skills (Claude Code,
  Cursor, Hermes Agent, OpenHands, etc.).
license: MIT
compatibility: Requires Python 3.10+ and pydantic-ai. CLI tool installs via pip.
metadata:
  source: https://git.brandyapple.com/magnus/agent-skills/agent-council
  spec-version: "1.0"
---

# Agent Council

Spawn a panel of expert agents to debate any question. The council runs a structured protocol — compose, premortem, position, cross-examination (iterative), synthesis — and produces a decision landscape with convergence diagnostics.

## When to Use

Invoke the council when any of these apply:

- The question has genuine tradeoffs with no clear correct answer
- You want multi-perspective analysis to surface hidden assumptions
- A decision would benefit from adversarial collaboration
- You want confidence diagnostics (not just a recommendation)
- The question has high stakes or irreversible consequences

**Signal phrases:** "Let's get multiple perspectives on this" / "Debate this: X" / "What would experts say about X" / "What are we missing?"

## Quick Start

### 1. Install

```bash
# One-time setup
pip install pydantic-ai
pip install agent-council

# Or install from this skill directory:
python3 scripts/bootstrap.py
```

### 2. Configure

```bash
export AGENT_COUNCIL_API_KEY="sk-..."
export AGENT_COUNCIL_MODEL="openai/gpt-4o-mini"
```

### 3. Run

```bash
agent-council "Should we use Postgres or SQLite for this service?"
```

## Command Reference

```
agent-council [OPTIONS] <question>

Options:
  --agents, -n INTEGER     Number of agents (3-7, default: 5)
  --mode, -m TEXT          Debate depth: quick | medium | deep (default: medium)
  --persona-file PATH      JSON file with custom agent personas
  --json                   Output structured JSON instead of markdown
  --verbose, -v            Show phase-by-phase progress
  --max-rounds INTEGER     Max cross-examination rounds (default: 4)
  --convergence FLOAT      Convergence threshold (default: 0.10)
```

### Mode Selection

| Mode | Agents | Rounds | When to use |
|------|--------|--------|-------------|
| `quick` | 3 | 1 cross-examine round | Low-stakes check, fast answer needed |
| `medium` (default) | 5 | Eval-driven, up to 4 rounds | Standard decisions |
| `deep` | 7 | Eval-driven, up to 4 rounds | High-stakes, hidden assumptions |

## How It Works

### Pipeline

```
Compose ──► Premortem ──► Position ──► Cross-examine ──► [eval] ──► Synthesis
  (1)        (parallel)    (parallel)    (iterative loop)    ↑        (1)

                    ┌── converged ──────┐
                    ├── diminishing_ret │
    eval ───────────┼── genuine_disagr──┼──► Synthesis
                    └── continue ───────┘
                          ↓
                   Cross-examine (next round)
```

### Phases

| Phase | What happens | Method |
|-------|-------------|--------|
| **Compose** | A single LLM call generates N expert personas tuned to the question | 1 call |
| **Premortem** | Each agent independently imagines how the decision already failed — bypasses positional commitment bias | N parallel calls |
| **Position** | Each agent forms an independent position, referencing their own premortem | N parallel calls |
| **Cross-examine** | Each agent reads all other positions and responds — concedes, disagrees, updates confidence | N parallel calls per round |
| **Eval** | Convergence detection: measures dispersion, argument novelty, concession rate. Decides whether to loop or stop | Algorithmic |
| **Synthesis** | Collates all phases into a structured decision landscape with LLM-generated narrative | 1 call |

### Convergence Detection

The council doesn't use a fixed number of rounds. After each cross-examination round, it measures:

- **Confidence dispersion** — standard deviation of agent confidence scores. Below threshold = converged.
- **Argument novelty** — new arguments not seen in prior rounds. Near zero = diminishing returns.
- **Concession rate** — points where agents shifted position. Zero + no new arguments = stalled.

Stopping conditions:
| Condition | Meaning |
|-----------|---------|
| `converged` | Dispersion below threshold, confidence stable. Genuine agreement. |
| `diminishing_returns` | No new arguments or concessions. Nothing more to surface. |
| `genuine_disagreement` | Dispersion widened, positions hardened. Summary of irreducible tension. |
| `max_rounds` | Hard cap reached. Inconclusive — principal must decide. |

## Bootstrapping

If `agent-council` is not available on PATH, the invoking agent should run:

```bash
python3 scripts/bootstrap.py
```

This installs the package from the skill directory using the current Python's pip, falling back to pipx. No PyPI dependency for the bootstrap path — the package ships inside the skill directory.

**If bootstrap fails:** Run one of these manually:
```bash
pip install pydantic-ai
pip install agent-council

# Or from this directory:
python3 -m pip install -e /path/to/agent-council/
```

## Configuration

| Env var | Required | Default | Description |
|---------|----------|---------|-------------|
| `AGENT_COUNCIL_API_KEY` | Yes | — | API key for your LLM provider |
| `AGENT_COUNCIL_MODEL` | No | `openai/gpt-4o-mini` | Model string (`provider/model`) |
| `AGENT_COUNCIL_BASE_URL` | No | Provider default | Custom API endpoint (OpenRouter, LiteLLM, etc.) |

You can set these as environment variables or create a `.env` file in the directory you run `agent-council` from:

```bash
# .env file
AGENT_COUNCIL_API_KEY=sk-...
AGENT_COUNCIL_MODEL=openai/gpt-4o-mini
```

Environment variables take precedence over `.env` file values.

Model strings follow PydanticAI convention: `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-20250514`, `deepseek/deepseek-v4-flash`, `google/gemini-2.0-flash`.

## Output

The synthesis report is a structured decision landscape. In markdown mode it includes:

1. **Confidence dispersion table** — per-round confidence metrics with diagnostic
2. **Shared risks** — failure modes from the pre-mortem (pre-positional, uncontaminated)
3. **Shared concerns** — what survived cross-examination as genuine shared risk
4. **Remaining disagreements** — positions that did not resolve
5. **Assumptions per position** — what must hold for each position to be valid
6. **Principal's path** — narrative synthesis of the decision landscape

Use `--json` for programmatic consumption.

## Architecture Decision

**Single-model debate:** All agents share one LLM configuration. Diversity comes from persona definitions (system prompts with distinct backgrounds, analytical approaches, biases), not from different model instances. This minimizes setup friction — one API key, one endpoint, predictable cost.

**Limitation:** All agents share the model's knowledge cutoff and blind spots. The convergence diagnostics include a "possible false consensus" flag when confidence starts high and never shifts.

## Reference Files

| File | Load when |
|------|-----------|
| `references/convergence.md` | Understanding the convergence detection algorithm |
| `references/debate-protocol.md` | Deep dive into phase structure and round design |
| `references/configuration.md` | Provider setup, troubleshooting, model strings |

## Directory Structure

```
agent-council/
├── SKILL.md                      # This file — skill entry point
├── pyproject.toml                # Pip package definition
├── README.md
├── LICENSE                       # MIT
├── agent_council/                # Python package
│   ├── cli.py                    # CLI entry point
│   ├── config.py                 # Env var loading
│   ├── state.py                  # Typed state + Pydantic models
│   ├── convergence.py            # Convergence detection
│   ├── graph.py                  # Debate graph orchestration
│   └── phases/
│       ├── compose.py            # Persona generation
│       ├── premortem.py          # Failure pre-mortem
│       ├── position.py           # Initial positions
│       ├── cross_examine.py      # Iterative cross-examination
│       └── synthesis.py          # Decision landscape
├── scripts/
│   └── bootstrap.py              # First-run installation
├── templates/
│   └── personas.json             # Example custom personas
└── references/
    ├── convergence.md
    ├── debate-protocol.md
    └── configuration.md
```

## Related Skills

- **langgraph** — for complex state-machine multi-agent orchestration beyond the debate protocol
- **pydanticai** — the underlying framework for type-safe agent definitions
- **spec-driven-development** — for building specs that agent-council can help you evaluate
