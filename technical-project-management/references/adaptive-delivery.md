# Iterative, incremental, and Scrum delivery

Use for uncertain requirements, learning through feedback, or a team using Scrum.
Basis: S02 for Scrum definitions, S05 for incremental development and oversight.
The project-coordination procedure is original synthesis.

## Preserve framework accountabilities

In Scrum, the Product Owner orders product work, Developers manage their delivery
plan, and the Scrum Master supports Scrum effectiveness. The project coordinator
handles cross-boundary commitments without taking over those accountabilities.
A Sprint Goal is not a guarantee that every selected item will finish. Work that
misses the Definition of Done is not a completed increment. Sprint Review is not
an additional release approval gate. These distinctions come from S02.

## Manage uncertainty explicitly

1. Identify the uncertainty that could invalidate the delivery forecast: user
   need, technical feasibility, integration, data quality, or operational fitness.
2. Define a small learning or delivery outcome with an evaluator and evidence.
   A prototype may retire a risk without being production-ready.
3. Reserve capacity for validation, integration, rework, and support; avoid a
   capacity plan that assumes every hour produces new scope.
4. Inspect results with people able to decide the next step. Record what changed
   in the assumption, scope, forecast, or acceptance evidence.
5. Update the broader milestone view from accepted work and remaining uncertainty.
   Report scope growth separately from throughput so progress is not obscured.

Do not convert one team's story points into another team's dates or compare people
by velocity. Use a stable team's relevant delivery history only when item boundaries,
quality criteria, capacity, and work mix are comparable. A new team needs explicit
uncertainty and an early calibration checkpoint, not invented historical data.

## Boundary cases

| Situation | Management response |
|---|---|
| A deadline is fixed but research may fail | Commit to a learning decision or bounded fallback; do not promise the research result |
| User feedback is unavailable | Find a legitimate evaluator or label the assumption unvalidated |
| Support interrupts every sprint | Quantify interruption demand and agree intake/capacity changes; route flow design to kanban-guru |
| Teams finish separate components but integration fails | Establish shared integration evidence before reporting capability complete |
| Audit evidence is required | Include evidence creation in work and acceptance; iteration does not waive obligations |
| AI output quality is probabilistic | Define evaluation dataset, acceptance criteria, review authority and fallback with ML/agent specialists |

## Lightweight and expert use

A team without a PM can start with one visible ordered work list, one shared outcome,
accepted-work evidence, and a brief review. Call this a lightweight adaptive setup
unless the full chosen framework is actually being followed. An expert TPM usually
needs an exception summary and impact on commitments, not a ceremony redesign.

Complete when the next learning/delivery outcome, evaluator, capacity assumptions,
and effect on project commitments are clear.
