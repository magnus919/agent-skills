# Fitness Functions for Decision Confirmation

A fitness function is a repeatable check that supplies evidence about whether an architectural decision still holds. It may be a static rule, a test, a runtime measurement, a scheduled audit, or a bounded human review. The useful unit is not the check alone: it is the trace from decision, to characteristic, to measurement, to observed evidence, and back to a reviewable owner.

## Ownership Boundary

The ADR owns the durable choice, rationale, consequences, and a link to confirmation. The fitness-function record owns the operational contract for the check. The project's test, CI, telemetry, runtime, or governance system owns execution and raw evidence. Do not put executable implementation in the ADR, and do not let an operational dashboard silently become the decision record.

For system-wide evolutionary architecture, use a human architecture decision owner; no current catalog skill owns that complete workflow. For general SLO, telemetry, or alerting design, use the relevant reliability or telemetry skill. For operating a named tool, use that tool's skill. This reference is about making an ADR's consequential claim confirmable.

## Decision-to-Evidence Trace

Record the chain explicitly:

```text
ADR-042: isolate tenant data at the repository boundary
  -> characteristic: cross-tenant access safety
  -> fitness function: integration test attempts reads and writes with mismatched tenant contexts
  -> observed evidence: CI run 1842, 0 unauthorized rows across 240 cases
  -> decision review: owner accepted evidence; next review 2026-09-30
```

An ADR link such as `Confirmed by: docs/architecture/fitness/tenant-isolation.md` is sufficient when the linked record contains the rest of the chain. A pass without a source, run identifier, sample window, or reviewer is not durable evidence.

## Select the Function

Start with the decision's observable characteristic, not with a favorite tool. Ask what would convince a skeptical future reviewer that the decision is holding.

### Scope

Choose the narrowest boundary that can falsify the decision without making the result meaningless:

- **Atomic:** one dependency, package, route, schema rule, or configuration property. Use for a crisp invariant such as forbidden imports.
- **Structural:** a set of components or relationships. Use for layering, cycles, ownership, or deployment topology.
- **Scenario:** a user or operational path across components. Use for authorization, recovery, ordering, or end-to-end guarantees.
- **Holistic:** a system-wide outcome such as latency distribution, cost, or recovery time. Use only when the decision itself is system-wide and the measurement can identify meaningful change.

State what is inside and outside the boundary, the population sampled, and the blind spots. A broad metric that cannot identify a violating path is a signal, not a compliance gate. Pair it with a narrower check when a missed violation would be costly.

### Cadence and Invocation

Select cadence from failure speed and change exposure:

- **Change-triggered:** run on pull requests, schema changes, or deployment configuration changes when a violation should block introduction.
- **Continuous:** collect at runtime when drift or harm can emerge between releases, such as error rates or resource isolation.
- **Scheduled:** sample periodically when the evidence is expensive, data-dependent, or needs a stable observation window.
- **Event-triggered:** run after an incident, migration, exception, or material dependency change.

Name the invocation mechanism and its failure behavior: command or job, environment, required fixtures, timeout, result sink, and whether a missing result is a failure, warning, or escalation. Automated invocation is preferred for repeatable facts. A manual review is valid when judgment is intrinsic, but it needs a named reviewer, structured evidence request, and due date rather than “review occasionally.”

### Evidence Type

Classify evidence before choosing a threshold:

| Evidence | Best for | Main limitation |
|---|---|---|
| Static analysis | Dependencies, ownership markers, configuration shape | Can miss runtime paths and generated behavior |
| Test result | Behavior under declared scenarios and fixtures | Only covers the scenarios and data exercised |
| Runtime telemetry | Actual distribution, incidents, saturation, and user impact | Needs context, sampling controls, and stable instrumentation |
| Audit sample | Data or process conditions that are expensive to check continuously | Sampling can miss rare failures |
| Expert review | Intent, trade-offs, and evidence not mechanically expressible | Must expose reviewer, rubric, dissent, and date |

