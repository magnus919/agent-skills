# Six-Level Governance Framework

The Six-Level Governance (6L-G) framework is a practical cross-cutting overlay for governing
Generative AI systems. It comes from *AI Governance* by Engin Bozdag and Stefano Bennati, and is
included here as an author-developed operating model, not as a NIST, ISO, or regulatory term. Use it
alongside the named frameworks in `risk-management-and-frameworks.md`, not as a replacement for them.

**Use this reference when:** an organization needs a repeatable governance loop across strategy,
risk assessment, implementation, launch, operations, and learning; when a review is becoming a
checklist with no evidence; or when a deployment posture or material change requires governance
controls to be re-applied.

## What 6L-G adds

`ai-lifecycle-governance.md` answers **when** a system moves through ideation, data, build,
evaluation, deployment, monitoring, and retirement. 6L-G answers **which governance discipline
must produce evidence** at each point and how that evidence feeds the next decision. The two views
are complementary:

| 6L-G level | Governing question | Typical lifecycle touchpoints |
|---|---|---|
| 1. Strategy & Policy | What is the organization willing and unwilling to do with AI? | Portfolio, policy, and intake |
| 2. Risk & Impact Assessment | Who could be affected, how, and with what residual risk? | Ideation, data, and material changes |
| 3. Implementation Review | Are the promised controls present in the design and build? | Data, build, procurement, and architecture review |
| 4. Acceptance Testing | Is there enough independent evidence to release this version? | Evaluation and go/no-go |
| 5. Operations & Monitoring | Is the live system behaving within its approved posture? | Deployment, monitoring, incidents, and vendor changes |
| 6. Learning & Improvement | What did evidence, incidents, and users teach us, and what changes now? | Postmortems, retraining, policy updates, and retirement |

Do not treat the levels as a one-time waterfall. A material incident, model update, new data class,
new region, new tool, or change in user population can send a live system back to Levels 2 through 4.
The trigger and resulting decision should be recorded in the system's governance history.

## The six levels

### Level 1: Strategy & Policy

Set the organization's direction before individual teams choose tools. Define the intended benefits,
prohibited uses, risk appetite, accountable executive, decision rights, and escalation path. Make
principles operational: for example, a human-oversight principle should identify which decisions
require review, what evidence the reviewer receives, and what happens when the reviewer disagrees.

**Evidence to retain:** approved AI strategy or principles, policy set, risk appetite, inventory
owner, role and decision-rights map, prohibited-use rules, exception process, and review cadence.

**Useful signals:** inventory coverage, policy training coverage, overdue policy reviews, exceptions
by risk tier, unresolved ownership gaps, and the percentage of material changes that triggered a
policy or risk review.

**Failure pattern:** a council or charter exists on paper, but teams can deploy unregistered AI,
policy language is not translated into controls, and no named person can accept an exception.

### Level 2: Risk & Impact Assessment

Identify affected people and groups, intended benefits, foreseeable harms, misuse paths, legal and
contractual constraints, and the controls that reduce inherent risk. Record likelihood and impact
separately from residual risk. Include affected-stakeholder input when the system can materially
affect people, and document uncertainty rather than converting unknowns into false precision.

**Evidence to retain:** use-case intake, stakeholder and data-flow map, impact assessment, risk
tier, risk register, control plan, residual-risk decision, owner, due date, and acceptance or
escalation record.

**Useful signals:** percentage of in-scope systems assessed before build, overdue high-risk
mitigations, residual-risk acceptance by role, time from identified risk to disposition, and
reassessment coverage after material change.

**Failure pattern:** a generic checklist produces a low-risk label without testing whether the
system has sensitive data, consequential actions, untrusted input, or a vulnerable population.

### Level 3: Implementation Review

Verify that the architecture can enforce the commitments made at Levels 1 and 2. Review data
collection and retention, model and dataset provenance, vendor and subprocessor boundaries,
identity and access, prompt and retrieval paths, tool permissions, output handling, monitoring,
rollback, and human-review mechanics. A control belongs in the design and build evidence, not only
in a policy or launch slide.

**Evidence to retain:** architecture and data-flow diagrams, threat model, model and data cards,
software or machine-learning bill of materials, vendor evidence, control-to-risk traceability,
configuration and prompt versions, test plan, and open-finding register with owners and service
levels.

