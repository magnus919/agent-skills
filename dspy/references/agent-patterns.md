# DSPy Agent Patterns

## ReAct Agent

```python
import dspy

def search(query: str) -> str:
    """Search the knowledge base."""
    return f"Results for: {query}"

def calculate(expr: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expr))

agent = dspy.ReAct(tools=[search, calculate], signature="question -> answer")
result = agent(question="What is 2+2?")
```

## AvatarOptimizer for Agent Programs

The AvatarOptimizer is specifically designed for agent-style programs with clean pass/fail metrics:

```python
from dspy.teleprompt import AvatarOptimizer

optimizer = AvatarOptimizer(metric=metric, max_iters=10)
compiled = optimizer.compile(program, trainset=trainset)
```

It partitions trainset into positive and negative examples, then iteratively proposes instruction edits that explain the difference.

## Tool Design Guidelines

- Tools are plain Python functions with type hints and docstrings
- The docstring becomes the tool description the LM sees
- Tools should handle errors gracefully and return string results
- For complex tools, wrap external APIs with error handling inside the function
- ReAct loops until no more tool calls or max iterations reached
