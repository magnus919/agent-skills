# Interpretability workflow

Interpretability is evidence about model behavior under a method and reference
distribution. It is not automatically a causal explanation or a user-facing
justification.

1. State the decision, audience, stakes, and explanation target: global model
   behavior, local prediction, error diagnosis, fairness investigation, or a
   contrastive question. Define whether the audience needs a diagnostic view or
   an actionable explanation.
2. Choose scope and background deliberately. Record the model, data version,
   reference population, feature preprocessing, missingness, and perturbation or
   intervention semantics. For local explanations, state the neighborhood and
   baseline; for global explanations, state the population and aggregation.
3. Check correlated features, proxies, extrapolation, and distribution shift.
   A feature attribution may be shared among correlated variables or reflect a
   model shortcut. A perturbation may create impossible records and should be
   marked invalid rather than interpreted.
4. Validate the explanation: rerun with seeds, nearby backgrounds, and relevant
   perturbations; use label or feature randomization sanity checks where
   applicable; compare at least one materially different method or model. Record
   disagreement instead of averaging it into false certainty.
5. Inspect slices, especially protected groups and high-impact cases. An
   aggregate explanation or fairness result can hide a subgroup failure. Report
   sample sizes, uncertainty, missingness, and the limits of slice comparisons.
6. Write the conclusion in predictive language unless a causal design identifies
   an intervention effect. Never turn “the model relied on X” into “X caused Y.”
   Route causal claims to `references/causal-inference-framework.md`.

Explanation outputs belong in a versioned report with method, target, audience,
background, stability results, method disagreement, slice results, and known
failure modes. Do not expose sensitive feature values or internal reasoning just
to make an explanation look complete.
