# LangChain Production Deployment

## LangSmith Observability

Enable tracing at module import time — before any chain or agent instantiation:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
```

LangSmith provides four layers:

### 1. Tracing
Every chain/agent step is automatically captured: LLM calls, tool invocations, retrievals, latency, token counts. Traces are visible in the LangSmith UI.

### 2. Evaluation with Datasets
```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("my-eval-set")
client.create_examples(
    inputs=[{"question": "What is RAG?"}],
    outputs=[{"answer": "Retrieval Augmented Generation"}],
    dataset_id=dataset.id,
)

# Run evaluation
results = client.evaluate(
    lambda inputs: chain.invoke(inputs["question"]),
    data="my-eval-set",
    evaluators=[lambda r, ref: r["output"] == ref["answer"]],
)
```

Evaluation types: LLM-as-judge, heuristic/validation, pairwise comparison, human annotation queues.

### 3. Prompt Hub
Version-controlled prompt management:
```python
from langchain import hub
prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
hub.push("my-org/my-prompt", prompt)
```

### 4. LangSmith Engine
Autonomous issue detection from production traces — clusters failures, finds root cause, proposes fixes.

## LangServe Deployment

```python
from langserve import add_routes
from fastapi import FastAPI

app = FastAPI()
add_routes(app, chain, path="/rag")
# Run: uvicorn main:app --port 8080
```

## Production Checklist

- [ ] Enable LangSmith tracing before any code execution
- [ ] Use `create_agent` not deprecated `AgentExecutor`
- [ ] Set `max_concurrency` in `RunnableConfig` to avoid rate limits
- [ ] Implement fallbacks with `.with_fallbacks()` for reliability
- [ ] Use cheaper models (gpt-4o-mini) for simple routing tasks
- [ ] Set up LangSmith Datasets for regression testing
- [ ] Use environment variables for all secrets

## LangSmith: online typed decision evaluator

For an authorized trace project, follow the
[LangSmith setup for Jev](https://www.langchain.com/blog/jev-is-now-available-in-langsmith-evals):
configure a server-side TypeSafe provider secret and select its decision model
in the evaluator's model configuration. Map only the needed run or thread
variables to state; write scoring criteria as separate typed questions.
Each criterion gets its own feedback key. Version the feedback keys when the
meaning, rubric or judge changes so dashboards do not mix unlike scores.
Check current UI and supported model names before configuration; never send raw
secrets or unnecessary private trace data to the judge.

Treat online scores as advisory feedback. Use the
[agent-eval method](../../agent-evals-and-observability/references/judge-stability.md)
for frozen trace replay and judge qualification, and
[harness engineering](../../harness-engineering/references/system-one-decisions.md)
for asynchronous execution, retry semantics and separate completion evidence.
