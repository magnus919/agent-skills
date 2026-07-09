# LCEL (LangChain Expression Language) Reference

LCEL uses the pipe operator (`|`) to connect Runnable components. Every component — prompt, model, parser, retriever — implements the Runnable interface.

## Basic Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

chain = ChatPromptTemplate.from_template("Answer: {q}") | ChatOpenAI() | StrOutputParser()
result = chain.invoke({"q": "What is LCEL?"})
```

## The Runnable Interface

All components implement `Runnable`, providing these methods:

| Method | Description |
|--------|-------------|
| `invoke(input)` | Sync execution |
| `ainvoke(input)` | Async execution |
| `stream(input)` | Token-by-token streaming |
| `astream(input)` | Async streaming |
| `batch(inputs)` | Batch processing |
| `abatch(inputs)` | Async batch |
| `astream_events(input, version)` | Event stream with metadata |

## Runnable Primitives

### RunnablePassthrough

```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# Pass input unchanged
RunnablePassthrough()

# Incrementally add keys to a dict — critical for RAG chains
RunnablePassthrough.assign(
    upper=lambda x: x["text"].upper()
)

# Combine both patterns
RunnableParallel(
    origin=RunnablePassthrough(),
    modified=lambda x: x["num"] + 1
)
```

### RunnableParallel — Concurrent Execution

```python
chain = RunnableParallel(
    answer=prompt_a | model | parser,
    summary=prompt_b | model | parser,
)
```

Dictionaries are automatically coerced to RunnableParallel:
```python
chain = {"answer": chain_a, "summary": chain_b}  # shorthand
```

### RunnableLambda — Wrap Any Function

```python
from langchain_core.runnables import RunnableLambda

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = retriever | RunnableLambda(format_docs) | prompt | model | parser
```

### RunnableConfig

| Field | Description |
|-------|-------------|
| `max_concurrency` | Limit parallel calls |
| `recursion_limit` | Max steps before error |
| `tags` | Labels for tracing |
| `callbacks` | Custom callback handlers |
| `metadata` | Arbitrary key-value data |

```python
from langchain_core.runnables import RunnableConfig

chain.invoke(input, config=RunnableConfig(max_concurrency=5, tags=["prod"]))
```

### Error Handling

```python
# Fallback chain if primary fails
safe_chain = chain.with_fallbacks([fallback_chain])
```

### Runtime Configuration

```python
# Make parameters configurable at invocation time
configurable_chain = (
    ChatPromptTemplate.from_template("Answer: {q}")
    | ChatOpenAI().configurable_fields(
        model=ConfigurableField(id="model", name="Model")
    )
    | StrOutputParser()
)

chain.with_config(configurable={"model": "gpt-4"})
```

## Branching

```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: len(x["q"]) > 100, long_chain),
    (lambda x: "code" in x["q"], code_chain),
    default_chain,
)
```

## Common Patterns Reference

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| Sequential | `A | B | C` | Linear pipeline |
| Parallel | `RunnableParallel(a=A, b=B)` | Independent operations |
| Passthrough | `RunnablePassthrough()` | Pass input unchanged |
| .assign | `.assign(key=fn)` | Incremental dict building |
| Lambda wrap | `RunnableLambda(fn)` | Wrap arbitrary Python fn |
| Branching | `RunnableBranch(...)` | Conditional routing |
| Fallback | `.with_fallbacks([...])` | Error recovery |
| Config | `.configurable_fields(...)` | Runtime model/param config |
