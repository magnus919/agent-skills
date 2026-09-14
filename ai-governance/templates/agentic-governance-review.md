# Agentic AI and Deployment Posture Governance Review

> Fill this out for an AI system that uses an external application, a model API, a self-hosted
> model, or one or more autonomous agent capabilities. Use with
> [`six-level-governance-framework.md`](../references/six-level-governance-framework.md),
> [`llm-and-agent-security.md`](../references/llm-and-agent-security.md), and
> [`privacy-and-data-governance.md`](../references/privacy-and-data-governance.md). This is a
> governance worksheet, not legal or security advice. Re-verify legal, regulatory, and technical
> requirements against current primary sources.

## 0. Review record

- **System / product name:**
- **Version, model, provider, and configuration:**
- **Business owner:**
- **Technical owner:**
- **Risk owner / approver:**
- **Privacy or legal contact, if applicable:**
- **Review date:**
- **Review trigger:** [ ] New system  [ ] Material change  [ ] Periodic review  [ ] Incident or near miss  [ ] Vendor change  [ ] User or regulator request
- **Review scope and exclusions:**
- **Evidence location:**

## 1. Deployment posture and control boundary

Select the primary posture and record hybrid boundaries. Do not assume a vendor's controls cover
what the organization controls, and do not assume a self-hosted deployment is safer merely because
data stays inside the network.

- [ ] **SaaS or application consumer:** vendor operates the interface, middleware, and model stack.
- [ ] **API integrator:** organization operates the interface and pre/post-processing; an external
  provider operates the model API.
- [ ] **Model hoster:** organization operates the model-serving and guardrail stack, whether on
  premises or through managed infrastructure.
- [ ] **Agentic overlay:** the system plans, observes, reflects, acts, uses tools, or retains memory.

| Layer or control | Organization owner | Vendor / provider owner | Evidence or contract reference | Gap, assumption, or follow-up |
|---|---|---|---|---|
| User interface and identity | | | | |
| Input filtering and redaction | | | | |
| Model, weights, and updates | | | | |
| Retrieval data and permissions | | | | |
| Output validation and disclosure | | | | |
| Tools, APIs, and downstream actions | | | | |
| Logs, traces, and retention | | | | |
| Incident response and notification | | | | |
| Deletion, export, and termination | | | | |
| Subprocessors and data destinations | | | | |

**Control-boundary conclusion:**

- **Controls directly verified by the organization:**
- **Controls supported only by vendor evidence or contract:**
- **Controls that cannot currently be verified:**
- **Compensating controls for those gaps:**

## 2. Capability and exposure inventory

Mark every capability that exists in the deployed configuration, not only the capability shown in
the happy-path demo. Record the narrowest useful scope and the evidence that proves it.

| Capability | Present? | Scope, limits, and stop condition | Evidence / test reference |
|---|---:|---|---|
| Planning across multiple steps | [ ] | | |
| Reflection or self-refinement | [ ] | | |
| Observation of events or schedules | [ ] | | |
| Acting on records, messages, workflows, or code | [ ] | | |
| Tool or API invocation | [ ] | | |
| Multi-agent communication or delegation | [ ] | | |
| Persistent memory across tasks or users | [ ] | | |
| External web or browser access | [ ] | | |
| Access to sensitive or regulated data | [ ] | | |
| Irreversible or consequential actions | [ ] | | |

### Six-factor security exposure ladder

Use these factors to identify the system's exposure, not to calculate a numeric risk score. The
factors are a dependency ladder, not a severity ranking. A weak environment can cause more harm
than a higher-level capability, and one factor can be present without all the others.

| Factor | Applies? | What makes it apply here | Existing control and residual concern |
|---|---:|---|---|
| **Environment**: weak logging, secrets, access, isolation, or vendor security | [ ] | | |
| **Model**: unvetted, externally controlled, fine-tuned, or provenance-uncertain model | [ ] | | |
| **Input**: untrusted user, document, web, or tool content reaches the model | [ ] | | |
| **Data access**: runtime retrieval of personal, confidential, or sensitive data | [ ] | | |
| **Ability to make changes**: records, messages, transactions, code, or configuration can change | [ ] | | |
| **Agency**: the system chooses goals, tools, order, or retries across multiple steps | [ ] | | |

**Highest exposed factor and why:**

**Why a lower factor cannot be treated as solved by a higher-level control:**

## 3. Risk and impact decision

