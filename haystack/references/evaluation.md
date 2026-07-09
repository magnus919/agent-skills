# Haystack Evaluation

## Evaluation Pipeline

Evaluation in Haystack is a pipeline itself — add evaluator components to measure your pipeline's outputs.

```python
from haystack import Pipeline
from haystack.components.evaluators import DeepEvalEvaluator, DeepEvalMetric, SASEvaluator

eval_pipeline = Pipeline()
eval_pipeline.add_component("faithfulness", DeepEvalEvaluator(
    metric=DeepEvalMetric.FAITHFULNESS,
    metric_params={"model": "gpt-4o-mini"}
))
```

## Available Evaluators

| Evaluator | What it measures | Type |
|-----------|-----------------|------|
| `DeepEvalEvaluator` | Faithfulness, relevancy, context recall | LLM-as-judge |
| `SASEvaluator` | Semantic answer similarity | Embedding-based |
| `LLMEvaluator` | Custom criteria via instruction + examples | LLM-as-judge |
| `DocumentMAPEvaluator` | Mean average precision for retrieval | Statistical |

## Evaluation Workflow

```python
from haystack import Pipeline
from haystack.components.evaluators import SASEvaluator

# Run your query pipeline
results = query_pipeline.run(...)

# Build evaluation pipeline
eval_pipeline = Pipeline()
eval_pipeline.add_component("sa_eval", SASEvaluator())
eval_result = eval_pipeline.run({
    "sa_eval": {
        "predicted_answers": [results["generator"]["replies"][0]],
        "golden_answers": ["Expected answer text"]
    }
})
print(eval_result["sa_eval"]["score"])
```

## Best Practices

- Evaluate on a held-out golden dataset (not your training queries)
- Use multiple metrics — faithfulness catches hallucinations, relevancy catches retrieval misses
- Build evaluation into CI/CD for regression detection
- For production, schedule periodic evaluation runs against new data
