# Added-case rubric challenges

Case: `policy-translation-fidelity`. Existing IDs and rubrics are unchanged. Author review fixtures, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Identifies original clauses and policy-owner review as authority for the decision table | Table rows cite L1–L4 and remain pending until policy-owner approval against the source | Generated table is treated as authoritative without owner review | Response omits this boundary |
| Requires translation-fidelity expected cases independently derived from original clauses | Owner derives expected verdicts directly from original clauses, before inspecting code | Expected cases are generated from the implementation and called independent | Response omits this boundary |
| Specifies date-based version selection with review on gaps or overlaps | Pickup date July 1 selects v2; zero or multiple applicable versions route to review | Always selects latest version, including historical requests | Response omits this boundary |
| Tests threshold boundaries and unavailable-versus-exception precedence | Lists 4/5/6 and 6/7/8 day tests plus unavailable-and-exception conflict | Only tests ordinary eligible loans | Response omits this boundary |
| Rejects a correctness guarantee from generated code and table-derived tests | States passing generated tests cannot establish translation correctness | States deterministic generated code guarantees 100% correctness | Response omits this boundary |
