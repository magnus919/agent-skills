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

## Counterfactual readiness for discrete decisions

Use off-policy evaluation only when the logged decision and outcome can support the
question. For an agent, start with a bounded choice such as routing to one of several
retrievers or tools. An arbitrary generated response or full multi-step trajectory is
not automatically a contextual-bandit action with comparable logged outcomes.

Before handing estimation to `data-scientist`, record:

1. Decision unit, eligible actions, available context, chosen action, logging policy
   version and the probability with which that policy chose the action. Confidence in
   an answer is not its action-selection probability.
2. Outcome definition, observation horizon, missing/delayed outcomes and attribution.
   Log only necessary, permitted context; do not collect sensitive fields speculatively.
3. Target policy and population, plus overlap: where the target chooses actions the
   logging policy never chose, the log cannot identify those outcomes without additional
   assumptions. Do not invent rewards for unchosen actions.
4. Weight concentration, effective information, uncertainty, and sensitivity to any
   clipping or model assumptions. Large logged volume does not fix absent support.
5. The smallest next evidence step if assumptions fail: improve authorized logging,
   narrow the estimand explicitly, or propose a bounded controlled experiment. Do not
   promote based on a counterfactual score whose eligibility checks failed.

An outcome model can extrapolate beyond observed support, but that is model-dependent
prediction, not an observed counterfactual. Doubly robust methods do not make missing
support or deployment distribution changes disappear. Preserve unsupported regions and
route estimator choice, confounding and interval design to the statistical owner.

Primary research checked 2026-09-14: [Wang et al., optimal and adaptive off-policy evaluation](https://arxiv.org/abs/1612.01205)
for contextual-bandit evaluation assumptions, and [Kallus et al., distributionally robust off-policy evaluation](https://proceedings.mlr.press/v162/kallus22a.html)
for sensitivity to shifts between logged and deployment environments.
