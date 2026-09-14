# Policy and observability ownership

Use this reference when a platform must preserve developer control while meeting security, compliance, reliability, or audit requirements.

## Developer-owned delivery with guardrails

Keep the application team in control of its build and deployment workflow. Publish reusable checks, starter pipelines, and policy interfaces that teams can call from their own pipelines. Enforce requirements at the point where a change is admitted or completed, rather than inserting a centralized manual queue for every deployment.

For each check, document the input, policy version, decision, evidence location, failure response, exception route, and owner. A check may run before a change or immediately after it, but it must be deterministic enough to explain why a decision was made. Policy-as-code engines and admission controllers are implementation choices; this methodology owns the contract and evidence flow.

## Exception and escape-hatch workflow

1. Consumer states the requested deviation, affected resources, duration, reason, and compensating controls.
2. Platform owner checks scope, authorization, blast radius, expiry, and whether the golden path or policy should be improved instead.
3. Approver records the decision and accountable owner. High-risk exceptions need the relevant security, compliance, or service owner.
4. Automation applies the narrowest permitted scope and emits an auditable decision record.
5. Owner reviews the exception before expiry, closes it, renews it with fresh evidence, or turns the repeated exception into a product backlog item.

An exception is not a permanent bypass. Missing evidence, an expired exception, or an unowned violation is a release or access blocker according to the consuming release/security policy; this skill does not define that policy.

## Observability as a platform service

The platform should provide collection, default dashboards, published SLIs/SLOs, and a clear response route. For every signal, identify:

| Concern | Ownership to record |
|---|---|
| Instrumentation and collection | Service team supplies meaningful signals; platform supplies the supported path and availability of collection |
| Storage, retention, and access | Platform/telemetry owner, including tenancy and cost controls |
| SLI/SLO definition | Service owner proposes the indicator and target; platform helps publish and validate it |
| Alert interpretation and response | The service owner handles service symptoms; platform handles platform symptoms and routes ambiguous cases |
| Adoption and quality | Platform product owner measures coverage, usefulness, query/alert friction, and feedback |

Require a response matrix for each published SLO: symptom, query or alert, severity, recipient, first diagnostic action, escalation, and evidence retained. Review false positives, missing signals, and unused dashboards with consumers. The service-facing observability contract remains the technical baseline; this workflow adds product adoption and response ownership.

## Review gate

Before calling the platform capability ready, verify that the contract, policy decision evidence, exception record, SLO/response matrix, owners, and adoption measurement are present. If any owner or failure route is unknown, record the gap and stop at the appropriate readiness decision.
