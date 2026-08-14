# Authority and Escalation

## Before constrained action

Record the access route, identity and privilege needed, approved egress,
systems and data in scope, change window, reviewer, rollback or recovery path,
external-boundary verification, and evidence that the action succeeded. Load
[remote-systems-administration](../../../remote-systems-administration/SKILL.md)
for its operational method rather than inventing one here.

## Authority table

| Decision | Proceed only when | Escalate to |
|---|---|---|
| Scope, sequence, and thin slice | Charter names accountable lead and sponsor | Engagement sponsor |
| Access and privilege | Authorized identity, least privilege, and route are recorded | System owner or security owner |
| Security boundary | Trust boundary, threat assumptions, and controls are reviewed | Security owner |
| Privacy and data use | Purpose, classification, access, retention, and deletion are explicit | Privacy/data owner |
| Irreversible change | Recovery is tested or an authorized exception is recorded | Service or change owner |
| Material cost or quota | Budget owner accepts estimate and guardrail | Budget owner |
| External commitment | Contract, customer, or public promise is authorized | Business owner |
| Business priority or portfolio choice | Product or executive authority decides | Product/business owner |

When authority or evidence is missing, stop the action, record the blocker,
preserve safe read-only discovery, and escalate with the smallest decision
needed. Do not use urgency, stakeholder enthusiasm, or a working demo as an
authority substitute.

## Applied AI release boundary

An applied-AI demo is not production-ready without a representative baseline,
adversarial or failure cases, risk constraints, evaluation results, an owner for
residual risk, rollout and rollback evidence, and an explicit release decision.
Route evaluation details to [agent-evals-and-observability](../../../agent-evals-and-observability/SKILL.md)
and readiness details to [production-readiness](../../../production-readiness/SKILL.md).
