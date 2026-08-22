# Architecture Governance

Architecture governance is a decision system, not a standing meeting. Its purpose is to keep consequential technology choices coherent while leaving routine, reversible choices with the people closest to the work. Select the governance path from the decision's consequences and evidence, not from an organization's preferred ceremony.

## Establish the Decision Context

Before choosing a process, capture:

- **Outcome:** the product, customer, operational, or organizational result sought.
- **Scope:** one component, one team, a shared capability, a portfolio, or the wider organization.
- **Reversibility:** how easily the choice can be changed, including data migration, contracts, training, and sunk operational work.
- **Risk and blast radius:** plausible harm, affected users and systems, failure propagation, and recovery options.
- **Regulation and obligations:** legal, contractual, safety, privacy, security, or audit constraints that require named controls or authority.
- **Cross-team impact:** coupling, shared interfaces, platform dependencies, duplicated investment, and coordination cost.
- **Evidence and uncertainty:** what is observed, what is assumed, and the smallest experiment or consultation that would reduce the important uncertainty.

Do not collapse these dimensions into a universal numeric threshold. A reversible decision with broad coordination cost may need advice or federation; a local decision can still require centralized authority when regulation or blast radius demands it.

## Choose a Governance Mode

Choose the least costly mode that controls the credible downside. A decision can move to a stronger mode when new evidence changes its consequence profile.

| Mode | Best fit | Minimum controls | Escalate when |
|---|---|---|---|
| **Automated policy** | The requirement is objective, repeatable, and machine-checkable, such as a required configuration or compatibility rule. | A stated rationale, an executable check, an owner, visible failure output, and a bounded exception path. | The check is a proxy for a judgment, exceptions become common, or the policy creates material cross-team or regulatory consequences. |
| **Federated decision** | A team or domain owns the outcome and the choice is local or reasonably reversible, while a shared convention prevents avoidable divergence. | Local decision authority, published decision and scope, compatibility expectations, and a route for affected peers to raise a conflict. | Shared interfaces, platform dependencies, duplicated investment, or accumulated divergence makes the choice enterprise-relevant. |
| **Advice process** | The proposer owns the decision but needs input from people who bear consequences or hold relevant expertise. This is useful for cross-team conceptual integrity without default veto power. | Named proposer and owner, identified consultees, written advice and dissent, response to material concerns, and a recorded decision. | Advice identifies an irreversible or high-blast-radius change, a mandatory control, unresolved authority conflict, or a need for portfolio-level coordination. |
| **Centralized review** | The choice is difficult to reverse, high impact, materially regulated, or spans teams that cannot resolve the trade-off locally. | A named decision authority, concise evidence package, alternatives and consequences, affected-team input, decision record, conditions, and an appeal or escalation route. | The authority lacks the required expertise, evidence is too weak for a responsible decision, or the review is redesigning implementation rather than governing the boundary. |

The modes are not maturity levels. Automated policy is not automatically more decentralized than advice, and a centralized review is not automatically better. Match authority, consultation, and automation to the failure modes the decision can create.

## Standards and Guardrails

Create a standard only when a shared rule produces more value than local variation. Each standard should state:

1. **Intent and benefit:** the problem or risk it addresses.
2. **Scope:** the systems, teams, lifecycle stages, and explicit exclusions.
3. **Requirement:** a testable rule, recommendation, or decision constraint.
4. **Owner and authority:** who maintains it and who can change it.
5. **Enforcement mode:** automated check, federated expectation, advice, or review.
6. **Exception path:** who may grant an exception, what evidence is needed, compensating controls, expiry or revisit conditions, and how exceptions are visible.
7. **Feedback signals:** implementation and operational evidence that may confirm, weaken, or invalidate it.

Avoid counting standards as a proxy for governance quality. A small organization may need several precise controls; a large regulated estate may need more. Prefer deleting, combining, automating, or narrowing a standard when it no longer earns its coordination cost.

## Decision Records and Advice

Use a concise decision record for any choice whose rationale or consequences will outlive the current conversation. Include the context, options, chosen path, owner, affected parties, assumptions, conditions, evidence, and reconsideration triggers. Use an ADR when the decision itself needs durable architectural history; this reference governs how to select the process, not the ADR format.

For advice processes, distinguish advice from approval. The proposer must seek input from people materially affected, consider the advice, and explain unresolved disagreement. Advice does not silently create a veto. If a mandatory control or authority boundary exists, name it and escalate rather than disguising it as consultation.

## Feedback From Delivery and Operations

Close the loop after implementation and during operation:

- Compare the intended outcome and constraints with observed behavior.
- Record surprises, incidents, support burden, delivery friction, cost, performance, adoption, and exceptions.
- Decide whether to keep, narrow, automate, revise, supersede, or retire the standard or radar entry.
- Update the decision record and notify affected owners; do not silently rewrite history.
- Promote recurring evidence into a better guardrail or experiment, and remove controls that no longer prevent a meaningful failure.

Operational evidence does not transfer incident command or service ownership to this skill. It supplies feedback for technology posture and governance decisions; operations teams retain operational response and reliability ownership.

## Exceptions and Proportional Escalation

An exception is a governed deviation, not an informal bypass. Record the requested scope, reason, affected assets, risk, compensating controls, accountable owner, expiry or review trigger, and evidence of closure. Emergency exceptions may use a shorter path, but they still require retrospective recording and review when the immediate risk is controlled.

Escalate when any of these becomes true:

- the choice cannot be reversed without material customer, data, contract, or migration cost;
- the blast radius or cross-team impact exceeds the local owner's authority;
- a regulatory, legal, safety, privacy, or security obligation requires a designated control owner;
- local decisions are creating incompatible interfaces, duplicated platforms, or portfolio-level cost;
- evidence is insufficient to understand a material downside;
- an exception is recurring, expanding, or compensating controls are failing.

De-escalate when an experiment reduces uncertainty, automation makes the rule objective, ownership becomes local, or the change is safely reversible. Stronger governance should not persist merely because it was used once.

## Neighboring Ownership

- **Enterprise architecture:** capability maps, business/technology alignment, operating models, target and transition states, and enterprise roadmaps belong there. This skill governs technology portfolio posture and decision paths.
- **ADR authoring:** durable records for consequential decisions and their fitness evidence belong there. This skill decides when and how governance is applied.
- **Implementation skills:** code, service design, API contracts, data models, migrations, and platform changes belong to their specialist owners. Governance sets boundaries and evidence; it does not design every implementation.
- **Secure software engineering:** threat modeling, security requirements, authentication/authorization, and secure implementation belong there. A security obligation may be an escalation input or automated guardrail here.
- **Operations and SRE:** deployment operations, incident command, SLOs, monitoring, and recovery runbooks belong there. Their evidence feeds governance; this skill does not replace operational ownership.

## Practical Output

Produce an artifact that makes authority and learning inspectable:

```markdown
# Governance decision: [subject]

## Context
- Outcome:
- Scope and affected teams:
- Reversibility and blast radius:
- Risk, regulation, and cross-team impact:
- Evidence and uncertainty:

## Chosen governance mode
[Automated policy | Federated decision | Advice process | Centralized review]

## Authority and controls
- Decision owner:
- Consultees or approving authority:
- Required checks or conditions:
- Exception path and compensating controls:

## Feedback plan
- Implementation evidence:
- Operational signals:
- Reconsideration triggers:
- Owner and next review point:

## Boundary and links
- Radar entry or standard:
- ADR, if needed:
- Specialist implementation, security, or operations owners:
```
