# Model Card

> **Confidentiality:** A completed model card records intended use, data, performance, fairness results, limitations, and monitoring for a specific model. Store it with access controls appropriate to the sensitivity of the model and its data. This template implements the model-card documentation discipline described in `references/fairness-bias-accountability.md` and `references/ai-lifecycle-governance.md`, and is informed by the current state of model and data cards in `research-technical-controls.md`. It is the durable, audit-ready record that accompanies a model-registry entry.

## When To Use

Use this card to document any model you develop, procure, or operate so that it is understood and applied only where it is suited. Finalize it at the evaluation gate, before deployment, and refresh it when the model, its data, its context of use, or its performance changes materially. The card is both the evidence that clears the evaluation gate and the reference that the monitoring and incident-response phases consult later. For a point-in-time analysis of how risky a model is and which tier it belongs in, use `model-risk-assessment.md`.

## When Not To Use

Do not use this card as a substitute for a risk assessment and tiering decision (`model-risk-assessment.md`), and do not use it in place of a use-case intake form for a brand-new application (`use-case-intake-form.md`). The card documents what a model is and how it behaves; it does not decide whether the residual risk is acceptable. Keep the card current through the lifecycle rather than treating it as a one-time launch artifact.

## Model Identity And Overview

| Field | Entry |
|---|---|
| Model name and version | <name and semantic version> |
| Model type | <e.g. classifier, regressor, LLM, agentic system, recommender> |
| Model registry / inventory ID | <registry entry this card accompanies> |
| Owner / accountable role | <name and role> |
| Development team | <name or team> |
| Release / card version | <version> |
| Effective date | <YYYY-MM-DD> |
| Next review date | <YYYY-MM-DD> |

## Intended Use

Describe what the model is for, who it serves, and where it should and should not be applied, so it is not used in a context for which it is unsuited.

- Intended function: <what the model does, e.g. classify, recommend, generate, automate, decide>
- Intended users and audience: <who operates it and who consumes its output>
- Intended domain and context of use: <the specific business process, environment, and jurisdiction>
- Intended decision outcome: <how the output is used and what decision it informs>
- Known non-intended uses: <applications the model is NOT suited for>
- Deployment status: <development / evaluation / production / shadow / retired>

## Data Description

Document what the model was trained on and what it consumes in production, so its provenance and limitations are explicit.

- Training data sources: <data sets, systems, or vendors supplying training data>
- Data collection and annotation method: <how data was gathered and labeled>
- Data sensitivity: <public / internal / confidential / personal / sensitive personal / regulated>
- Contains personal or protected-attribute data: <yes/no — if yes, list the types>
- Data lineage and governance: <where data comes from and how it is governed>
- Known data quality issues and gaps: <errors, missingness, historical bias, or staleness>

## Performance And Evaluation

Record how the model was evaluated, on what data, and how it performed — broken out by relevant subgroups so the spread across groups is visible rather than being collapsed into one average.

- Evaluation procedure: <test sets, holdouts, cross-validation, or benchmark methodology>
- Primary performance metrics and thresholds: <e.g. accuracy, precision, recall, F1, calibration, quality>
- Overall results: <the headline performance against the agreed thresholds>
- Results by subgroup: <performance disaggregated by relevant demographic or other groups>
- Robustness and edge cases: <how it performs under expected variation and known adversarial cases>
- Evaluation limitations: <what the evaluation does not cover>

## Fairness And Bias Assessment

State which fairness metrics were chosen, why, what they showed across groups, and which decisions were made in response — not a single number but an explicit, auditable statement.

- Fairness metrics computed: <e.g. demographic parity, equalized odds, equal opportunity, calibration>
- Metric selection rationale: <why these metrics were the right ones and how priorities were ordered>
- Results across protected groups: <what the subgroup results showed, including any disparate impact>
- Known biases or proxy features: <describe any identified bias or correlated-proxy concerns>
- Trade-offs accepted: <what was given up in accuracy or parity, and why it was defensible>
- Mitigations applied: <reweighting, threshold adjustment, human review, or other corrective actions>

## Limitations And Considerations

Document the situations where the model is likely to underperform, so it is not applied somewhere it is unsuited.

- Known limitations: <where the model is likely to fail, mislead, or behave unpredictably>
- Suitable versus unsuitable contexts: <restate the boundary between intended and non-intended use>
- Environmental or dependence assumptions: <what must hold in production for the model to behave as intended>
- Security and integrity concerns: <prompt injection, misuse, data exposure, supply chain, tooling>
- Human oversight requirements: <how and when a person reviews or overrides the output>

## Monitoring And Maintenance

Define how the model is watched in production and how it is kept current, so that drift, degradation, or reintroduced bias is detected and responded to rather than improvised.

- Monitoring configuration: <metrics, alert thresholds, owners, and response runbook>
- Drift detection approach: <how data drift and concept drift are detected and who responds>
- Retraining / refresh cadence: <how often the model is re-evaluated or retrained and on what trigger>
- Incident and response path: <how problems are escalated and how the card is updated in response>
- Retirement plan: <how the model is decommissioned and its outputs archived>

## Approval And Review

Record who approved the card and its contents, and how it is kept current.

| Review field | Entry |
|---|---|
| Prepared by | <name and role> |
| Reviewed by | <name and role> |
| Approved by | <name and role> |
| Approval date | <YYYY-MM-DD> |
| Review trigger | <annual / on drift / on material change / on incident> |

## Completion

To complete this card: fill every labeled field, finalize the intended-use and non-intended-use statements, record the data description and its limitations, report performance broken out by subgroup rather than a single average, state the fairness metrics chosen and their results, document limitations and human oversight requirements, define the monitoring and drift-detection configuration, and obtain the approvals named above. Attach the card to the model-registry entry as the source-of-record, and refresh it whenever the model, its data, its context of use, or its performance changes materially or on the review trigger you set.

> **Synthesized from** `research-technical-controls.md` and `research-org-board-governance.md` and the ideas of *Responsible AI in the Enterprise*, *Responsible AI: Best Practices*, and *AI Fairness* (see `references/fairness-bias-accountability.md` and `references/ai-lifecycle-governance.md`). Fillable artifact of the `ai-governance` skill.
