# Evidence modes and offline-to-online metric mirrors

Choose the evidence mode from the decision, rather than treating offline scores as a complete proxy for production behavior.

| Mode | Question | Design | Boundary |
|---|---|---|---|
| Performance | Does the candidate meet the declared outcome on known cases? | Frozen cases, baseline pairing, task and slice metrics | Does not explain why a case fails or predict distribution shift |
| Diagnostic | Which behavior, slice, component, or condition produces the failure? | Error taxonomy, controlled perturbations, slice analysis, trace review | Diagnostic findings are hypotheses until the claimed property is tested |
| Replay/simulation | What would the candidate do under recorded or modeled conditions? | Versioned replay inputs, simulated tools/state, side-effect suppression, fidelity checks | Replay cannot establish user response or an alternate outcome without assumptions |
| Online | What happens under live distribution, latency, feedback, and user interaction? | Shadow, canary, or randomized exposure with guardrails and consent | Confounding, feedback loops, missingness, and proxy gaming constrain inference |

## Metric mirror

For every offline metric used to justify an online decision, record:

- offline property, dataset population, case version, and grader;
- online signal intended to reflect it, population and denominator;
- causal or operational link assumed between the two;
- expected direction and acceptable divergence;
- slice coverage and known blind spots;
- data latency, missingness, selection, and feedback-loop risks;
- owner, alert or review action, and next validation date.

Do not call two measures correlated because they share a name or trend in one release. Check the relationship over multiple comparable runs or windows, inspect reversals by slice, and record when evidence is insufficient. A product metric can be useful for monitoring while remaining unsuitable as a release oracle.

## Readiness and replay controls

Before live exposure, verify the candidate and baseline identifiers, fixture and tool versions, replay fidelity, side-effect suppression, time and concurrency conditions, and privacy limits. Shadow or replay evidence can qualify a candidate for a live experiment; it cannot silently authorize mutations. For replayed production data, retain only the minimum transformed inputs required for the decision and document rights, consent, retention, and contamination controls.
