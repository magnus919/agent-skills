# Evaluation Workflow — ParamTuner and Metrics

This reference shows how to set up systematic evaluation for a LlamaIndex RAG pipeline, including parameter tuning, evaluator configuration, and batch scoring.

## Setup

```python
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    SemanticSimilarityEvaluator,
    BatchEvalRunner,
)
from llama_index.llms.openai import OpenAI

gpt4 = OpenAI(model="gpt-4o")

faith_evaluator = FaithfulnessEvaluator(llm=gpt4)
rel_evaluator = RelevancyEvaluator(llm=gpt4)
sim_evaluator = SemanticSimilarityEvaluator(llm=gpt4)
```

## Single Query Evaluation

```python
response = query_engine.query("What is the rate limit for the API?")

faith_result = faith_evaluator.evaluate_response(response=response)
print(f"Faithfulness: {faith_result.score} — {faith_result.feedback}")
# Example output: Faithfulness: 0.92 — The answer is grounded in the provided context

rel_result = rel_evaluator.evaluate_response(
    response=response,
    question="What is the rate limit for the API?"
)
print(f"Relevancy: {rel_result.score} — {rel_result.feedback}")
# Example output: Relevancy: 0.88 — The answer addresses the core question
```

## Batch Evaluation

```python
eval_questions = [
    "How do I authenticate?",
    "What are the rate limits?",
    "How do I paginate results?",
    "What error codes exist?",
    "How do I handle webhooks?",
]

# Get responses
responses = [query_engine.query(q) for q in eval_questions]

# Batch evaluate
runner = BatchEvalRunner(
    {
        "faithfulness": FaithfulnessEvaluator(),
        "relevancy": RelevancyEvaluator(),
    },
    workers=4,
)

results = runner.evaluate_responses(eval_questions, responses)

for metric_name, metric_results in results.items():
    scores = [r.score for r in metric_results]
    print(f"{metric_name}: mean={sum(scores)/len(scores):.2f}, "
          f"min={min(scores):.2f}, max={max(scores):.2f}")
# Example output:
# faithfulness: mean=0.91, min=0.78, max=1.00
# relevancy: mean=0.85, min=0.72, max=0.94
```

## ParamTuner — Systematic Optimization

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.param_tuner.base import ParamTuner
from llama_index.core.evaluation import SemanticSimilarityEvaluator
import numpy as np

def build_and_evaluate(params):
    chunk_size = params["chunk_size"]
    top_k = params["top_k"]

    # Build index with these parameters
    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[SentenceSplitter(chunk_size=chunk_size)]
    )

    # Query
    query_engine = index.as_query_engine(similarity_top_k=top_k)
    responses = [query_engine.query(q) for q in eval_questions]

    # Evaluate
    evaluator = SemanticSimilarityEvaluator(llm=gpt4)
    scores = []
    for i, resp in enumerate(responses):
        result = evaluator.evaluate_response(
            response=resp,
            reference=reference_answers[i]
        )
        scores.append(result.score)

    return np.mean(scores)

param_tuner = ParamTuner(
    param_fn=build_and_evaluate,
    param_dict={
        "chunk_size": [256, 512, 1024],
        "top_k": [2, 5, 10],
    },
    fixed_param_dict={
        "documents": documents,
        "eval_questions": eval_questions[:3],
    },
)

results = param_tuner.tune()
best = results.best_run_result
print(f"Best: chunk_size={best.params['chunk_size']}, "
      f"top_k={best.params['top_k']}, score={best.score:.3f}")
# Example output: Best: chunk_size=512, top_k=5, score=0.894
```

## Seven RAG Measurement Aspects

Based on (Gao, Yunfan et al., 2023), evaluate across these dimensions:

| Aspect | What it measures | Evaluator |
|--------|-----------------|-----------|
| Answer Relevance | Does the answer address the question? | RelevancyEvaluator |
| Context Relevance | Is the retrieved context on-topic? | RelevancyEvaluator (on context) |
| Faithfulness | Is the answer grounded in context? | FaithfulnessEvaluator |
| Context Recall | Are all needed chunks retrieved? | Custom (check coverage) |
| Context Precision | Are irrelevant chunks excluded? | Custom (check rank order) |
| Noise Sensitivity | Does noise degrade answers? | Compare with/without noise |
| Answer Correctness | Are facts correct? | SemanticSimilarityEvaluator |

## Evaluation Best Practices

1. **Use held-out queries** — never tune on the same questions you evaluate on
2. **Run evaluation in the same process** — span-attached scoring preserves trace context
3. **Monitor in production** — offline notebook scoring catches known issues; production monitoring catches novel ones
4. **Combine multiple metrics** — faithfulness alone misses relevancy failures and vice versa
5. **Track over time** — regressions are easier to catch when you have a baseline
