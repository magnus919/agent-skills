# Architecture Health Assessment

Use this template for a repeatable, evidence-backed assessment of an existing system. Keep recommendations separate from reverse-engineered facts.

## Scope and confidence

- System/revision:
- Assessment date:
- Included surfaces:
- Excluded surfaces:
- Stakeholders and operators consulted:
- Evidence limitations:
- Confidence scale: high / medium / low

## Executive assessment

- Overall health statement:
- Strongest evidence-backed property:
- Highest-risk unresolved property:
- Immediate observation or containment:
- Boundary statement and neighboring skills:

## Evidence ledger

| ID | Claim | Class (observed/reported/inferred/unknown) | Evidence | Confidence | Follow-up |
|---|---|---|---|---|---|
| E-001 |  |  |  |  |  |

## Architecture characteristics

| Scenario | Characteristic | Current behavior | Evidence | Owner/boundary | Tension or risk | Next probe |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Coupling and modularity

| Candidate boundary | Static | Dynamic | Data | Temporal | Deployment | Organizational | Change coupling | Verdict |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

## Data ownership and workflows

- Entity/fact authority map:
- Shared invariants:
- Distributed transaction boundaries:
- Workflow shape: orchestration / choreography / hybrid / unknown
- Partial completion states:
- Failure detection and repair:
- Reconciliation key, precedence, and audit evidence:

## Decomposition readiness

- Pressure requiring a boundary change:
- Candidate capability and invariant owner:
- Independent deployment/scaling evidence:
- New coordination and operating cost:
- Alternatives considered, including retaining a modular monolith:
- Readiness verdict: ready for bounded experiment / needs seam work / retain current boundary / insufficient evidence
- Reversible probe and stop condition:

## Prioritized findings

| Priority | Finding | Evidence IDs | User/operator impact | Smallest safe next step | Owner |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Clean-room and handoff checks

- [ ] No source code, copied implementation examples, private identifiers, or line-level derivative detail appears in the design output.
- [ ] Facts, inferences, reports, and unknowns are labeled.
- [ ] API/interface semantics are handed to `api-design-and-evolution`.
- [ ] Data-platform strategy is handed to `data-architect`.
- [ ] Implementation is handed to the relevant engineering skill.
- [ ] Approved migration execution is handed to `migration-engineering`.
