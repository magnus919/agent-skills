# DSPy FAQ and Troubleshooting

## Paradigm Questions

**Q: Is DSPy like LangChain?**
A: No. DSPy is a compiler, not a chain framework. You write programs with Python control flow and typed signatures; the compiler optimizes the prompts automatically. LangChain requires explicit prompt engineering.

**Q: When should I use DSPy instead of prompt engineering?**
A: When you need to iterate on prompt quality systematically, have a measurable metric, and can afford compilation cost. For one-shot tasks, raw API calls or LangChain are simpler.

## Installation

**Q: Installation fails?**
A: `pip install dspy` requires Python 3.10+. For ColBERT retrieval: `pip install dspy[colbert]`.

## Compilation

**Q: Compilation is too slow?**
A: Reduce `num_candidates` or use `auto="light"`. Set `num_threads` higher (8-16). Cache aggressively between runs.

**Q: Compilation is too expensive?**
A: Start with `BootstrapFewShot` (cheapest). Use a cheaper `prompt_model` than `task_model`. Enable `DSPY_CACHEDIR`.

**Q: "Context too long" errors?**
A: Reduce `max_bootstrapped_demos` and `max_labeled_demos`. Reduce retrieved passage count. Increase LM `max_tokens`.

## Errors

**Q: `dspy.ContextWindowExceededError`?**
A: Too many demos or too much context. Reduce the parameters above. This is a subclass of `dspy.LMInvalidRequestError`.

**Q: Program not improving after compile?**
A: Metric may not be discriminating enough — use float metrics instead of bool. You may need a different optimizer (check cheat sheet).

**Q: Sub-module not being optimized?**
A: Check `_compiled` flag. Set `module._compiled = False` before recompiling if you want to update it.

**Q: GEPA not working well?**
A: Ensure your metric returns `Prediction(score, feedback)`, not a bare float. GEPA is the only optimizer that reads feedback.

## Deployment

**Q: How do I deploy a compiled program?**
A: `program.save("path.json")`, copy the file to your deployment environment, load with `program.load("path.json")`.

**Q: How do I turn off caching?**
A: `dspy.LM("openai/gpt-4o-mini", cache=False)`. Or set `DSPY_CACHEDIR` to a temp directory.

**Q: Can I use DSPy with other models?**
A: Yes. DSPy supports any model accessible via `dspy.LM()`, including OpenAI, Anthropic, Ollama (local), and custom endpoints.
