# Third-Party AI Due Diligence Questionnaire

> **Confidentiality:** A completed questionnaire records what an external AI engagement — a hosted model API, pretrained weights, a licensed dataset, an ML platform, or a consultancy — brings in, what it could harm, and what the contract and controls must protect against. Store it with access controls appropriate to procurement, governance, and board-oversight information. This template implements the due-diligence and supply-chain discipline described in `references/procurement-third-party-and-board-oversight.md`, proportional to the risk tier assigned under `references/risk-management-and-frameworks.md`. It is a working questionnaire, not legal advice; contract, liability, and regulatory terms should be confirmed with qualified counsel at use time.

## When To Use

Use this questionnaire to investigate a proposed third-party AI engagement **before** you commit to it, so that you accept the relationship with your eyes open rather than discover its flaws after signing. Run it on intake for any vendor, model, dataset, or service that will support a governed use case, and complete it in full for anything that lands in a medium or high risk tier. Keep the completed questionnaire as the source-of-record that justifies the onboarding decision, and revisit it when the system, the vendor, its subprocessors, or the surrounding risk profile changes. It is the intake companion to `model-risk-assessment.md`; use that worksheet for the full inherent-versus-residual scoring of a model you are already engaged with.

## When Not To Use

Do not use this questionnaire as the routine intake form for an internally built model or use case (that is `use-case-intake-form.md`), and do not use it as a substitute for ongoing vendor monitoring and exit planning, which the lifecycle discipline describes. This is a point-in-time diligence artifact that characterizes an external engagement and sets the contract terms; monitoring, audit, and exit keep those commitments honest after onboarding.

## Engagement Identity

| Field | Entry |
|---|---|
| Engagement / vendor name | <vendor, model, or service name> |
| Due-diligence ID | <reference, e.g. DD-2026-032> |
| Engagement type | <hosted model API / open-source weights / licensed dataset / ML platform / professional service> |
| Supporting use case | <linked intake-form ID and use case name> |
| Risk tier (provisional) | <low / medium / high> |
| Diligence owner | <name and role> |
| Reviewing authority | <procurement / AI council / risk committee / board committee> |
| Diligence date | <YYYY-MM-DD> |
| Status | <draft / in review / approved / approved with conditions / rejected> |

## Purpose And Scope (Map)

Establish what the component is, how it is used, and where its risks and benefits arise across the supply chain, as the governance reference directs.

- Intended function of the component: <what it does, e.g. generate, classify, recommend, automate, enrich>
- Use case and deployment context: <the business process, environment, and jurisdiction it supports>
- How it is integrated: <API / fine-tuned / embedded library / fully hosted / human-supervised>
- Affected parties: <who operates it and who is affected by its output>
- Expected benefit and success metric: <the value it delivers and how success is measured>
- Alternatives considered: <in-house build or a different vendor, and why they were set aside>

## Provider Identity And Standing

Assess who owns and operates the component, because its stability, jurisdiction, and accountability shape your exposure.

- Provider name and legal entity: <registered name and corporate form>
- Location and jurisdiction: <country / state, and governing law>
- Size and financial stability: <scale, funding, or financial indicators of continuity>
- Relevant regulatory status: <whether the provider is subject to a regime relevant to your data or use>
- Ownership and subprocessors: <who controls the provider and which subprocessors it relies on>
- Reputation and track record: <public incidents, known weaknesses, or sanctions the team is aware of>

## Data Flows And Handling

Enumerate the data that moves to and from the vendor. Personal, regulated, or proprietary data raises lawful-basis, transfer, and confidentiality duties.

- Inputs shared with the vendor: <what data is sent, and for what purpose>
- Outputs and their use: <what the vendor returns and how you act on it>
- Data sensitivity: <public / internal / confidential / personal / sensitive personal / regulated>
- Contains personal or special-category data: <yes/no — if yes, list the types>
- Lawful basis and transfer basis: <the basis relied on and any cross-border mechanism>
- Vendor data handling commitments: <training, retention, storage location, reuse, and subprocessors>

## Model And Capability Assessment

Characterize the model itself so you know what you are relying on and how to validate it.

- Model origin and lineage: <who built it, on what data, and what its provenance is>
- Version and registry entry: <exact model version and any AI BOM / model card references>
- Capabilities and limitations: <what it does well and where it is known to fail>
- Intended vs allowed use: <vendor's stated intended use and any restricted uses>
- Known biases and fairness data: <what bias testing the vendor provides and its results>
- Performance and accuracy evidence: <benchmarks, evaluations, or guarantees supplied>

## Security And Privacy Controls

Ask for evidence of the vendor's controls rather than accepting assertions at face value.

- Security certifications and audits: <e.g. SOC 2, ISO 27001, NIST-based assessments — and their scope>
- Privacy certifications and practices: <e.g. GDPR/DPA posture, privacy-enhancing measures>
- Access control and data isolation: <how your data is isolated from other tenants or use>
- Encryption in transit and at rest: <the mechanisms in place and their scope>
- Model-governance practices: <how the vendor governs its own models and changes>
- Right to audit or review evidence: <whether you can inspect the controls you rely on>

## Incident, Reliability, And Exit

Confirm what happens when things go wrong and how you would leave.

- Incident-notification commitment: <the window and format for notifying you of a material incident>
- Uptime and performance commitments: <service-level targets and remedies for breach>
- Liability and indemnification terms: <how liability and IP indemnity are allocated>
- Data return and deletion on exit: <what happens to your data when the contract ends>
- Migration and transition assistance: <the path for moving off the vendor>
- Dependency and concentration: <how critical this vendor is and any concentration risk it creates>

## Proportionality And Approvals

Weigh how deep this diligence must go and who must sign off, driven by inherent risk, impact, and likelihood.

- Inherent risk drivers: <the factors that most raise the risk of this engagement>
- Required diligence depth: <standard / enhanced / full assessment plus controls review>
- Contractual commitments to encode: <data handling, subprocessor disclosure, notification, audit rights, exit>
- Required approvals: <who must sign off at this tier>
- Decision and rationale: <approved / rejected / approved with conditions — and why>
- Decision recorded by: <name and role> on <YYYY-MM-DD>

## Completion

To complete this questionnaire: fill every labeled field, classify the engagement and assign a provisional risk tier, characterize the provider and its jurisdiction, enumerate the data flows and the vendor's handling commitments, review the model's provenance and capabilities, record the security and privacy evidence you actually obtained, confirm the incident, reliability, and exit terms, and route the outcome to the reviewing authority named above. Obtain the required approvals and record the decision as the source-of-record that every later onboarding, monitoring, and audit step calibrates against. Revisit the questionnaire whenever the system, the vendor, its subprocessors, or the surrounding risk profile changes materially.

> **Synthesized from** `references/procurement-third-party-and-board-oversight.md`, which draws on *The AI Product Manager's Handbook* and *Developing Cybersecurity Programs and Policies*, together with `research-org-board-governance.md`. Fillable artifact of the `ai-governance` skill; educational context, not legal advice.
