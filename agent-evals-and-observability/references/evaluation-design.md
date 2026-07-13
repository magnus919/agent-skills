# Evaluation Design

Write a task contract: inputs and context, permitted tools and permissions, expected outcome, prohibited outcomes, environment assumptions, and observable completion evidence. Add a trajectory contract when the path matters: eligible tool selection and arguments, authorization checks, state transitions, grounding sources, recovery behavior, stopping/escalation, and permitted side effects.

Select evidence rather than requiring every evaluation type:

| Evidence | Useful when | Boundary |
|---|---|---|
| Unit | A prompt formatter, tool adapter, parser, or guard can be isolated | Does not establish integration behavior |
| Component | Router, retriever, policy layer, or tool boundary interacts internally | May hide production environment behavior |
| Scenario | A complete task must run under controlled conditions | Results depend on fixture fidelity |
| Regression | A known behavior or escaped failure must remain protected | Cannot cover unknown failures |
| Adversarial | Misuse, injection, unsafe actions, or leakage are plausible | Challenge coverage is never exhaustive |
| Online | Distribution shift, service variability, or user outcomes matter | Confounding and consent constrain interpretation |
| Human review | Domain or subjective criteria cannot be directly automated | Review remains rubric- and context-sensitive |

Use synthetic, curated, replayed-production, adversarial, and regression cases as distinct declared sources. Choose a mix based on task harm, reversibility, novelty, external side effects, and availability of valid evidence.
