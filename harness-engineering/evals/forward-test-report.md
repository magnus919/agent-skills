# Independent forward-test review

Date: 2026-09-26. Skill candidate: local working revision; upstream course pinned at
77e7a3e21469dcbece2558086c8d91657abeaa40.

Three separate agents received realistic raw fixtures and the skill entry point,
without the intended solution. They could read routed resources; writes were
confined to disposable fixtures/output. Reviewer provenance: `reviewer_kind:
model_teacher`. The exact inherited provider model identifier was not recorded;
these are advisory model-produced reviews, not human labels or calibrated accuracy.

| Scenario | Observed outcome | Evidence boundary |
|---|---|---|
| Pagination project with passing shape test | Agent added acceptance checks; broken pages failed, conforming in-memory oracle passed, empty discovery exited 2, fresh-process rerun failed reproducibly | Demonstrates fixture-local detection; application was intentionally not repaired; no real-agent paired efficacy run |
| Ticket creation followed by timeout before checkpoint | Agent produced reconciliation, authorization-after-hook, and fail/unknown routing contracts; state/graph declarations validated | Recovery drills were planned, not executed; runtime was not implemented |
| Old/new checkout records with changed environment | Comparator refused comparison; agent deferred adoption and distinguished supplied outcomes from verified checkout behavior | One supplied case, no authenticated traces, no causal inference |

The comparison review found an actionable usability issue: refusal did not name
the mismatched fingerprint. The tool now names incompatible fingerprint keys;
a repeat comparison names `environment` and exits 2. Its regression suite passes.

Repository review also showed that a small existing project can improve its
checks without using the scaffold or adding redundant state. Runtime review
identified an intentional tooling boundary: tool/event/hook contracts receive
design review, while bundled validation covers state, graph and run declarations.
Neither review warrants expanding a methodology skill into a framework runtime.

## Retained review artifacts

- [Repository report](forward-evidence/repository-report.md)
- [Executed repository probes](forward-evidence/repository-results.json)
- [Runtime handoff and limits](forward-evidence/runtime-handoff.md)
- [Comparison decision before error-message repair](forward-evidence/comparison-decision.md)

These retain the reviewers' original observations, including the old comparator
message. Temporary fixture paths are historical locations, not installation
requirements. The full disposable runtime/fixture output is not bundled here.
The script suites provide reproducible deterministic regression checks; these
forward reviews are a bounded advisory screen. Nineteen declarative eval cases
remain a contract, not nineteen verified semantic passes. No broad effectiveness,
release approval, calibrated grader quality, or world-class status is established.
