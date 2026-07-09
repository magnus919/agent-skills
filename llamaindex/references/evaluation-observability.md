# LlamaIndex Evaluation and Observability

## Built-in Evaluators

| Evaluator | What It Measures | Requires Labels? |
|-----------|-----------------|-----------------|
| `FaithfulnessEvaluator` | Answer faithful to retrieved context | No (LLM-as-judge) |
| `RelevancyEvaluator` | Answer relevant to query | No (LLM-as-judge) |
| `SemanticSimilarityEvaluator` | Answer matches reference semantically | Yes |
| `PairwiseComparisonEvaluator` | Which response is better | No (LLM-as-judge) |

```python
from llama_index.core.evaluation import FaithfulnessEvaluator

evaluator = FaithfulnessEvaluator()
result = evaluator.evaluate_response(response=response)
print(f"Faithfulness: {result.score}")
```

## Batch Evaluation

```python
from llama_index.core.evaluation import BatchEvalRunner

runner = BatchEvalRunner(
    {"faithfulness": FaithfulnessEvaluator()},
    workers=4,
)
results = runner.evaluate_responses(queries, responses)
```

## RAG Evaluation Metrics

Based on the RAG survey (Gao et al., 2023), seven measurement aspects:
1. **Answer Relevance** — Does the answer address the question?
2. **Context Relevance** — Is the retrieved context relevant?
3. **Faithfulness** — Is the answer grounded in context?
4. **Context Recall** — Are all needed chunks retrieved?
5. **Context Precision** — Are irrelevant chunks excluded?
6. **Noise Sensitivity** — Does irrelevant context degrade quality?
7. **Answer Correctness** — Is the factual answer correct?

## OpenTelemetry Tracing

```python
from fi_instrumentation import register
from traceai_llamaindex import LlamaIndexInstrumentor

trace_provider = register(project_name="rag_app")
LlamaIndexInstrumentor().instrument(tracer_provider=trace_provider)

# Every workflow run now produces trace trees with:
# - Root span per run() call
# - Child spans for retrieval and LLM calls
# - Attributes: latency, model, token counts, tool arguments
```

## Span-Attached Evaluation

```python
from fi.evals import evaluate
from fi.evals.otel import enable_auto_enrichment

enable_auto_enrichment()  # Call once at startup

# Inside a workflow step:
context = "\n\n".join([n.get_content() for n in ev.nodes])
r = evaluate("groundedness", output=str(resp), context=context)
# Score becomes a span attribute on the active span
```

## Available Observability Integrations

| Platform | Package | Type |
|----------|---------|------|
| FutureAGI traceAI | `traceai-llamaindex` | OTel spans + eval |
| OpenLLMetry | `openllmetry` | OTel spans |
| LangFuse | `langfuse` | Traces + evals |
| Arize AI | `arize` | ML observability |