Use at least two evidence types when the decision has both a structural condition and an outcome claim. Do not treat a proxy metric as proof of the decision; label it as leading, lagging, or diagnostic evidence.

### Threshold Rationale

Every threshold needs a reason, not just a number. Record:

1. the unit, population, aggregation, and time window;
2. the desired value or allowed range;
3. the baseline and measurement uncertainty;
4. the harm or decision consequence at the boundary;
5. why this threshold is achievable now;
6. who can change it and what evidence is required.

Prefer a hard gate for a safety or compatibility invariant. Prefer a warning band and trend review for noisy outcomes. Use a minimum sample size, confidence or uncertainty note, and a missing-data rule where they affect interpretation. A threshold that can be passed by reducing traffic, excluding difficult cases, or changing the denominator is not defensible until those gaming paths are addressed.

## Operate Without Fooling Yourself

### Ownership

Assign three roles when the blast radius warrants it:

- **Decision owner:** accountable for whether the ADR still applies and for approving changes to its rationale.
- **Function owner:** keeps the check runnable, interpretable, and linked to the current decision.
- **Evidence consumer:** reviews results and acts on failures; this may be an on-call, service, or governance owner.

For small teams one person may hold all roles, but record the names or teams and the escalation path. The function owner cannot unilaterally weaken a threshold that protects another team's boundary.

### False Positives and False Negatives

Document known failure modes for the measurement:

- A **false positive** reports violation when the decision holds. Record suppression criteria, fixture corrections, quarantine limits, and the human escalation path. Never make a permanent exception by hiding the result.
- A **false negative** reports compliance while the decision is violated. Record untested paths, sampling gaps, instrumentation failures, and a compensating check.

For every expected exception, identify the evidence that distinguishes it from a real violation. If a check fails because its own data or instrumentation is stale, mark the result as indeterminate rather than compliant.

### Gaming and Proxy Risk

Assume that teams optimize for the visible score. Review whether the subject can improve the metric while the decision's intent worsens: narrow the sample, move work outside the measured boundary, delete failures, retry until success, or optimize an average while harming the tail. Countermeasures include immutable raw evidence, denominator and exclusion reporting, stratified or adversarial samples, paired outcome measures, independent review, and periodic spot checks. Record which countermeasure is used and what it cannot prevent.

### Exceptions

An exception is a visible, time-bounded deviation, not a second threshold. Each exception record should state the affected boundary, reason, risk acceptance, compensating control, approver, start date, expiry date, and exit evidence. A failed function should route to the decision owner or named escalation path. Do not auto-approve an exception merely because the check is noisy.

## Review and Retirement

Review the function when the ADR changes, the measured system boundary changes, a failure or incident exposes a blind spot, the owner changes, or the evidence stops influencing a decision. At the review, ask:

- Does the decision still apply, and does the characteristic still matter?
- Does the scope cover the paths and populations that can violate the decision?
- Is the cadence early enough for the harm and affordable enough to sustain?
- Does observed evidence support the threshold, or is the baseline now stale?
- Are false positives, false negatives, gaming paths, and exceptions visible?
- Did a human act on the last meaningful result?

Retire a function only when the ADR is superseded, the characteristic is no longer a decision driver, or a better check replaces it. Record the retirement reason, date, owner approval, replacement link if any, last evidence location, and any unresolved risk. Do not delete historical results or leave an ADR link pointing to an unmarked dead check.

## Common Forms

Static architecture tests such as ArchUnit can enforce dependency direction, package cycles, or naming rules. TypeScript equivalents can inspect module relationships. Runtime or integration checks are better for tenant isolation, recovery, ordering, or authorization scenarios. CI can validate a Structurizr model's syntax and references. An AI-assisted review can compare a change against several ADRs when the claim is semantic, but it must identify its input artifacts, rubric, model or reviewer, uncertainty, and escalation path; it is evidence for review, not an unquestioned gate.

The implementation belongs in the project's test or operational infrastructure. The ADR should link to the record and the record should link to the observed run, report, query, or review artifact.
