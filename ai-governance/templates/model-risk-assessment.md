# Model Risk Assessment & Tiering Worksheet

> **Confidentiality:** A completed assessment records inherent and residual risk, mitigations, and a tiering decision for a specific model. Store it with access controls appropriate to governance and board-oversight information. This template implements the NIST AI Risk Management Framework functions — Govern, Map, Measure, Manage — and the model risk tiering discipline described in `references/risk-management-and-frameworks.md`. It is a working worksheet, not a legal opinion; framework details should be confirmed against current NIST and ISO releases at use time.

## When To Use

Use this worksheet to run a single-model risk assessment and assign a risk tier before development deepens, at deployment, and whenever the model, its data, its context of use, or its controls change materially. It is the companion to the intake form: `use-case-intake-form.md` captures intent and initial classification, while this worksheet performs the full inherent-versus-residual assessment that justifies the tier. Complete it for any model whose tiering decision must be auditable and defensible. For documenting what a model is and how it behaves rather than how risky it is, use `model-card.md`.

## When Not To Use

Do not use this worksheet as the intake gate for a brand-new use case (that is `use-case-intake-form.md`), and do not use it as a substitute for ongoing post-deployment monitoring and drift detection, which the `model-card.md` template and the lifecycle gates describe. This is a point-in-time assessment that records the analysis and decisions; monitoring keeps those decisions honest after launch.

## Assessment Identity

| Field | Entry |
|---|---|
| Model / system name | <model or system name> |
| Assessment ID | <assessment reference, e.g. MRA-2026-017> |
| Model inventory / registry ID | <registry entry this assessment updates> |
| Use-case link | <linked intake-form ID, if applicable> |
| Assessor | <name and role> |
| Reviewing authority | <steward / AI council / board committee> |
| Assessment date | <YYYY-MM-DD> |
| Status | <draft / in review / approved / approved with conditions / rejected> |

## Purpose And Context (Map)

Establish the context of the AI system, as the NIST Map function directs: who the actors are, what the system is for, and where its risks and benefits arise across the life cycle.

- Intended function: <what the model does, e.g. classify, recommend, generate, automate, decide>
- Context and domain of use: <the specific business process, environment, and jurisdiction>
- Users and affected parties: <who operates it and who is affected by its output>
- Expected benefit and success metric: <the value it is meant to deliver and how success is measured>
- Alternatives considered: <non-AI or lower-risk alternatives and why they were set aside>
- Deployment environment and reach: <scale of exposure, e.g. users, transactions, or decisions per year>

## Data And Inputs

Describe what trains and feeds the model. Sensitive, high-volume, or personal data raises inherent risk and the controls required.

- Training and input data sources: <data sets, systems, or vendors supplying data>
- Data sensitivity: <public / internal / confidential / personal / sensitive personal / regulated>
- Contains personal or special-category data: <yes/no — if yes, list the types>
- Data lineage and provenance: <where data comes from and how it is governed>
- Data quality and known limitations: <gaps, errors, or biases you are aware of>
- Retention, minimization, and privacy: <how long data is kept and what is minimized>

## Autonomy And Decision Impact

Classify how much the model decides and how consequential its output is. This is a principal driver of the inherent risk tier.

- Level of autonomy: <human-in-the-loop review / human-on-the-loop review / fully automated>
- Decision type: <advisory / recommendation / direct action / automated decision>
- Decision impact: <informational / operational / financial / life- or liberty-affecting>
- Opportunity for human override: <how and when a person can review or reverse the outcome>
- Affected population: <who bears the consequences and any protected groups involved>

## Inherent Risk Assessment (Measure)

Score the risk the model would pose with no controls, validation, or mitigation applied — the danger present simply because the model exists and is used in this context. Rate likelihood and impact, then derive an inherent risk tier.

| Risk factor | Likelihood (1–5) | Impact (1–5) | Notes |
|---|---|---|---|
| Bias / fairness | <1–5> | <1–5> | <basis for the scores> |
| Data quality and privacy | <1–5> | <1–5> | <basis for the scores> |
| Accuracy / reliability | <1–5> | <1–5> | <basis for the scores> |
| Autonomy / decision impact | <1–5> | <1–5> | <basis for the scores> |
| Security / integrity | <1–5> | <1–5> | <basis for the scores> |
| Regulatory / legal exposure | <1–5> | <1–5> | <basis for the scores> |

- Inherent risk tier: <low / medium / high — justify from the scores above>
- Primary risk drivers: <list the factors that most raise inherent risk>
- Known limitations and underperformance contexts: <where the model is likely to fail or mislead>

## Risk Tiering Decision

Assign the model to a governance tier so the depth of review, validation, and monitoring matches the stakes. The tier should weight inherent risk over residual risk so the review depth tracks the true stakes, not just what strong controls currently hide.

- Assigned risk tier: <low / medium / high>
- Tiering rationale: <why this tier, referencing the drivers and scoring above>
- Required review depth: <standard / enhanced / full assessment + controls review>
- Required approvals: <who must sign off at this tier>
- Tiering decision recorded by: <name and role> on <YYYY-MM-DD>

## Mitigations And Controls (Manage)

Record the controls that bring inherent risk down, then re-score to estimate residual risk. The gap between inherent and residual is the value of the control environment.

| Control / mitigation | Owner | Status | Reduces which risk |
|---|---|---|---|
| <e.g. human-in-the-loop review> | <owner> | <planned / in place / verified> | <risk factor> |
| <e.g. subgroup fairness testing> | <owner> | <planned / in place / verified> | <risk factor> |
| <e.g. input/output monitoring and drift detection> | <owner> | <planned / in place / verified> | <risk factor> |
| <e.g. security and red-teaming> | <owner> | <planned / in place / verified> | <risk factor> |

## Residual Risk Assessment

Re-score the model with controls applied to determine the realistic risk the business actually carries day to day.

- Residual likelihood: <1–5>
- Residual impact: <1–5>
- Residual risk tier: <low / medium / high>
- Risk appetite check: <is residual risk within the organization's accepted appetite? state how you know>
- If residual risk exceeds appetite: <what additional controls are required, or why the model should not ship as-is>

## Risk Register And Escalation

Link this assessment to the central risk register and to the escalation path so the finding is acted on rather than filed away.

- Risk-register entry ID: <registry reference for the residual risk>
- Escalation trigger: <what bumps this model to a higher review tier or to the council / board>
- Review cadence: <when this assessment is revisited, e.g. annually, on drift, on material change>
- Linked artifacts: <model card, monitoring configuration, audit logs, incident reports>

## Completion

To complete this assessment: fill every labeled field, score inherent risk honestly before considering controls, assign and justify the tier, list every planned or existing control with its owner and status, re-score to residual risk and check it against the organization's appetite, link the entry to the risk register, and obtain sign-off from the reviewing authority named above. Record the tiering decision as the source-of-record that every later lifecycle gate — evaluation, deployment, monitoring, and retirement — calibrates against. Revisit the worksheet whenever the model, its data, its context of use, or its controls change materially, or on the review cadence you set here.

> **Synthesized from** `research-standards.md` and `research-technical-controls.md` and the ideas of *Responsible AI in the Enterprise* and *Platform and Model Design for Responsible AI* (see `references/risk-management-and-frameworks.md`). Fillable artifact of the `ai-governance` skill.
