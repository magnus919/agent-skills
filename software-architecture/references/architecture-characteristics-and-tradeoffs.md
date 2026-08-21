# Architecture Characteristics And Tradeoffs

## Start with scenarios

Do not list qualities as adjectives. Write a scenario with a stimulus, affected boundary, measurable response, and context. For example: "During a regional dependency outage, checkout preserves order acceptance for 15 minutes, returns a clear pending state, and reconciles accepted orders when the dependency returns." The scenario makes the tradeoff and evidence surface visible.

Classify each driver as business outcome, user expectation, operational need, legal or contractual constraint, team constraint, or technical constraint. Mark each claim as observed, reported, inferred, or unknown.

## Prioritize without pretending precision

Rank scenarios using a short rationale such as must-preserve, differentiating, enabling, or deferrable. Record who supplied the priority and what would change it. Avoid universal numeric weights when evidence cannot support them. If a score is useful, show the inputs and uncertainty.

## Compare options

For each candidate, assess:

- value delivered for the drivers;
- cost paid in complexity, latency, coordination, and operations;
- failure and recovery behavior;
- reversibility and migration burden;
- team capability and ownership fit;
- evidence available now and evidence still needed.

Separate hard constraints from preferences. A candidate that violates a hard constraint is not a lower-scoring option; it is rejected unless the constraint changes.

## Conflicts are decisions

Common tensions include consistency versus availability, isolation versus cost, autonomy versus duplicated capability, latency versus durability, flexibility versus simplicity, and local ownership versus cross-system reuse. State which side is favored, for which scenario, and what consequence is accepted. A tradeoff record is incomplete if it names only benefits.

## Review questions

Ask: What user or operator harm occurs if this characteristic is missed? Where is the boundary that can enforce it? What is the tail behavior, not just the average? Which assumption is most likely to be wrong? What evidence would reverse the choice?