**Useful signals:** review completion time, high-severity findings closed before testing, percentage
of controls verified in the running environment, threat-model coverage, and vendor evidence gaps.

**Failure pattern:** the organization approves privacy, security, or fairness commitments without
showing the implemented anonymization, authorization, logging, or fallback behavior.

### Level 4: Acceptance Testing

Require independent, scenario-based evidence before release. Test normal, boundary, adversarial,
and failure cases, including prompt injection, data leakage, hallucination, subgroup performance,
unsafe tool use, cost runaway, and recovery. Test the human interface as well as the model. A
reviewer who can only see a polished demo cannot provide meaningful oversight.

Record the exact model or model-service version, configuration, prompt and retrieval versions,
input data or fixture version, test harness, results, unresolved limitations, and go/no-go decision.
For high-impact actions, validate the approval path and rollback or kill-switch behavior, not just
the text response.

**Useful signals:** test coverage by risk, critical findings open at go/no-go, pass and failure
rates by subgroup or scenario, approval-path success rate, and time to resolve launch blockers.

**Failure pattern:** a launch email is called approval, red-team findings are accepted without a
risk owner, or a human is present only to rubber-stamp the model's answer.

### Level 5: Operations & Monitoring

Observe the live system against the approved posture. Capture enough structured evidence to
reconstruct what happened: request or run identifier, user or agent identity, model and
configuration version, relevant retrieval source identifiers, tools and parameters used, policy
decisions, approvals, output disposition, and downstream outcome. Redact or minimize sensitive
content in telemetry, and separate audit evidence from unrestricted model reasoning by default.

Monitor reliability, quality, fairness, privacy leakage, prompt injection, tool behavior, spend,
latency, vendor changes, drift, user complaints, and control failures. Define thresholds that
pause, degrade, revoke, or escalate the system. A dashboard without an owner, threshold, or
response path is not operational governance.

**Evidence to retain:** monitoring plan, structured traces, alert history, incident and exception
records, vendor-change log, periodic review, access review, and evidence that a control actually
worked in the live boundary.

**Useful signals:** incident detection and resolution time, recurring incidents, subgroup drift,
blocked or approved tool calls, unexpected data destinations, policy exceptions, leakage findings,
feedback response time, and cost or token anomalies.

**Failure pattern:** logs capture only the final answer, guardrails fail silently, vendor updates
change behavior without a review, or feedback is collected but never routed to an owner.

### Level 6: Learning & Improvement

Turn incidents, near misses, user feedback, evaluation results, and operational metrics into
corrective and preventive action. Distinguish correlation from causation, preserve the evidence
that supports the conclusion, and measure whether the change reduced the original failure mode.
Update prompts, tools, datasets, policies, training, risk assessments, and release gates together
when the evidence requires it.

**Evidence to retain:** postmortem, root-cause analysis, corrective-action record, regression test,
updated risk and impact assessment, policy or control change, owner and deadline, reapproval record,
and before-and-after outcome measure.

**Useful signals:** recurrence rate, corrective-action closure time, time from incident to regression
test, percentage of improvements with measured effect, feedback-to-change conversion, and the
number of material changes that were reapproved before release.

**Failure pattern:** an incident is patched locally, but the playbook, test suite, policy, and
related systems remain unchanged, allowing the same class of failure to recur.

## Maturity across the levels

Assess maturity per level and per system. Do not average away a critical weakness in monitoring or
privacy because strategy is strong.

| Maturity | Observable posture |
|---|---|
| **Ad hoc** | Governance is fragmented and reactive. Inventory, ownership, testing, and evidence are incomplete or depend on individual initiative. |
| **Baseline** | A repeatable process, roles, escalation paths, and minimum safeguards exist. Reviews happen consistently, but measurement and remediation may be fragile. |
| **Managed** | Reviews, controls, exceptions, and findings produce versioned evidence. Metrics have owners, high-risk fixes are verified, and decisions are auditable. |
| **Proactive** | Operational signals can trigger reassessment, policy or control changes, and regression testing. The loop adapts without waiting for a public incident. |

The target is proportional. A low-impact internal experiment may need baseline safeguards, while a
system handling sensitive data or consequential actions may need managed or proactive controls in
specific levels. The rationale, residual risk, and sustainability of the chosen posture belong in
the decision record. Privacy, security, fairness, and accountability are not optional merely
because a system is early-stage.

## Operating rules for an evidence-backed loop

