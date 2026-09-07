# Methodology and Evidence

## What it is

ASQ defines gap analysis as comparing a current condition to a desired state. NIST's Cybersecurity Framework makes the pattern operational: an organization creates a Current Profile and Target Profile, compares them to identify gaps, and uses gap size, priority, and corrective-action cost to plan implementation. The general method transfers, but NIST categories and tiers are cybersecurity-specific.

The generic unit is:

`criterion -> current condition -> target condition -> difference -> consequence -> action -> closure evidence`

A target may be a mandatory requirement, a service/outcome level, a risk-informed design objective, a strategic choice, or a research question. Name which. “Best practice” is not a target until its authority and applicability are established.

## Scope and evidence protocol

Write an analysis question that names the object, population, boundary, time horizon, and decision. Build a criterion register before collecting evidence. For each criterion record:

- identifier and plain-language statement;
- source/authority, version/date, and applicability;
- measure, unit, denominator, observation period, and threshold;
- evidence sources and collection method;
- confidence and known bias/limitations;
- accountable owner and affected stakeholders.

Triangulate when stakes justify it. Metrics show behavior but may omit context; interviews reveal experience but may be selective; documents show intended practice but not execution; tests show behavior under their scenario but not every real-world condition. Do not treat self-attestation as independent assurance.

## Gap taxonomy

Use one primary type and optional secondary types:

- **Outcome/performance:** the result is below the required condition.
- **Capability/control:** a needed ability, control, or decision right is absent or unreliable.
- **Process:** work differs from the required flow, timing, quality, or handoff.
- **Resource:** people, skills, data, capacity, funding, or tooling are insufficient.
- **Knowledge/evidence:** information is missing, imprecise, biased, inconsistent, or not relevant to the decision.
- **Ownership/decision:** authority, accountability, escalation, or feedback is unclear.

A symptom is not automatically a gap cause. “Incidents increased” is an observation; “no tested rollback path” may be a control gap; “unclear ownership” is a hypothesis until supported by records or interviews.

## Scores and uncertainty

Scores are communication aids, not measurements unless the scale, anchors, evidence, and aggregation rules are defined. Prefer descriptive states such as absent, partial, repeatable, measured, and continuously improved when they fit. If using a numeric scale, publish anchors and do not average incomparable dimensions. A low-confidence red score means “urgent uncertainty” may be more accurate than “worst performance.”

## What sources support

- NIST CSF profiles support current/target profile comparison, risk-informed outcomes, and prioritized implementation planning. NIST explicitly warns that Implementation Tiers are not necessarily maturity levels.
- GAO workforce reviews support data-driven identification, prioritization by programmatic impact, and stakeholder consultation before naming skills gaps. They also illustrate the risk of inconsistent metrics and incomplete competency data.
- CDC needs-assessment guidance supports defining the goal in relation to program outcomes and describing gaps as outcomes not currently occurring.
- AHRQ/NCBI research-gap work supports classifying where evidence falls short and why, including insufficient/imprecise, biased, inconsistent/unknown, or not-the-right information. It is a research-evidence framework, not a general organizational maturity model.
- ASQ provides the concise quality definition and examples of baseline measurement and process evidence. It does not prescribe one universal prioritization formula.

## Minimum review questions

1. Who set the target, and why does it apply here?
2. Is the current state observed, reported, inferred, or assumed?
3. Are current and target measured on the same unit, population, period, and boundary?
4. What consequence follows if the gap remains open?
5. Which causes are evidenced, and which are hypotheses?
6. What would prove closure, and who can accept that evidence?
