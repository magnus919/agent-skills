# LangChain Skill — Research Validation Audit

**Date:** 2026-07-09
**Sources:** docs.langchain.com, reference.langchain.com, GitHub source

## Claims Verified Correct

| Claim | Source | Status |
|-------|--------|--------|
| `create_agent` from `langchain.agents` is the v1.0+ recommended pattern | docs.langchain.com migration guide | ✓ Verified |
| `create_react_agent` from `langgraph.prebuilt` is deprecated in v1.0 | reference.langchain.com deprecation warning | ✓ Verified |
| `RunnablePassthrough.assign()` exists and works as documented | reference.langchain.com | ✓ Verified |
| `RunnableParallel` and `RunnableBranch` exist in `langchain_core.runnables` | reference.langchain.com | ✓ Verified |
| `@tool` decorator has `args_schema`, `parse_docstring`, `return_direct` params | reference.langchain.com | ✓ Verified |
| `BaseCallbackHandler` in `langchain_core.callbacks` | LangChain GitHub source | ✓ Verified |
| LangSmith has Datasets, Evaluation Runs, Prompt Hub | docs.langchain.com | ✓ Verified |

## Corrections Needed

| Finding | Impact | Action |
|---------|--------|--------|
| `create_history_aware_retriever` is in `langchain_classic.chains` (deprecated module) | RAG reference should note it's classic/migration path | Add deprecation note |
| `@tool` defaults `parse_docstring=False` — LLMs miss parameter descriptions | Agents may fail to call tools correctly | Document `parse_docstring=True` recommendation |
| Docs show `from langchain.tools import tool` (not `from langchain_core.tools`) | Import path correction | Update templates and agent reference |
| `create_react_agent` has 18+ parameters documented that our skill doesn't mention | Significant depth gap | Expand agent reference with real params |

## New Content Added

| Topic | Source | File |
|-------|--------|------|
| Callbacks system with event handlers | FutureAGI article + GitHub source | `references/callbacks.md` |
| create_react_agent full parameter reference | reference.langchain.com | `references/agent-patterns.md` |
| Parse docstring pattern for @tool | GitHub issue #34292 | `references/agent-patterns.md` |
| LangSmith evaluation/experiment workflow | docs.langchain.com | `references/production-deployment.md` |
