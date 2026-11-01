# Agent-trust routes

Choose the user's decision first. This is a human-readable router and worked
handoff guide for existing skills, not a new methodology, install pack, permission
grant, or runtime alias. Load only the specialist needed at the current decision.
Carry source revisions, evidence limits, decision owner, scope and expiry through
handoffs; unknown or missing evidence remains unknown.

| User question | First owner and next handoff | Evidence exchanged | Decision owner | Stop / escalation | Disposition and limit |
|---|---|---|---|---|---|
| May this agent act? | [ai-governance](../ai-governance/SKILL.md), earned autonomy → [agent-production-operations](../agent-production-operations/SKILL.md); security for enforcement | Capability/environment/action scope, policy ceiling, grant expiry/revocation, counterevidence, readiness and current control state | Accountable human with grant authority; operator enforces that decision | Missing/expired grant, breached ceiling, unavailable mandatory controls → hold and authorized escalation | Maintain/expand/reduce/suspend/revoke scope. Evaluation or readiness is not a permission grant |
| May this capability enter our environment? | [ai-governance](../ai-governance/SKILL.md), capability admission → [secure-software-engineering](../secure-software-engineering/SKILL.md) for threat/enforcement review | Pinned component revision/configuration, provenance, permissions, overlap, dependencies, exit/rollback and re-review triggers | Environment's admission authority | Unknown provenance, unsupported permissions, unresolved risk or unapproved update → defer/reject | Admit bounded revision/configuration, defer, reject or retire. Admission alone grants no runtime action |
| Should we scale this AI pilot? | [ai-operating-economics](../ai-operating-economics/SKILL.md) → evals/analytics/financial specialists as needed, then governance for any authority change | Workflow outcomes, countermetrics, displaced/review/exception cost, user/worker effects, uncertainty, causal limits and stop triggers | Business/workflow owner; governance owner for expanded authority | Benefits unsupported, subgroup harm, review overload or exceeded bounds → constrain/defer/stop | Adopt/scale/constrain/redesign/retire. Install counts, saved tokens and pilot throughput alone do not establish value |
| Grill this specification or proposal | [product-discovery](../product-discovery/SKILL.md), artifact-first review → relevant product/engineering owner after unresolved decisions are explicit | Versioned draft, one-question exchanges, assumptions, contradictions, author decisions and targeted proposed patch | Draft's accountable decision-maker, not automatically its author | User stops, question budget expires, missing authority or unresolved consequential contradiction → stop/defer with gaps | Traceable proposed edits or no edit. Author agreement does not validate customer demand or technical safety |
| Why did this agent fail, and may it resume? | [systematic-debugging](../systematic-debugging/SKILL.md) for cause; operations for current containment; [incident-learning](../incident-learning/SKILL.md) for incident closure; governance for authority | First-divergence evidence, tool/state records, effects, incident disposition, repair/retest, current grants and independent control receipt | Incident/runtime owner contains; accountable authority decides resume scope | Uncontained effects, unknown cause where required, unverified repair or expired/revoked grant → remain held | Diagnose/contain/repair/hold; resume only under current authorized scope. A patch, correct answer or closed ticket is insufficient |
| Can the agent weaken its own controls? | Governance rights registry → security enforcement → harness child coverage → operations live receipt; [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) challenges evidence | Protected asset versions, operation-specific rights, independent enforcement/monitor/sink evidence, child coverage, exception expiry and restoration | Independent authorized human/control owner, never the controlled agent alone | Missing, degraded, redirected or suppressed mandatory control → control-integrity incident; hold/contain/terminate | Refuse unauthorized weakening; bounded approved maintenance only with independent compensating controls. Policy prose is not live enforcement |
| Can humans supervise this volume of agent work? | [operational-design](../operational-design/SKILL.md) for queues/handoffs; [org-design](../org-design/SKILL.md) for competence/role decisions; economics and governance for scope/cost/authority | Output volume/variability, work needing review, qualified reviewer availability, queue age, severity, rework, reserved decisions, cost/outcome evidence | Workflow/people owner and accountable authority for automation scope | Unreviewable workload, absent qualifications, decision rights or stop ability → reduce scope, slow/hold automation and escalate | Staff/reassign/instrument/sample only within approved risk bounds, constrain automation, or request more evidence. No validated cross-organization capacity method is claimed |

<a id="failure-and-resumption"></a>
## Failure and resumption

Worked example (synthetic): a support agent gives the right reply but its tool
call changes an account without the required approval. Operations contains current
side effects. Debugging locates the first unauthorized action; evals distinguishes
answer correctness from trajectory failure; incident-learning records cause and
repair evidence. Governance reviews whether the grant should be reduced or remain
suspended. Operations verifies current controls and revocation before any authorized
resumption. The diagnostic report itself cannot authorize restart.

<a id="protected-controls"></a>
## Protected controls

Worked example (synthetic): a worker proposes redirecting alerts to speed a batch.
The task owner cannot silently override the independent control owner. Use the
registry to identify propose/approve/deploy/modify/disable/restore rights; inspect
external enforcement and current sink delivery. If redirection already occurred,
record a control-integrity incident and use the protected alternate escalation
path. A child's coverage must be established for its actual identity and scope.

Detailed protected-control work is tracked in [#759](https://github.com/magnus919/agent-skills/issues/759)
and monitor-quality evidence in [#760](https://github.com/magnus919/agent-skills/issues/760).
Use their verified merged artifacts when available; the router does not manufacture
completion evidence for dependencies.

<a id="supervisory-capacity"></a>
## Supervisory capacity

Worked example (synthetic): an agent creates 100 proposals/hour but only 10 can be
reviewed by qualified staff. Do not treat proposal throughput as accepted output.
Determine which decisions require full review, available qualified attention,
queue age and severity, context/rework cost and who may stop automation. Constrain
generation or action scope while those conditions are unresolved. Sampling is not
an automatic substitute for reserved human decisions.

[#762](https://github.com/magnus919/agent-skills/issues/762) validates whether a shared
assessment adds value in actual or faithfully reconstructed organizations. Until
that gate is met, route to existing methods and report uncertainty; do not advertise
a validated capacity bundle. The solo-business journey likewise remains gated by
actual-user evidence in [#758](https://github.com/magnus919/agent-skills/issues/758).

## Near misses

- “Fix this Kubernetes alert rule” → the named [kubernetes](../kubernetes/SKILL.md)
  or [grafana](../grafana/SKILL.md) tool owner as appropriate; the router does not
  operate an alert backend.
- “Approve this investment because our agent says it is safe” → do not approve;
  obtain independently supported evidence and the actual decision authority.
- “Implement an approved spec” → [neckbeard](../neckbeard/SKILL.md), with
  [implementation-planning](../implementation-planning/SKILL.md) if sequencing is
  unresolved. Draft interrogation is not mandatory for settled requirements.
- “Review this code diff” → [code-review](../code-review/SKILL.md), not a substitute
  customer interview or whole-system security assessment.
- “Secretly score employee loyalty” → refuse covert profiling; chief-of-staff
  language does not authorize surveillance or create a monitoring route.
- “Fine-tune a model” → [ml-engineering](../ml-engineering/SKILL.md) and the chosen
  tool; harness engineering does not own model-weight training.

## Completion

A routing result identifies the next owner, evidence, human decision and stop
condition, while preserving unknowns. It does not execute the handoff, confer
permission, or prove the specialist outcome. If no existing owner fits, record the
precise uncovered job before considering a new skill.
