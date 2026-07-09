# DSPy — Worked Example: Full RAG Compilation

This example shows a complete DSPy program from definition through compilation, with expected output annotations.

## Program Definition

```python
import dspy
from dspy.datasets import DataLoader

lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

class RAG(dspy.Module):
    def __init__(self, k=3):
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = "\n".join(self.retrieve(question).passages)
        return self.generate(question=question, context=context)
```

## Dataset

```python
trainset = [
    dspy.Example(question="What is DSPy?", answer="A compiler for prompt programs.").with_inputs("question"),
    dspy.Example(question="What is a signature?", answer="Input/output field pairs defining a task.").with_inputs("question"),
    dspy.Example(question="What is MIPROv2?", answer="Bayesian optimizer for joint instruction and demo tuning.").with_inputs("question"),
]
```

## Compilation

```python
from dspy.teleprompt import MIPROv2

def correct(example, pred, trace=None):
    return example.answer in pred.answer

optimizer = MIPROv2(metric=correct, auto="light")
compiled = optimizer.compile(RAG(), trainset=trainset)
```

**Expected compile output:**
- Compiler output logs showing: bootstrapping demos, proposing instruction candidates, evaluating candidates, selecting best
- Typical run: ~30-60 seconds, ~150-300 API calls (auto="light")
- Output: a compiled module with `_compiled = True` flag set

## Inference

```python
# Use the compiled program
result = compiled(question="What is DSPy compiling?")

# Expected result structure:
print(result)  # dspy.Prediction object
print(result.answer)  # The generated answer string
# ChainOfThought also provides:
print(result.reasoning)  # The reasoning chain used

# Save for deployment
compiled.save("rag_program.json")

# Later, reload
loaded_rag = RAG()
loaded_rag.load("rag_program.json")
```

## Expected Output Depth

- Uncompiled: Answer based solely on LM training data, no optimization
- BootstrapFewShot: Higher quality, uses successful traces as demos
- MIPROv2: Highest quality, optimized instructions + demos together
- Cost: ~$0.50-2.00 for auto="light" on gpt-4o-mini
