# DSPy Compilation Guide

## Caching

DSPy caches all LM calls by default. Two environment variables control cache directories:

| Variable | Scope |
|----------|-------|
| `DSP_CACHEDIR` | Legacy clients (deprecated `dspy.OpenAI`, `dspy.ColBERTv2`) |
| `DSPY_CACHEDIR` | Current `dspy.LM` client |

```python
import os
os.environ["DSPY_CACHEDIR"] = os.path.join(os.getcwd(), "cache")

# Disable cache per model
lm = dspy.LM("openai/gpt-4o-mini", cache=False)
```

## Compilation Cost Management

Compilation is expensive. A typical MIPROv2 run with `auto="medium"` on gpt-4o-mini:
- ~3200 API calls
- ~2.7M input tokens, ~156K output tokens
- ~$3 USD (gpt-3.5 pricing, current models may vary)

**Cost-saving strategies:**
- Start with `BootstrapFewShot` (cheapest)
- Use `auto="light"` before `auto="medium"` or `auto="heavy"`
- Cache aggressively — re-running with cache is free
- Use a cheaper prompt_model at compile time than your task_model

## Save and Load

```python
# After compilation
compiled_program.save("my_program.json")

# Later, to use
program = MyProgram()
program.load("my_program.json")
```

## _compiled Flag

When a sub-module has `_compiled = True`, it is skipped during re-optimization. This enables the "optimize inner -> embed in outer -> optimize outer" pattern.

```python
# Force recompile a sub-module
module._compiled = False
```

## Sharing Between Programs

```python
# Export for deployment
compiled_program.save("deploy/qa_program.json")

# In deployment code
import dspy
lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

class QAModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.qa = dspy.ChainOfThought("question -> answer")

qa = QAModule()
qa.load("deploy/qa_program.json")
result = qa(question="What is DSPy?")
```

## Key Guidelines

- Compile on a representative trainset (50-500 examples typical)
- Track cost and latency from day one
- One compile per program version; serve the saved artifact many times
- Provider-side prompt caching (Anthropic, OpenAI) reduces latency for repeated ReAct calls
