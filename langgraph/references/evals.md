# Evals — Evaluating Multi-Agent Systems

This reference covers methodology for evaluating multi-agent LangGraph systems. Evals are critical — without them, you're debugging routing behavior in production.

## Why Multi-Agent Evals Are Different

Single-agent evals test output quality against a rubric. Multi-agent evals must also test:
- **Routing accuracy** — Did the right agent(s) handle each domain?
- **Resolution coverage** — Were ALL parts of a multi-domain request addressed?
- **Handoff correctness** — Were handoffs clean, with full context propagation?
- **Recovery behavior** — Did the system degrade gracefully on errors?

## Building an Eval Dataset

### Using LangSmith

```python
from langsmith import Client

ls_client = Client()

dataset = ls_client.create_dataset(
    dataset_name="multi-agent-routing-evals",
    description="Routing and resolution evaluation dataset",
)

ls_client.create_examples(
    dataset_id=dataset.id,
    inputs=[
        {"question": "I need to change my payment method to a credit card."},
        {"question": "My SSO integration is returning error code SAML-401."},
        {"question": "I want to upgrade to Enterprise and also fix my broken SSO."},
        {"question": "Can you tell me who my account manager is?"},
    ],
    outputs=[
        {
            "expected_agents": ["billing"],
            "must_mention": ["payment", "credit card"],
        },
        {
            "expected_agents": ["tech_support"],
            "must_mention": ["SSO", "SAML"],
        },
        {
            "expected_agents": ["tech_support", "account"],
            "must_mention": ["SSO", "upgrade"],
        },
        {
            "expected_agents": ["account"],
            "must_mention": ["account manager"],
        },
    ],
)
```

### Dataset Design Principles

- **Cover all routing paths** — single-domain requests, multi-domain requests, edge cases
- **Include ambiguous requests** — ones that could route to multiple agents
- **Include negative cases** — requests that should not route to certain agents
- **5-20 examples minimum** — enough to catch regressions, not so many that eval is slow

## Evals

### 1. LLM-as-Judge (Routing Quality)

```python
from langsmith import evaluate
from openevals.llm import create_llm_as_judge

ROUTING_QUALITY_PROMPT = """\
Customer query: {inputs[question]}
Expected domains: {reference_outputs[expected_agents]}
Agent response: {outputs[final_response]}
Resolution notes: {outputs[resolution_notes]}

Rate 0.0-1.0 on whether the correct specialist agents handled the request
and the response fully addressed the customer's needs.
Return ONLY: {{"score": <float>, "reasoning": "<explanation>"}}"""

routing_judge = create_llm_as_judge(
    prompt=ROUTING_QUALITY_PROMPT,
    model="anthropic:claude-sonnet-4-5-20250929",
    feedback_key="routing_quality",
)
```

### 2. Resolution Coverage (Custom Evaluator)

Measures whether the final response mentions all required topics:

```python
def resolution_coverage(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    text = outputs.get("final_response", "").lower()
    notes = " ".join(outputs.get("resolution_notes", [])).lower()
    combined = text + " " + notes
    must_mention = reference_outputs.get("must_mention", [])
    hits = sum(1 for t in must_mention if t.lower() in combined)
    return {
        "key": "resolution_coverage",
        "score": hits / len(must_mention) if must_mention else 1.0,
    }
```

### 3. Agent Routing Accuracy (Custom Evaluator)

Measures whether the correct agents were invoked:

```python
def agent_routing_accuracy(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    notes = " ".join(outputs.get("resolution_notes", [])).lower()
    expected = reference_outputs.get("expected_agents", [])
    hits = sum(1 for agent in expected if agent.lower() in notes)
    return {
        "key": "routing_accuracy",
        "score": hits / len(expected) if expected else 1.0,
    }
```

## Running Evaluations

### Pattern Comparison

Run both patterns against the same dataset to compare:

```python
# Supervisor target function
def supervisor_target(inputs: dict) -> dict:
    result = supervisor_graph.invoke({
        "messages": [HumanMessage(content=inputs["question"])],
        "current_agent": "",
        "resolution_notes": [],
    })
    return {
        "final_response": result["messages"][-1].content,
        "resolution_notes": result.get("resolution_notes", []),
    }

# Swarm target function
def swarm_target(inputs: dict) -> dict:
    result = swarm_graph.invoke({
        "messages": [HumanMessage(content=inputs["question"])],
        "current_agent": "",
        "resolution_notes": [],
    })
    return {
        "final_response": result["messages"][-1].content,
        "resolution_notes": result.get("resolution_notes", []),
    }

# Run both
supervisor_results = evaluate(
    supervisor_target,
    data="multi-agent-routing-evals",
    evaluators=[routing_judge, resolution_coverage, agent_routing_accuracy],
    experiment_prefix="supervisor-v1",
    max_concurrency=2,
)

swarm_results = evaluate(
    swarm_target,
    data="multi-agent-routing-evals",
    evaluators=[routing_judge, resolution_coverage, agent_routing_accuracy],
    experiment_prefix="swarm-v1",
    max_concurrency=2,
)
```

## What to Watch

| Metric | What it catches | Action if it drops |
|--------|----------------|--------------------|
| **Routing accuracy** | Wrong agent handling a domain | Fix routing prompt or handoff logic |
| **Resolution coverage** | Multi-domain requests only partially addressed | Add explicit multi-domain routing logic |
| **Token cost per request** | Supervisor re-routing waste or context bloat | Consider fast-path or swarm migration |
| **Handoff chain length** | Swarm ping-pong or routing confusion | Add recursion guard, fix agent prompts |

## Eval-Driven Development Workflow

1. **Write the eval before the second agent** — building the routing accuracy eval is the first step after the triage agent
2. **Run on every PR** — the `routing_accuracy` evaluator is the canary. If it drops, your routing prompt or handoff logic regressed
3. **Compare patterns side-by-side in LangSmith** — make the supervisor-vs-swarm decision with data, not intuition
4. **Add examples from production misroutes** — every routing error in production should become a new eval example
