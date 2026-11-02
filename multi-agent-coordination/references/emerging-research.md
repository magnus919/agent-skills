# Emerging research: useful distinctions and open questions

All sources accessed 2026-11-02; pinned versions and evidence limits are in source
records S22–S27. These are research findings, not reproduced local results. Follow
full papers and released artifacts before making quantitative deployment claims.

## Constraint survival at synthesis boundaries

[AgentCollabBench v1](https://arxiv.org/abs/2605.08647v1) separates four behavioral
risks rather than aggregating them. A converging node can discard a constraint
from a minority branch even when the combined answer appears plausible. Apply
this as a challenge: give two workers compatible facts plus one consequential
constraint, then inspect whether integration preserves that constraint. Include
cross-task leakage and harmless markers, but do not confuse marker survival with
correct reasoning or compliance. This proposed fixture is our transfer, not an
execution of the published benchmark.

## Communication is not distributed reasoning

[Silo-Bench v2](https://arxiv.org/abs/2603.01045v2) distinguishes successful exchange
from correct synthesis on algorithmic distributed-information tasks. Diagnose
whether the integrator lacks evidence or fails to combine sufficient evidence.
Adding more messages only addresses the former. This challenges the video's
strongest context-only reading: sometimes the necessary information is already
present. The benchmark's protocols and homogeneous models limit generalization.

## Measure the actual coordination structure

[When Agents Coordinate v1](https://arxiv.org/abs/2608.16801v1) models agent/file
interactions over time. A coordinator title does not establish a functioning
hub. Inspect actual directed messages, shared artifacts and decisions, and account
for unobserved shell file activity. Compare resource cost and outcomes, not a
network visual alone. Protected evaluator fixtures are necessary because agents
may reach for grading material; the paper's sealed replication changes how some
uncontained findings should be interpreted.

[MAScope v1](https://arxiv.org/abs/2610.10126v1) uses topology-grounded trace context
for failure classification. Preserve graph evidence and extraction uncertainty
in incident records. Correlated topology/failure patterns are triage hypotheses;
a model-assigned category is not an independently established root cause.

## Integration tests can manufacture apparent interference

[STALE v1](https://arxiv.org/abs/2609.25396v1) compares each patch and their
combination with the same combined tests. If solo runs use narrower tests,
a preexisting defect can appear to be caused by merging. Apply the same suite
and base revision before counting newly introduced interaction failures. Its
contrast between mined reviewed PR pairs and constructed tasks warns against
using challenge-set failure rates as production prevalence. Updated interface
information is a candidate intervention, not proof that a brief message solves
all integration problems.

## Resource contention is a protocol problem too

[DPBench v2](https://arxiv.org/abs/2602.13255v2) varies simultaneous action,
communication and resource structure independently. Use it to motivate safe
mechanism probes for ordering, symmetry breaking and release of reservations.
Do not transfer its group-size behavior into a recommendation to add workers.
A real system still needs runtime-enforced ownership and recovery.

## Research backlog

- Do these effects persist across heterogeneous frontier harnesses under equal
  total cost and real integration/review work?
- Which lineage signals detect accidental bad practice without excessive storage,
  false positives or disclosure of private context?
- Can context refresh improve decision quality without increasing process noise?
- Which shared-file designs preserve privacy and authority while reducing
  duplicate exchange?
- How does a verified topology change migrate already running/queued work?

Promote answers only with preserved evidence, independent acceptance, adverse
cases and clearly stated populations. Keep new tool reports in the tool-assessment
format; refresh this reference on material revisions or newly observed failures.
