# Route a thread and guard a tool separately

Use [decision_middleware.py](../scripts/decision_middleware.py) when a LangChain
agent repeatedly pays for an open-ended decision with a bounded answer. Thread
routing and authorization-sensitive tool checks have different scopes and
fallbacks. Neither requires replacing the chat model.

| Decision | Hook | State and lifetime | Unknown or unavailable |
|---|---|---|---|
| Choose a model tier | `before_agent` classifies; `wrap_model_call` uses that tier | Classify the first human message against the registered tiers; persist the chosen tier in checkpointed thread state | Use the preapproved fixed baseline for this workflow, never an invented tier |
| Check an ambiguous tool request | `wrap_tool_call`, before the handler | Apply hard constraints first; assess only necessary arguments for the specific proposed call | Do not call the handler; return that review is needed without implying a review was queued |

`before_agent` is per invocation. State plus a checkpointer is what makes the
decision sticky across invocations using the same thread ID. An in-memory
checkpointer only demonstrates that within one process; use a durable one for
restart recovery. A benign route fallback says nothing about tool permission.
A production risk check needs an authenticated, versioned assessment contract
and an owned review path. The example writes to an in-memory list only.

Keep the route through ordinary follow-ups and tool results. If a task changes
purpose, hits a verified capability limit, or moves to a tier that is no longer
allowed, make an explicit transition: check the new task against currently
permitted tiers and remaining budget, start a new thread with a bounded handoff,
or design and test a versioned in-thread replacement. Price cache misses and
context rebuilding. Do not reclassify every turn by default. Do not send raw
tool output or unrelated conversation to the router. Log route reason, version,
queue and service time, cache state, fallback, and accepted outcome without
retaining unnecessary payloads.

Run the demo and assertions with the version in
[decision-middleware-requirements.txt](../scripts/decision-middleware-requirements.txt):

```sh
python -m pip install -r langchain/scripts/decision-middleware-requirements.txt
python langchain/scripts/decision_middleware.py
python -m pytest -q -o addopts= langchain/scripts/test_decision_middleware.py
```

These tests use fake models with real middleware and checkpoint hooks. They
verify persisted selection and tool effects, not provider quality or savings.
For those, use [the paired eval method](../../agent-evals-and-observability/SKILL.md)
and [System One](../../system-one/SKILL.md) for the typed adapter.

Sources: [LangChain custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom),
[Open SWE router experiment](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness),
and [Sydney Runkle’s talk, routing and tool checks](https://www.youtube.com/watch?v=qquIt--ANqI&t=247s).
