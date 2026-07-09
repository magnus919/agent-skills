# DSPy Evaluation

## Defining Metrics

Metrics are Python functions. They can return bool, int, or float.

```python
def exact_match(example, pred, trace=None):
    return example.answer == pred.answer

def f1_score(example, pred, trace=None):
    pred_tokens = set(pred.answer.split())
    gold_tokens = set(example.answer.split())
    if not pred_tokens or not gold_tokens:
        return 0.0
    precision = len(pred_tokens & gold_tokens) / len(pred_tokens)
    recall = len(pred_tokens & gold_tokens) / len(gold_tokens)
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
```

## dspy.Evaluate

```python
from dspy.evaluate import Evaluate

evaluator = Evaluate(devset=devset, metric=exact_match, num_threads=8)
score = evaluator(compiled_program)
print(f"Accuracy: {score}")
```

## Metrics with Feedback (for GEPA)

GEPA is the only optimizer that reads `Prediction(score, feedback)`:

```python
def metric_with_feedback(example, pred, trace=None):
    score = 1.0 if pred.answer == example.answer else 0.0
    feedback = "Correct" if score else f"Expected: {example.answer}, Got: {pred.answer}"
    return dspy.Prediction(score=score, feedback=feedback)
```

## Creating Datasets

```python
from dspy.datasets import DataLoader

# From list of dicts
trainset = [dspy.Example(question="Q1", answer="A1").with_inputs("question")]
devset = [dspy.Example(question="Q2", answer="A2").with_inputs("question")]

# Or use DataLoader for common formats
dl = DataLoader()
dataset = dl.from_json("data.json")
```

## Best Practices

- Split trainset and devset/valet — never optimize on your evaluation set
- Use float metrics for fine-grained optimization signal
- For GEPA, always provide feedback in the metric
- Start with exact_match, graduate to semantic similarity for subjective tasks
- Parallelize evaluation with `num_threads`
