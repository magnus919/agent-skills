# Problem Framing

## Start with the decision

A model is fit for purpose only relative to a decision. Record who acts, what action is
available, when the action occurs, what information exists then, and what error costs
matter. A request such as “predict risk” is incomplete until risk is defined as an
outcome, probability, loss, quantile, aggregate, or time-to-event quantity.

## Classify the question

| Question | Target | Main danger |
|---|---|---|
| Descriptive | What patterns are present? | Treating association as effect |
| Predictive | What will be observed later? | Leakage and population shift |
| Causal | What would change under intervention? | Confounding and unsupported counterfactuals |
| Decision | Which action has better expected consequence? | Optimizing a proxy that is not the decision |

Use causal language only when the design and identification strategy support it. A
predictive variable can be useful without being a cause, and a causal variable can be
poorly predictive.

## Define the observational unit

Write the row grain explicitly: policy-period, claim, payment development cell, customer-month,
firm-quarter, or event episode. Check whether rows are independent. If an entity appears
multiple times, decide whether the task needs clustered errors, fixed/random effects,
recurrent-event methods, a hierarchical model, or aggregation.

## Define exposure and windows

Counts and rates need a denominator or offset that represents opportunity. Define policy
in-force time, earned exposure, person-time, account months, or trading time. Define the
origin, observation window, development window, and prediction horizon separately. Do not
label an event “absent” when it could occur after the observation window.

## Data contract questions

- What is the source, extraction time, version, and authoritative field?
- Which fields were known at scoring time, and which were revised afterward?
- Are claims incurred, reported, paid, or developed? Are losses nominal or real?
- Are zeros structural, censored, missing, or a real measured value?
- Are large observations plausible, data errors, or a distinct regime?
- What populations are excluded, and could exclusion depend on the outcome?
- Which variables are legally, ethically, operationally, or contractually permitted?
- Which missingness, exposure, and grouping decisions must be preserved in provenance?

## Estimands and outputs

State whether the output is an expected value, event probability, rate, quantile, tail
mean, reserve, volatility, survival probability, ranking, or scenario distribution. Name
the conditioning population and horizon. For a two-part loss process, distinguish
`P(Y > 0 | X)` from `E[Y | Y > 0, X]` and explain how they are combined.

## Escalation

Stop and ask for clarification when the outcome grain, exposure, decision boundary, or
information availability cannot be recovered. Do not fill those gaps with a plausible
industry convention. For regulated or consequential use, route the completed brief to a
qualified practitioner and the applicable standard or policy owner.
