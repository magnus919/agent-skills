# DSPy Program Patterns

## RAG Program

```python
import dspy

class GenerateAnswer(dspy.Signature):
    """Answer with context."""
    context: str = dspy.InputField(desc="relevant facts")
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="1-3 sentences")

class RAG(dspy.Module):
    def __init__(self, k=5):
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(question=question, context=context)

rag = RAG()
result = rag("What is DSPy compiling?")
# Optimize: BootstrapFewShotWithRandomSearch
```

## Classification Program

```python
class Classify(dspy.Signature):
    """Classify customer intent."""
    text: str = dspy.InputField()
    intent: str = dspy.OutputField(desc="billing, technical, account, or sales")
    confidence: float = dspy.OutputField()

class Classifier(dspy.Module):
    def __init__(self):
        self.classify = dspy.ChainOfThought(Classify)

    def forward(self, text):
        return self.classify(text=text)
```

## Multi-Step Reasoning

```python
class Decompose(dspy.Signature):
    """Break complex question into sub-questions."""
    question: str = dspy.InputField()
    sub_questions: list[str] = dspy.OutputField()

class AnswerEach(dspy.Signature):
    """Answer a sub-question."""
    sub_question: str = dspy.InputField()
    answer: str = dspy.OutputField()

class Synthesize(dspy.Signature):
    """Combine answers into final response."""
    answers: str = dspy.InputField()
    final_answer: str = dspy.OutputField()

class MultiStepQA(dspy.Module):
    def __init__(self):
        self.decompose = dspy.ChainOfThought(Decompose)
        self.answer = dspy.ChainOfThought(AnswerEach)
        self.synthesize = dspy.ChainOfThought(Synthesize)

    def forward(self, question):
        sub_qs = self.decompose(question=question).sub_questions
        answers = [self.answer(sub_question=q).answer for q in sub_qs]
        return self.synthesize(answers="\n".join(answers))
```

## Agent with Tools

```python
def search_wikipedia(query: str) -> str:
    """Search Wikipedia."""
    return f"Results for {query}"

def calculate(expression: str) -> str:
    """Evaluate math expression."""
    return str(eval(expression))

agent = dspy.ReAct(
    tools=[search_wikipedia, calculate],
    signature="question -> answer"
)
result = agent(question="What is the population of France times 2?")
```
