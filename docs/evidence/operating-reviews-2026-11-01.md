# Five operating-method reviews

Research-only change: each report retains its own scope, source revision, case
corpus, method, evidence limits and decision. No skill, eval, gate or live control
implementation is included.

| Issue | Findings | Evidence and result |
|---|---|---|
| #766 production operations | [Runtime transition consistency](operations-audit-2026-11-01/findings.md) | Nine existing cases plus two static boundary fixtures; `defer` and third-breach source contradictions require separately approved repair |
| #765 governance | [Decision coverage](governance-audit-2026-11-01/findings.md) | Eight cases inspected; 35 helper tests passed; bounded EU timeline check; no new method justified |
| #767 harness engineering | [Task and declaration boundaries](harness-audit-2026-11-01/findings.md) | Eight cases inspected; 46 tests and 66 subtests passed; behavior/runtime/release acceptance unassessed; no new method justified |
| #769 AI operating economics | [Workflow decision evidence](economics-audit-2026-11-01/findings.md) | Six cases inspected; no actual financial/causal/user outcome evidence; no new method justified |
| #762 supervisory capacity | [Three public reconstructions](supervisory-capacity-2026-11-01/findings.md) | Shared worksheet did not materially change the authored baseline recommendations; no-build gate retained |

Passing local tests and repository validation establish their named mechanics only.
Source coverage is not behavioral quality; public reconstructions are not participant
observations; narrative recommendations are not actual organizational decisions.
Actual-user validation in #758 remains separate and incomplete.
