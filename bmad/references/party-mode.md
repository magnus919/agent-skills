# Party Mode: Multi-Persona Deliberation

Party Mode puts several BMad roles into one conversation to find missing concerns,
pressure-test a plan, run a post-mortem, or debate a trade-off. It is a deliberation
protocol — not an implementation method.

## When to use

- Trade-off decisions with several defensible answers.
- Finding missing concerns before committing to a plan.
- Pressure-testing a plan or spec.
- Post-mortems.
- Design debates.

## Execution modes

| Mode | Mechanics | Cost | Independence |
|---|---|---|---|
| **session** | One model voices all personas inline | Cheapest, most fluid | None — one shared mind |
| **auto** | Inline unless separate agents would change the answer | Depends | Conditional |
| **subagent** | Separate agent for each persona in substantive rounds | Higher | Real separation of reasoning paths |
| **agent-team** | Persistent multi-agent team in supported harnesses | Highest | Real, persistent |

The mode is not cosmetic. Session mode is cheap and fluid but cannot provide genuinely
independent reasoning — the perspectives share one underlying mind. Subagent and team
modes cost more but reduce shared-context convergence, which is the whole point when
independence matters.

## The independence caveat

Role names provide continuity, expectations, and a consistent point of view. They do
not guarantee separate cognition. Five names in a conversation do not create five
minds. Role separation is still valuable with one model — it changes the checklist,
priorities, and questions the model is instructed to apply — but never describe it as
independent review unless the reasoning paths are actually independent.

## Ground rules

- Each persona applies its own checklist and asks its own questions; do not let one
  persona's conclusion pre-empt another's.
- Surface disagreements explicitly; consensus among personas is not independent
  validation.
- Converge toward a decision landscape: shared risks, remaining disagreements,
  confidence, and a recommended path — not a false unanimity.
- End with the decision or the open question that needs the human.

## Harness mapping

In this repository, `agent-council` is the nearest equivalent for genuinely separate
deliberation agents, and `agent-evals-and-observability` covers independent evaluators.
Use them when the independence of the reasoning paths matters to the decision.