- **Affected people, groups, customers, employees, or third parties:**
- **Intended benefit and success measure:**
- **Foreseeable harms and misuse paths:**
- **Sensitive or regulated data involved:**
- **Consequential decisions or external communications:**
- **Inherent risk:**
- **Residual risk after controls:**
- **Uncertainty that must not be hidden in the rating:**
- **Risk tier and rationale:**
- **Required stakeholder review:**

### Material-change triggers

Reopen the risk and impact assessment when any of these changes: [ ] model or provider
[ ] prompt, policy, or guardrail [ ] data class or retrieval source [ ] user population or geography
[ ] tool, agent, destination, or permission [ ] memory or retention behavior [ ] material drift
[ ] incident, near miss, complaint, or challenge [ ] external obligation or contract.

## 4. Approved tools and authorization

A tool registry is an allowlist and accountability record, not a catalog of everything a connector
can do. Approve individual operations where possible. Authorization must be evaluated outside the
model's natural-language reasoning and immediately before invocation.

| Tool / operation ID | Purpose | Data fields sent and returned | Read / write / destructive | Destination / region | Agent identity and user context | Approval tier | Version or integrity evidence | Owner |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

### Authorization policy

- **Default decision:** [ ] Deny unless explicitly allowed  [ ] Other, with rationale:
- **Runtime attributes checked:** [ ] agent identity  [ ] user identity  [ ] role  [ ] purpose
  [ ] data classification  [ ] fields and parameters  [ ] destination  [ ] tenant or resource
  [ ] time or rate limit  [ ] current approval  [ ] tool version or integrity
- **Decision point outside model reasoning:**
- **Policy decision and enforcement component:**
- **Credential scope and lifetime:**
- **How tool-description or tool-output injection is handled:**
- **How newly advertised or changed tools are detected and held for review:**
- **Inter-agent trust and authentication, if applicable:**

### Action approval tiers

Classify by consequence, not by what the agent claims it intends to do.

| Tier | Example class | Default behavior | This system's rule and evidence |
|---|---|---|---|
| Low impact, reversible read | Read a permitted record or retrieve a non-sensitive source | Allow with logging and rate limits | |
| Medium impact or externally visible | Draft, schedule, update a reversible field, or send a bounded message | Confirmation or targeted human review | |
| High impact, sensitive, or irreversible | Payment, deletion, access change, regulated decision, production change | Explicit approval every time, with rollback or escalation | |

- **Approval threshold is calibrated to avoid:** [ ] approval fatigue  [ ] rubber-stamping
  [ ] unreviewed consequential actions  [ ] hidden outbound egress
- **Approval evidence and approver identity:**
- **Rollback, reversal, or containment path:**

## 5. Purpose-aware data egress

Evaluate every outbound tool call or external transfer at the enforcement point. A “read-only”
operation can still exfiltrate data through a URL, query, tool response, or downstream log.

- **Declared purpose for this run:**
- **Lawful basis or internal authorization record, where applicable:**
- **Minimum data necessary for that purpose:**
- **Permitted destinations, regions, and subprocessors:**
- **Blocked destinations or data categories:**
- **Data classification method:**
- **Egress enforcement point:**
- **Fail-closed behavior when no rule matches:**

For each proposed transfer, the gate must evaluate:

1. **Purpose:** Is the use compatible with the declared purpose?
2. **Necessity:** Are these exact fields required, or can the payload be redacted, generalized, or
   replaced with a reference?
3. **Destination:** Is this tool, recipient, region, and subprocessor permitted?

Record the policy result and the data actually sent:

| Run / call ID | Tool and destination | Purpose | Fields proposed | Fields sent after minimization | Decision | Approval / basis | Evidence |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |

Allowed outcomes should be explicit: **allow**, **allow with redaction**, **block**, **request
human approval**, or **request just-in-time consent**. A policy engine may return a decision, but a
separate enforcement point must prevent the call when the decision is block or approval is absent.

## 6. Memory, retention, and user rights

Treat memory as a governed data store and a possible persistence mechanism for malicious or
incorrect instructions. Do not allow durable memory to become an unreviewed second source of truth.

| Memory tier | Contents and purpose | Retention / TTL | Who can read or write | User or admin inspect/delete path | Evidence |
|---|---|---|---|---|---|
| Ephemeral working memory | | | | | |
| Bounded session or task log | | | | | |
| Long-term user or organizational memory | | | | | |
| Shared multi-agent memory | | | | | |
| Derived model, embedding, or index state | | | | | |

