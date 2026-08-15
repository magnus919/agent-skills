# AI Use-Case Intake Form

> **Confidentiality:** A completed intake form describes data, decisions, and risk. Store it with access controls appropriate to the sensitivity of the use case. This template turns the earliest lifecycle gate and the risk-register entry described in `references/risk-management-and-frameworks.md` and `references/ai-lifecycle-governance.md` into a fillable form.

## When To Use

Use this form to open a governed lifecycle for any proposed or newly discovered AI use case — whether built in-house, procured from a vendor, or embedded in an inherited system. Completing it routes the use case into the risk register and to the correct depth of review before significant investment, model training, or deployment. Submit it at the intake stage; revisit it when the use case, data, or context changes materially.

## When Not To Use

Do not use this form as a substitute for a full single-model risk assessment. If the use case already exists and you are evaluating an individual model's residual risk, use `model-risk-assessment.md`. This form captures intent and initial classification; it does not replace monitoring, drift detection, or incident response after deployment.

## Use-Case Identity

| Field | Entry |
|---|---|
| Use-case name | <short descriptive name> |
| Use-case ID | <registry ID, e.g. UC-2026-014> |
| Submitted by | <name and role> |
| Submitted date | <YYYY-MM-DD> |
| Business unit / domain | <unit> |
| Status | <new / triaged / in review / approved / rejected / live / retired> |

## Purpose And Context

Describe what the use case does, who it serves, and why it is being built or adopted.

- Problem statement: <what problem the AI system addresses and for whom>
- Intended function: <what the system does, e.g. recommend, classify, generate, automate, decide>
- Users and affected parties: <who operates it and who is affected by its output>
- Expected benefit: <what value is expected, with a rough scale or metric>
- Alternatives considered: <non-AI or lower-risk alternatives and why they were set aside>

## Data And Inputs

Describe the data that trains and feeds the system. Sensitive, high-volume, or personal data raises the inherent risk and the controls required.

- Primary data sources: <data sets, systems, or vendors supplying data>
- Data sensitivity: <public / internal / confidential / personal / sensitive personal / regulated>
- Contains personal or special-category data: <yes/no — if yes, list the types>
- Data lineage and provenance: <where data comes from and how it is governed>
- Data quality and known limitations: <describe quality issues, gaps, or biases you are aware of>
- Retention and minimization: <how long data is kept and what is minimized>

## Autonomy And Decision Impact

Classify how much the system decides and how consequential its output is. This drives the tier.

- Level of autonomy: <human-in-the-loop / human-on-the-loop / fully automated>
- Decision type: <advisory / recommendation / direct action / automated decision>
- Decision impact: <informational / operational / financial / life- or liberty-affecting>
- Scale of exposure: <approximate users, transactions, or decisions affected per year>
- Opportunity for human override: <how and when a person can review or reverse the outcome>

## Initial Risk Classification

Record the inherent risk (with no controls applied) and any immediate risk considerations, aligned with the tiering discipline in `references/risk-management-and-frameworks.md`.

- Inherent risk tier: <low / medium / high — justify>
- Primary risk drivers: <list factors such as sensitive data, autonomy, decision impact, volume>
- Known biases or fairness concerns: <describe any identified bias or disparate-impact risk>
- Known security or integrity concerns: <prompt injection, data exposure, misuse, tooling, supply chain>
- Suggested review depth: <standard / enhanced / full assessment + tiering>
- Proposed controls to reach acceptable residual risk: <list candidate mitigations>

## Review Routing

Route the use case to the right level of review based on its tier, and record the decision.

| Routing field | Entry |
|---|---|
| Assigned reviewer / assessor | <name and role> |
| Review path | <steward only / AI council / board committee> |
| Required approvals | <who must sign off before development or deployment> |
| Escalation trigger | <what bumps the use case to a higher review tier> |
| Linked risk-register entry | <registry reference, if created> |

## Decisions And Next Steps

Record the outcome and the follow-up actions so the intake is closed out.

- Decision: <approved / approved with conditions / deferred / rejected / referred>
- Conditions or mitigations required: <list any conditions attached to approval>
- Next steps and owners: <describe the next actions, owners, and due dates>
- Re-review trigger: <what change would require the intake to be reopened>

## Completion

To complete this intake: fill every labeled field, confirm the submitted-by and business owner, perform the initial risk classification honestly (inherent risk first), route the form to the assigned reviewer through the path your operating model defines, record the decision and any conditions, and file the completed entry in the risk register as the source-of-record. Revisit the form whenever the use case, data, context, or risk tier changes materially.

> **Synthesized from** `research-standards.md` and `research-technical-controls.md` and the ideas of *Responsible AI in the Enterprise* and *Platform and Model Design for Responsible AI* (see `references/risk-management-and-frameworks.md` and `references/ai-lifecycle-governance.md`). Fillable artifact of the `ai-governance` skill.
