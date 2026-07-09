# LCEL (LangChain Expression Language) Reference

LCEL is the recommended way to build chains in LangChain. The pipe operator (`|`) connects Runnable components where each component's output becomes the next component's input.

## Basic Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Answer in one sentence: {question}")
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt | model | parser
result = chain.invoke({"question": "What is LangChain?"})
```

## The Runnable Interface

All LangChain components implement `Runnable`, providing:
- `invoke()` — sync execution
- `ainvoke()` — async execution
- `stream()` — streaming output
- `batch()` — batch processing
- `astream_events()` — event streaming with metadata

## Advanced Patterns

### Parallel Execution
```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

chain = RunnableParallel(
    answer=prompt | model | parser,
    metadata=RunnablePassthrough()
)
```

### Branching
```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: len(x["question"]) > 100, long_chain),
    (lambda x: "code" in x["question"], code_chain),
    default_chain  # fallback
)
```

### Streaming
```python
for chunk in chain.stream({"question": "Explain Kubernetes"}):
    print(chunk, end="")
```

## Common Patterns

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| Sequential | `A | B | C` | Linear pipeline |
| Parallel | `RunnableParallel(a=A, b=B)` | Multiple independent operations |
| Passthrough | `RunnablePassthrough()` | Pass input unchanged |
| Branching | `RunnableBranch(...)` | Conditional routing |
| Config | `.configurable_fields()` | Runtime configuration |

## Memory in LCEL

For conversation history, use LangGraph's checkpointer rather than legacy memory:

```python
from langgraph.checkpoint.memory import MemorySaver

config = {"configurable": {"thread_id": "1"}}
saver = MemorySaver()
agent = create_agent(model, tools, checkpointer=saver)
result = agent.invoke({"messages": [("user", "Hi!")]}, config=config)
```
