# Performance audit protocol — issue #768

Recorded before the local execution below. Source revision:
`6eeef1dfbe2348191b0866acdfb7a8b470186e63`.

Question: do representative tasks expose a repeated, decision-relevant gap that
justifies changing performance-optimization rather than its metadata or a neighbor?

Hypothesis: the current measurement/diagnosis/experiment/field loop already supplies
the decisions required by the seven existing output cases. This is an inspection
hypothesis, not a claim about agent behavior or user outcomes.

Corpus: all seven stable cases in the pinned performance-optimization/evals/evals.json,
plus its runnable membership example. Cases are authored reproducible fixtures;
they are not actual-user reports or evidence of market demand. Inspect all cases,
including stop, timeout and proxy failures; do not choose only favorable ones.

Method: inventory every skill file and relevant history; map each case to exact
sections and record the action/disposition those instructions support. Execute the
existing example for nine alternating pairs and both documented CPU profiles.
Check invalid-run input once. Preserve commands, raw stdout/stderr, exit status,
environment and source hashes. No generated model output or live field run.

Decision rule: recommend one bounded follow-on if the same consequential missing
decision mechanism appears in at least two cases, or one severe boundary defect is
reproduced. Distinguish absence of a language example from a missing method. If no
such failure is demonstrated, recommend no skill change for the inspected scope,
list unassessed evidence, and name the observation that would reopen the decision.

Bounds: local synthetic example only; one nine-pair comparison, two profiles, one
invalid-argument probe; no production data, network benchmark, load test, deployment,
live model/Jev call, or telemetry collection. Stop on unexpected fixture failure;
preserve it rather than modifying the skill. Host timing does not establish field
benefit or validate a performance gate. No skill implementation under this audit.