- **Durable writes require:** [ ] explicit user choice  [ ] human review  [ ] approved source
  [ ] purpose and lawful-basis check  [ ] summarization or normalization  [ ] other:
- **Memory-poisoning detection and recovery:**
- **Cross-tenant or cross-user isolation:**
- **Erasure workflow covers:** [ ] source records  [ ] prompts and outputs  [ ] logs and traces
  [ ] caches and backups  [ ] embeddings and indexes  [ ] memory stores  [ ] model updates or
  fine-tuning inputs  [ ] downstream tools and agents
- **How future runs are prevented from using erased data:**
- **What cannot currently be erased or corrected, and how that limitation is disclosed:**
- **User memory view, correction, and deletion surface:**

## 7. Test and evidence plan

Do not infer control effectiveness from policy text, a vendor assertion, or a model response alone.
Test the control at the boundary where it is supposed to operate.

| Risk or control | Test scenario / fixture | Expected result | Actual result | Model, config, data, and tool versions | Evidence link | Owner / due date |
|---|---|---|---|---|---|---|
| Direct and indirect prompt injection | | | | | | |
| Retrieval or tool authorization | | | | | | |
| Sensitive-data leakage or egress | | | | | | |
| Hallucination, output integrity, or overreliance | | | | | | |
| Fairness or subgroup impact | | | | | | |
| Memory poisoning or stale memory | | | | | | |
| Cost, loop, timeout, or denial-of-wallet | | | | | | |
| Human approval and contestability | | | | | | |
| Kill switch, credential revocation, and rollback | | | | | | |
| Vendor, model, tool, or configuration change | | | | | | |

- **Independent reviewer or red team:**
- **Known limitations and untested paths:**
- **Regression tests added for prior failures:**

## 8. Six-level governance decision

Summarize the evidence at each level. A level can be lighter for a low-impact system, but it must
not be silently skipped.

| Level | Evidence available | Open gap or exception | Owner | Decision / re-review trigger |
|---|---|---|---|---|
| 1. Strategy & Policy | | | | |
| 2. Risk & Impact Assessment | | | | |
| 3. Implementation Review | | | | |
| 4. Acceptance Testing | | | | |
| 5. Operations & Monitoring | | | | |
| 6. Learning & Improvement | | | | |

- **Decision:** [ ] Approve  [ ] Approve with bounded exception  [ ] Pilot only  [ ] Reject or hold
- **Approved scope and duration:**
- **Named exception owner and expiration:**
- **Compensating control:**
- **Required remediation before expansion:**
- **Next review date or trigger:**
- **Approver and date:**

## 9. Runtime handoff and learning loop

- **Structured trace fields:** request/run ID, identity, model and configuration version, retrieval
  source IDs, tools and parameters, policy decisions, approvals, output disposition, downstream
  outcome, and error or override. Minimize or redact sensitive content.
- **Runtime thresholds and response:**
- **Automatic degradation, pause, credential revocation, or kill-switch triggers:**
- **Manual intervention path:**
- **User complaint, contestation, and feedback path:**
- **Incident and near-miss review owner:**
- **How findings become policy, control, or regression-test changes:**
- **Metric showing whether the last improvement worked:**

### Completion check

- [ ] Control ownership is explicit across the deployment boundary.
- [ ] The capability inventory reflects the deployed configuration, including hidden or optional paths.
- [ ] Risk factors, affected people, residual risk, and uncertainty are recorded.
- [ ] Tool operations, credentials, destinations, and action approvals are allowlisted and enforced.
- [ ] Every external data transfer has purpose, necessity, destination, and fail-closed checks.
- [ ] Memory tiers, retention, deletion, and correction paths are documented.
- [ ] Tests exercise adversarial, boundary, failure, and recovery behavior with versioned evidence.
- [ ] Runtime monitoring, intervention, and learning owners are assigned.
- [ ] The decision, exceptions, expiration, and re-review triggers are signed by the accountable role.

---

### Source note

This original worksheet operationalizes the deployment postures, six exposure factors, agentic
capabilities, tool authorization, approval calibration, purpose-aware egress, memory tiers, and
closed-loop evidence practices described in *AI Governance* by Engin Bozdag and Stefano Bennati,
then cross-wires them with the existing `ai-governance` references. It does not reproduce source
prose or establish legal requirements. See `../references/source-index.md` for provenance.
