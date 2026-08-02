# Follow-Up Domains

Every incident finding maps to at least one of six follow-up domains. Each domain has a distinct owner, a typical verification method, and a routing target — the specialist skill that owns implementation in that domain.

## The six domains

### Product

**What this domain covers:** Requirements, specifications, design decisions, user experience, feature behavior, API contracts, and product assumptions.

**When to use this domain:** The incident revealed a missing, incorrect, or incomplete requirement; a product assumption that did not hold; a user experience that produced operational risk; or a design decision that needs revision.

**Typical follow-up work:**
- Update or add a requirement or specification
- Revise a design decision or API contract
- Update a product assumption in the assumption ledger
- Add a user story for handling a previously unanticipated scenario

**Routing target:** [product-lifecycle-learning](../product-lifecycle-learning/SKILL.md) for assumption updates and product-outcome review.

**Verification method:** The requirement, specification, or design change is documented and approved; the change addresses the gap identified in the escaped-from analysis.

### Code

**What this domain covers:** Implementation, logic, dependencies, configuration, algorithms, data handling, and error handling.

**When to use this domain:** The incident involved a code defect, a missing implementation, an incorrect algorithm, a configuration error, or a dependency behavior that needs to be handled.

**Typical follow-up work:**
- Fix a code defect
- Add input validation or error handling
- Configure a timeout or circuit breaker
- Update a dependency or handle its failure mode

**Routing target:** Implementation specialist per the system's tech stack ([backend-engineering](../backend-engineering/SKILL.md), [frontend-engineering](../frontend-engineering/SKILL.md), or domain-specific skill).

**Verification method:** The code change is merged, tested, and deployed; the specific failure mode from the incident is reproduced and confirmed fixed.

### Tests

**What this domain covers:** Regression tests, integration tests, unit tests, assertion coverage, test infrastructure, and test data.

**When to use this domain:** The incident revealed missing regression coverage, a test that should have caught the failure but didn't (weak assertions, skipped test, test-environment gap), or a need for a new test category (e.g., chaos test, load test).

**Typical follow-up work:**
- Add a regression test that reproduces the failure mode
- Strengthen existing test assertions
- Add an integration test covering the component boundary where the failure occurred
- Add a performance or load test for a scaling-related incident

**Routing target:** [qa-methodology](../qa-methodology/SKILL.md) for test strategy and design.

**Verification method:** The test exists, passes, and fails when the original failure condition is reintroduced (mutation or fault-injection verification).

### Evals

**What this domain covers:** Evaluation cases, grader coverage, dataset gaps, trajectory review, and eval harness improvements for AI agents or ML systems.

**When to use this domain:** The incident involved an AI agent or ML system behavior that should have been caught by an eval; a failure mode that is not covered by existing eval cases; or a grader that did not detect a problematic output.

**Typical follow-up work:**
- Add an eval case that reproduces the failure mode
- Add a grader dimension that would have flagged the incident behavior
- Add a trajectory-review checkpoint for a previously unobserved failure pattern
- Update a dataset to include the incident scenario

**Routing target:** [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) for eval design and implementation.

**Verification method:** The eval case exists, produces a failing result when run against the pre-fix system, and produces a passing result against the post-fix system.

### Operations

**What this domain covers:** Monitoring, alerting, runbooks, capacity planning, incident response procedures, on-call rotations, and operational tooling.

**When to use this domain:** The incident involved a monitoring gap, an alert that did not fire or was ignored, a runbook that was incorrect or missing, a capacity limit that was not tracked, or an operational procedure that failed.

**Typical follow-up work:**
- Add or tune a monitor or alert
- Update or create a runbook
- Add capacity planning for a resource that was exhausted
- Update an incident response procedure
- Instrument a previously unmonitored component

**Routing target:** [site-reliability-engineering](../site-reliability-engineering/SKILL.md) for monitoring, alerting, and operational practice.

**Verification method:** The monitor or alert fires under the incident condition (tested via fault injection or replay); the runbook is exercised and produces the expected outcome.

### Governance

**What this domain covers:** Access control, authority boundaries, policy, compliance, approval workflows, change management, and agent authority configuration.

**When to use this domain:** The incident involved insufficient access control, a missing or bypassed approval gate, an authority boundary that was too broad (human or agent), a policy that was not enforced, or a compliance gap.

**Typical follow-up work:**
- Restrict a permission or access level
- Add an approval gate to a workflow
- Configure an agent authority boundary
- Update a policy or compliance control
- Add a change-management check

**Routing target:** Domain-specific: access control and policy changes route to the system's IAM or governance framework; agent authority changes route to the agent's configuration framework.

**Verification method:** The restricted action is attempted and blocked; the approval gate is exercised and requires the expected authorization; the policy is audited and enforced.

## Domain assignment rules

1. **Every significant finding maps to at least one domain.** A finding that maps to no domain is either too vague (refine it) or not actionable (record as unresolved uncertainty).
2. **A finding can map to multiple domains.** A monitoring gap (operations) that also reveals a missing requirement (product) maps to both. Each domain gets its own follow-up item.
3. **The escaped-from category suggests the primary domain, but is not binding.** A migration gap (escaped-from category) typically maps to code or operations; but if the migration gap exposed a systemic monitoring deficiency, operations may be the primary domain.
4. **Assign ownership before closing the follow-up map.** A follow-up item without a named owner is incomplete. "The team" is not an owner.
5. **Each domain has a verification method.** The verification method is recorded in the follow-up work map and referenced in the closure record. A follow-up item without a verification method cannot be closed.

## Follow-up work map fields

Each follow-up item in the work map must include:

| Field | Description |
|---|---|
| **Finding ID** | Unique identifier linking to the incident learning record |
| **Domain** | One of: product, code, tests, evals, operations, governance |
| **Description** | What needs to be done |
| **Escaped-from category** | The originating gap (requirement, monitoring, authority, migration, adoption) |
| **Owner** | Named individual or role accountable for completion |
| **Target date** | When the follow-up work should be completed |
| **Verification method** | How completion and effect will be verified |
| **Routing target** | Specialist skill or team that owns implementation |
| **Status** | Proposed / accepted / in progress / implemented / verified / rejected |
| **Closure record reference** | Link to the verification and closure record when closed |