1. **Assign one accountable owner per decision.** Contributors can share work, but risk acceptance,
   exceptions, and release decisions need a named role.
2. **Attach evidence to the decision.** Link the exact artifact, version, test fixture, result, and
   reviewer. Never treat a policy, tool verdict, or vendor assertion as proof of the live boundary
   without checking the boundary itself.
3. **Keep exceptions bounded.** Record the reason, affected risk, compensating control, approver,
   expiration date, and re-review trigger. An unexpired exception is not a permanent tier change.
4. **Trigger reassessment on change.** At minimum, reassess after a model or vendor change, new
   data class, new tool or destination, new geography or user population, new action capability,
   material drift, incident, or changed external obligation.
5. **Measure outcomes, not activity alone.** Counts of reviews and policies are leading indicators;
   recurrence, leakage, subgroup harm, recovery, and user contestation show whether controls work.
6. **Close the loop deliberately.** A finding is not closed when a ticket changes state. Verify the
   fix against the failure mode in the live or representative environment, add a regression test
   where practical, and record residual uncertainty.

## Deployment-posture overlay

The same six levels apply across postures, but the control center of gravity changes. Classify the
posture before assigning control owners:

| Posture | Organization controls directly | Organization must obtain or contract for | Primary governance risk |
|---|---|---|---|
| **SaaS or application consumer** | User policy, identity, approved features, local DLP or review, data selection, and vendor administration exposed by the product | Vendor retention, training use, tenant isolation, logs, incident response, model changes, deletion, and subprocessor behavior | Vendor opacity can make an approved control impossible to verify |
| **API integrator** | User interface, pre- and post-processing, redaction, RAG permissions, application logs, routing, budgets, and action controls | Model behavior, provider-side logs, availability, subprocessors, data use, and service changes | Responsibility is split across two control planes, so either side can bypass the intended policy |
| **Model hoster** | Model and dataset provenance, serving stack, guardrails, logs, data residency, access, change, and incident controls | Hosting or infrastructure dependencies, upstream artifacts, and license or support commitments | Maximum control also means maximum operational and assurance burden |
| **Agentic overlay** | Agent identity, allowed tools, purpose and data scopes, memory, plans, approvals, sandbox, egress, traces, and kill switch | Each connected tool or agent's security, retention, availability, and downstream use | Planning, memory, and tool chaining can create unanticipated data flows and actions |

Do not infer risk from posture alone. A hardened, narrowly scoped agent can be safer than a simple
chatbot on an insecure foundation, and a vendor's certification does not transfer accountability
for choices the organization controls. For a concrete posture and agent review, use
`templates/agentic-governance-review.md`.

## Deliverable package

A defensible 6L-G review normally leaves behind:

- a system inventory record and accountable owner;
- the approved strategy, policy, risk appetite, and prohibited-use rules;
- a risk and impact assessment with residual-risk decisions;
- architecture, data-flow, threat, vendor, and control-traceability evidence;
- acceptance tests, limitations, launch decision, and rollback or escalation plan;
- monitoring, incident, exception, and change records; and
- a learning record that shows what changed and how the effect was measured.

If a level does not apply, record why and what compensating evidence covers the same risk. Do not
silently skip a level.

## Where to go next

- **`ai-lifecycle-governance.md`**: place these governance disciplines into lifecycle stage gates.
- **`governance-operating-model.md`**: assign councils, stewards, decision rights, and RACI roles.
- **`risk-management-and-frameworks.md`**: translate risk and impact findings into NIST or ISO-aligned artifacts.
- **`llm-and-agent-security.md`**: assess the exposure ladder, tool authorization, containment, and agent identity.
- **`privacy-and-data-governance.md`**: assess the four GenAI privacy pillars, purpose-aware egress, and memory retention.
- **`templates/agentic-governance-review.md`**: complete the posture, capability, tool, privacy, and evidence worksheet.

---

### Synthesized from

This reference is an original synthesis of the 6L-G framework and maturity model in *AI Governance*
by Engin Bozdag and Stefano Bennati, with terminology and control mappings cross-checked against the
skill's existing lifecycle, risk-management, operating-model, security, privacy, and current
research references. The 6L-G label is attributed to the book and is not presented as an
established external standard. Current legal, regulatory, security, and standards claims must be
re-verified against primary sources at use time. See `source-index.md` for the complete provenance
record.
