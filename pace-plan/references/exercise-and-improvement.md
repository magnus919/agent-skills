# Exercise And Improvement

Load this reference when planning a test, capturing observations, reviewing an event, assigning corrective actions, or changing the plan.

## Choose A Bounded Objective

Exercise the smallest scope that can answer the readiness question. Examples of objective types include endpoint acknowledgment, transition decision-making, fallback setup, message fidelity, dependency discovery, or recovery handoff. These are categories, not prescribed scenarios.

Use the plan-local review and exercise cadence. The retained CISA guide calls for regular training and exercises but does not prescribe a universal frequency.

## Authorization And Safety Bounds

Before any live-system test, confirm:

- target paths and participants;
- named exercise controller and activation authority;
- start, stop, and abort conditions;
- allowed actions and prohibited actions;
- isolation from real incident traffic where required;
- rollback or return-to-normal procedure;
- evidence collection and sensitive-data handling;
- applicable local procedure and regulation.

If a path cannot be safely or legally exercised, record the limitation and use the most representative authorized check. Do not claim untested behavior passed.

## Observe Against Criteria

Record expected evidence before the exercise. During the exercise, preserve timestamps, acknowledgments, transition decisions, observed dependencies, message or procedure errors, recovery results, and conflicting observations. Avoid judging performance from memory alone when direct evidence is available.

## After-Action Review

Separate observations from findings:

- **Observation:** what happened, with evidence.
- **Finding:** why it matters to the plan objective.
- **Corrective action:** bounded change needed.
- **Owner and due date:** accountability for the action.
- **Validation action:** future evidence required for closure.
- **Plan change:** exact artifact or procedure affected.

Do not close an action because a document was edited. Close it when the stated validation action passes or the authorized owner accepts and records a different disposition.

## Change Governance

For each plan revision, record what changed, why, supporting evidence, affected pairs and tiers, approver, effective date, distribution or acknowledgment needs, and next review. Recheck dependencies whenever equipment, providers, staffing, sites, procedures, or participants change.
