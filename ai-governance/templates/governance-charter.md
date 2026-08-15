# AI Governance Council Charter

> **Confidentiality:** A completed charter names accountable executives, decision rights, and escalation paths. Store it with access controls appropriate to governance and board-oversight information. This template instantiates the council terms of reference described in `references/governance-operating-model.md`.

## When To Use

Use this charter to stand up (or refresh) any AI governance body — an AI ethics council, an AI risk council, an enterprise AI committee, or a board-level technology committee. The operating model reference explains the tiered council structure; this template turns the council's purpose, membership, responsibilities, decision rights, cadence, and reporting lines into a written terms of reference. Complete it when the council is created and review it at least annually or whenever the operating model or risk profile changes.

## When Not To Use

Do not use this template as a substitute for an individual role's job description, and do not use it to assign operational work that belongs to stewards and functional owners. A charter governs how a body deliberates and decides; it is not a RACI for every task. Use `model-risk-assessment.md` for single-model reviews and `use-case-intake-form.md` for routing individual use cases.

## Charter Meta

| Field | Value |
|---|---|
| Council name | `<name, e.g. Enterprise AI Risk Council>` |
| Charter version | `<version, e.g. 1.0>` |
| Effective date | `<YYYY-MM-DD>` |
| Next review date | `<YYYY-MM-DD>` |
| Sponsor / accountable executive | `<name and role>` |
| Status | `<draft / ratified / amended>` |

## Purpose

State, in one to three sentences, why the council exists and what outcomes it is accountable for. Anchor it to a mission statement so every decision can be traced back to it.

- Council purpose: `<one-to-three-sentence statement of the mandate and the outcomes it owns>`
- What the council is accountable for: `<list the decisions, standards, and risk approvals it must own>`
- What the council must NOT decide alone: `<identify matters that require executive sign-off or board approval>`

## Membership

List the representative roles and named individuals. A cross-functional council should bring together legal, risk, compliance, privacy, security, data, product, and engineering. Note alternates so the body is never blocked by a single person's absence.

| Role | Representative | Alternates | Term / rotation |
|---|---|---|---|
| <council chair> | <name> | <name> | <term> |
| <legal / compliance> | <name> | <name> | <term> |
| <risk management> | <name> | <name> | <term> |
| <privacy / data protection> | <name> | <name> | <term> |
| <security> | <name> | <name> | <term> |
| <data / product / engineering> | <name> | <name> | <term> |
| <business unit / domain steward> | <name> | <name> | <term> |

- Quorum: `<minimum number or roles required for a valid meeting>`
- Decision method: `<consensus / majority / by chair with recorded dissent>`

## Responsibilities

List the standing duties of the council. Tie each duty to the stage of the AI life cycle or the risk framework where it bites.

- Set and maintain AI policy, standards, and principles: <duty details>
- Review and approve higher-risk AI use cases and their residual risk: <duty details>
- Own the risk register and ensure entries above threshold are escalated: <duty details>
- Review monitoring, incident, and drift signals and direct responses: <duty details>
- Oversee third-party and procured AI diligence: <duty details>
- Prepare aggregate risk reporting for the executive team and board: <duty details>

## Decision Rights And Escalation

Make explicit who the council can decide, who it must consult, who it must inform, and how disputes are raised. Reference the operating model's RACI so one person is accountable for each outcome.

| Matter | Decision right | Consulted | Informed | Escalation path |
|---|---|---|---|---|
| Approve low-risk use case | <who decides> | <roles> | <roles> | <path> |
| Approve medium-risk use case | <who decides> | <roles> | <roles> | <path> |
| Approve high-risk use case | <who decides> | <roles> | <roles> | <path> |
| Approve residual-risk exception | <who decides> | <roles> | <roles> | <path> |
| Declare material incident | <who decides> | <roles> | <roles> | <path> |

- Escalation trigger and path: <describe when a matter must be raised to the executive sponsor, CEO, or board>
- Dispute resolution: <describe how a deadlock or contested decision is resolved and recorded>

## Meeting Cadence And Operation

Define how often the council meets, what it reviews, and how members prepare. The operating model reference notes that councils need a regular cadence and ground rules for psychological safety so that honest discussion, including disagreement, is possible.

- Meeting frequency: <e.g. every other week, monthly, quarterly>
- Session length: <e.g. 60–90 minutes>
- Standing agenda items: <list recurring items, e.g. new use cases, risk register, incidents, metrics>
- Pre-read expectations: <describe what members review before the meeting>
- Ground rules for discussion: <state expectations for candid disagreement and psychological safety>
- Record keeping: <state where decisions, minutes, and dissents are recorded and retained>

## Reporting And Oversight

Describe how the council reports up (to the executive sponsor and board) and down (to stewards and operating owners), consistent with the board tier's "noses in, fingers out" oversight posture.

- Reports to: <executive sponsor, CEO, board committee — name them>
- Report cadence and contents: <what is reported, how often, and to whom>
- Material-incident briefing path: <how the board is briefed promptly on material incidents>
- Interactions with stewards and operating owners: <how decisions are communicated and enforced downstream>

## Effectiveness Review

Define how the council evaluates its own performance so the charter stays a living instrument, not a filed artifact.

- Review trigger: <annual / on operating-model change / on material incident>
- Effectiveness criteria: <list measurable criteria, e.g. decisions within SLA, incidents caught early, documented dissent>
- Success measures: <list the metrics the council watches and reports>
- Amendment process: <who can change the charter and how it is ratified>

## Completion

To complete and ratify this charter: fill every labeled field, confirm each named member and alternate, obtain sign-off from the accountable executive (and board sponsor where applicable), record the ratification date and version, and store the ratified copy in the shared governance location referenced by the operating model. Schedule the next review date before circulating the final version.

> **Synthesized from** `research-org-board-governance.md` and the ideas of *Designing Data Governance from the Ground Up* and the *Data Governance Handbook* (see `references/governance-operating-model.md`). Fillable artifact of the `ai-governance` skill.
