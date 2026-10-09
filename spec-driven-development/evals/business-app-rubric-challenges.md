# Added-case rubric challenges

Case: `policy-translation-fidelity`. Existing IDs and rubrics are unchanged. These are author review examples, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Identifies original clauses and policy-owner review as authority for the decision table | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Requires translation-fidelity expected cases independently derived from original clauses | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Specifies date-based version selection with review on gaps or overlaps | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Tests threshold boundaries and unavailable-versus-exception precedence | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Rejects a correctness guarantee from generated code and table-derived tests | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
