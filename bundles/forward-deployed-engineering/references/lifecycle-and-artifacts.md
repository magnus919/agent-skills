# Lifecycle and Artifacts

The lifecycle is a continuity contract, not a claim about industry standard
practice. Every stage reads the current charter, workflow map, and ledger; it
adds evidence rather than re-deriving prior decisions.

| Stage | Required question | Minimum output | Stop condition |
|---|---|---|---|
| Discover | What user workflow and problem are real? | Stakeholder/workflow map and unknowns | No recognizable problem or access to the relevant workflow |
| Frame | What is in scope, who decides, and what outcome matters? | Charter and decision rights | Authority, constraints, or outcome cannot be named |
| Hypothesize | What smallest intervention could change the workflow? | Testable hypothesis and decision rule | No falsifiable hypothesis or unsafe test |
| Build | What operationally complete slice can be built? | Thin-slice implementation plan and owner | Dependencies or permissions are infeasible |
| Evaluate | What evidence supports quality, safety, and usefulness? | Evaluation record and release recommendation | Baseline, representative evidence, or risk constraints missing |
| Deploy | Can it be released, recovered, and verified in the authorized environment? | Readiness, rollout, rollback, and verification record | No authorized access, rollback, or release decision |
| Adopt | Do intended users activate and use it in the target workflow? | Adoption scorecard and intervention record | Adoption failure is unexplained or ownership/support is absent |
| Measure | Did the capability change the agreed outcome? | Outcome measurement record | Instrumentation cannot distinguish expected from observed |
| Generalize | What should happen to the local learning? | Productization record and field-learning handoff | No evidence or receiving owner for the proposed next step |

## Shared record fields

For every stage record: date, stage, accountable lead, decision authority,
entry evidence, work performed, source/evidence label, observed result,
unknowns, risks, decision rule, decision, commitment, owner, due date, and next
handoff. A stopped engagement remains a valid output if the stop reason and
learning are preserved.
