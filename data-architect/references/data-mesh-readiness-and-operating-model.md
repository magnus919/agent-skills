# Data Mesh Readiness and Operating Model

Use this reference before recommending a mesh adoption program. It is an assessment and design method, not a maturity badge or a preferred end state.

## Start With the Pressure

Name the measurable problem that centralization is failing to solve:

- Which consumers are blocked, and by what queue, quality failure, or missing context?
- Which domains generate the data, and which teams have authority to change it?
- What is the cost of delay, duplicate transformation, or unreliable data today?
- Could a catalog, ownership assignment, quality agreement, or platform improvement solve the problem without changing the operating model?

If the answer is unclear, do not begin a mesh rollout. Run discovery and a small product experiment first.

## Readiness Assessment

Assess each condition as **evidenced**, **partial**, or **absent**. Record the evidence, accountable owner, and next action.

| Condition | Evidence to seek | If absent |
|---|---|---|
| Meaningful domains | Stable business boundaries and named domain decision makers | Keep ownership centralized or pilot one bounded domain |
| Product accountability | A team can own semantics, quality, support, change, and retirement | Assign a product owner before publishing a mesh product |
| Consumer demand | Identified consumers with concrete freshness, quality, and access needs | Avoid platform work without a use case |
| Self-service platform | Repeatable paths for storage, processing, access, metadata, testing, and observability | Build the smallest enabling capability first |
| Federated governance | Shared definitions, classification, compatibility, access, and quality rules that can be checked | Establish minimum standards and decision rights |
| Team capacity | Domain and platform teams have funded time and operating skills | Use a centralized or hybrid transition |
| Executive sponsorship | Authority to resolve cross-domain conflicts and fund shared capabilities | Limit scope until sponsorship exists |

Do not collapse these into a numeric score. One absent prerequisite can dominate several positive signals.

## Data Product Minimum Contract

For every proposed product, document:

- **Identity:** product name, domain, owner, support path, version, and lifecycle status
- **Meaning:** business definitions, grain, units, keys, time semantics, and known exclusions
- **Consumers:** named use cases and whether access is push, pull, or both
- **Quality:** accuracy checks, completeness expectations, validity rules, freshness, availability, and incident response
- **Discoverability:** catalog entry, sample queries or payloads, lineage, classification, and access request path
- **Change:** compatibility policy, notification window, deprecation process, and consumer migration responsibility
- **Security and policy:** permitted use, sensitivity, retention, residency, masking, and audit requirements

The product is not complete because a table or topic exists. It is complete when consumers can find it, understand it, use it safely, and recover when it changes or fails.

## Operating Model Boundaries

- **Domain teams** own source meaning, product quality, support, and lifecycle decisions for the products they publish.
- **The self-service platform team** owns reusable paved paths and guardrails for storage, processing, access, metadata, testing, observability, and recovery. It does not become the hidden owner of domain semantics.
- **Federated governance** owns shared rules and conflict resolution for definitions, classification, compatibility, access, retention, and quality. Prefer automated checks and clear escalation over blanket approval queues.
- **Consumers** state their use case, service expectations, access need, and migration plan. Consumption does not transfer product ownership.

Keep interface contract syntax and protocol semantics in `api-design-and-evolution`; keep pipeline construction in `data-engineering`; keep platform deployment and operations in `platform-engineering`.

## Federated Computational Governance Method

Use a **rule plane and evidence loop** rather than a committee queue. The rule plane has two layers:

- **Global rules** cover interoperability and enterprise policy: shared identifiers and time semantics, minimum metadata, classification, access and retention constraints, compatibility, and required quality signals. They apply to every product and are changed only by the federated governance decision body.
- **Domain rules** cover local meaning and operating choices: valid business states, acceptable lateness, source-specific quality thresholds, and consumer-specific transformations. A domain owner may change them within the global envelope and must publish their scope and rationale.

Encode each rule as a versioned, machine-readable policy with a stable identifier, scope, owner, severity, effective time, and test expression. Execute it at the earliest useful control point: admission checks for schemas and metadata, build or publish checks for quality and compatibility, and read-time authorization or retention enforcement for policy rules. A human review is an escalation path, not the default execution engine.

For every execution, retain an evidence record linking rule ID and version, product and data release, subject, timestamp, evaluator, result, and remediation reference. Permit an exception only as a time-bounded record naming the approving authority, affected scope, reason, compensating control, expiry, and renewal decision; expired exceptions fail closed or return to the owning team for review. The domain product owner remediates local failures; the platform owner remediates broken enforcement; the federated governance owner resolves global-rule ambiguity or conflict. Review exception and failure records on a recurring cadence: repeated patterns become a proposed global rule, a clearer domain rule, a platform control, or an explicit decision not to standardize, with the decision and evidence retained.

## Transition Choices

Choose the smallest transition that tests the hypothesis:

1. **Centralized foundation:** Improve ownership, cataloging, quality, and serving in the existing platform.
2. **Domain pilot:** Publish one high-value product with a willing domain and a small consumer group.
3. **Hybrid:** Retain central conformance or regulatory serving while domains own bounded products and their source context.
4. **Broader mesh:** Expand only after the pilot demonstrates consumer value, product reliability, workable governance, and sustainable team capacity.

For each step define entry evidence, exit evidence, reversible actions, new operational load, and what will remain centralized. A transition plan that only lists platform components is incomplete.
