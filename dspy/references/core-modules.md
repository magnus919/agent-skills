# DSPy Core Modules

DSPy modules are the building blocks of prompt programs. Unlike LangChain chains, modules are compiled — the optimizer tunes their prompts automatically.

## dspy.Predict

The simplest module. Makes a direct prediction without intermediate reasoning.

```python
import dspy

class Sentiment(dspy.Signature):
    """Classify sentiment."""
    text: str = dspy.InputField()
    sentiment: str = dspy.OutputField(desc="positive, negative, or neutral")

classifier = dspy.Predict(Sentiment)
result = classifier(text="DSPy is amazing!")
print(result.sentiment)  # "positive"
```

## dspy.ChainOfThought

Adds step-by-step reasoning before answering. Almost always beats Predict on complex tasks.

```python
qa = dspy.ChainOfThought("question, context -> answer")
result = qa(question="What is the capital?", context="France is a country in Europe.")
print(f"Reasoning: {result.reasoning}")
print(f"Answer: {result.answer}")
```

## dspy.ReAct — Tool-Use Agent

Combines reasoning with tool calls in a loop. Takes tools as callable functions.

```python
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

# ReAct accepts a list of tools
agent = dspy.ReAct(tools=[search], signature="question -> answer")
result = agent(question="What is the latest DSPy version?")
print(result.answer)
```

## Custom dspy.Module

For multi-step programs with Python control flow:

```python
class RAG(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(question=question, context=context)

rag = RAG()
result = rag("What is DSPy?")
```

## dspy.Assert and dspy.Suggest

Validation within programs:

```python
class VerifiedQA(dspy.Module):
    def __init__(self):
        self.qa = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        pred = self.qa(question=question)
        dspy.Suggest(len(pred.answer) > 10, "Answer should be detailed.")
        return pred

# Activate assertions
from dspy.primitives.assertions import assert_transform_module, backtrack_handler
verified = assert_transform_module(VerifiedQA(), backtrack_handler)
```
