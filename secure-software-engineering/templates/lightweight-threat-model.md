# Lightweight Threat Model

> **Confidentiality:** A completed threat model can expose system boundaries and weaknesses. Store it with access controls appropriate to sensitive project security information.

## When To Use

Use before implementing a new feature, integration, service, sensitive data flow, tenant boundary, or AI capability. Adapt the prompts to the risk; this is a thinking tool, not a compliance form.

## When Not To Use

Do not use this as evidence that an existing system has been assessed. Use `security-audit-methodology` for authorized assessment work.

## System Overview

What does the system or change do? What data and actions flow through it?

## Assets

| Asset | Sensitivity or harm if compromised | Location or flow | Owner |
|---|---|---|---|
| <asset> | <harm> | <where> | <owner> |

## Actors And Authority

| Actor or workload | Trust basis | Current authority | Required authority | Explicitly denied |
|---|---|---|---|---|
| <actor> | <credential or boundary> | <current> | <needed> | <denied> |

## Data Flows And Trust Boundaries

Describe each flow and where trust changes. Include clients, services, stores, workers, external providers, build systems, and AI model/retrieval/tool paths when applicable.

For a diagram, ask the `c4-diagramming` skill to render the components and labeled boundaries from this description.

## Assumptions To Test

| Assumption | Why it matters | Evidence or test | Owner | Status |
|---|---|---|---|---|
| <assumption> | <impact> | <evidence> | <owner> | <open/verified> |

## Component Threats

Use applicable STRIDE prompts from `security-audit-methodology/references/threat-modeling.md` or another suitable method.

| Component or boundary | Abuse or failure case | Preconditions | Mitigation | Verification | Residual risk |
|---|---|---|---|---|---|
| <component> | <case> | <conditions> | <control> | <test/evidence> | <risk> |

## AI Boundaries (If Applicable)

| Boundary | Untrusted content | Allowed capability | Server-side enforcement | Approval gate |
|---|---|---|---|---|
| <prompt/retrieval/tool> | <content> | <scope> | <policy> | <when> |

## Decisions And Follow-Up

| Risk or decision | Likelihood | Impact | Chosen mitigation | Owner | Delivery phase | Exception or review date |
|---|---|---|---|---|---|---|
| <item> | <low/medium/high> | <low/medium/high> | <action> | <owner> | <phase> | <date or none> |
