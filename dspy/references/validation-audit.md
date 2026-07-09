# DSPy Skill — Research Validation Audit

**Date:** 2026-07-09
**Sources:** dspy.ai, github.com/stanfordnlp/dspy

## Claims Verified Correct

| Claim | Source | Status |
|-------|--------|--------|
| `dspy.Predict(signature)` — direct prediction | dspy.ai docs | ✓ |
| `dspy.ChainOfThought(signature)` — with reasoning | dspy.ai docs | ✓ |
| `dspy.ReAct(signature, tools=tools, max_iters=10)` — tool-use agent | dspy.ai ReAct page | ✓ |
| Custom module via `class MyModule(dspy.Module)` with `forward()` | dspy.ai custom_module tutorial | ✓ |
| BootstrapFewShot, BootstrapRS, MIPROv2, GEPA, COPRO optimizers | dspy.ai optimizer guide | ✓ |
| `DSPY_CACHEDIR` for current cache, `DSP_CACHEDIR` for legacy | dspy.ai FAQ | ✓ |
| `_compiled = True` flag prevents sub-module re-optimization | dspy.ai optimizer guide | ✓ |
| `.compile()` returns new copy, original not mutated | dspy.ai optimizer guide | ✓ |
| Tool functions need docstring + type hints | dspy.ai customer_service_agent tutorial | ✓ |

## Claims Verified and Corrected

| Claim | Correction | Source |
|-------|-----------|--------|
| `max_iters` parameter on ReAct | Confirmed: exists, default not documented | dspy.ai ReAct page |

## Missing from Skill (Addressed in This Enrichment)

- Worked example showing full RAG compilation with expected output
- `max_iters` on ReAct documented
- Custom agent pattern (not just ReAct — full Module subclass)
