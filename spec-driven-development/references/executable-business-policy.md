# Executable business policy

Use when authoritative business clauses must become repeatable decisions. Retrieval can explain a clause with citations; it cannot establish eligibility or permission. Deterministic evaluation implements an approved interpretation; generated code and passing tests do not guarantee translation fidelity or 100% correctness.

## Recipe and gates

1. Identify the policy owner, authoritative document, clause IDs, version, effective interval, jurisdiction/scope, and event whose date selects the policy. Preserve the source hash. Drafts, retrieved summaries, and model explanations are not authority.
2. Extract a decision table with conditions, outcomes, reasons, exception paths, and precedence. Have the policy owner review it against the original clauses before implementation. Unresolved ambiguity, contradictory rules without approved precedence, or uncovered exceptions produce `review`, never an invented default.
3. Specify typed inputs with units and requiredness; distinguish missing, invalid, zero, and false. Specify output status (`eligible`, `ineligible`, `review`), reason codes, rule IDs, policy version, and evidence references. Eligibility is not execution authorization.
4. Select exactly one published version by the agreed event date and scope. Zero matches, overlaps, or an unavailable version stop automated evaluation. Use half-open effective intervals; do not silently use today's latest rules for a historical request.
5. Implement pure deterministic evaluation. Keep explanation generation separate and cite the actual selected clauses. Model judgment can classify uncertain evidence into a review lane, but cannot override policy, fill missing facts, or authorize execution.
6. Obtain translation-fidelity fixtures independently from a policy owner or domain reviewer working from the original clauses, not from the generated implementation or its decision table. Preserve provenance, expected reasons/rule IDs, and disagreements. Synthetic developer fixtures below are demonstrations, not independent owner approval.
7. Test thresholds on both sides and exactly at the boundary, precedence conflicts, exceptions, absent/invalid facts, version transitions, gaps, and overlaps. Tests of code against the same mistaken table cannot prove the table matches policy. Route evaluation methodology to `agent-evals-and-observability` and authority enforcement to `agent-production-operations`.
8. Release source, approved table, code, fixtures, and hashes as one versioned package. Require policy-owner signoff and engineering review; record compatibility, migration, rollback to a still-applicable approved package, and effective time. Shadow historical cases before activation. If rollback would select expired rules, pause automatic decisions and route to review instead. Route release orchestration to `release-engineering`.

Complete when the traceable package is reviewable and gates have evidence. Stop with named owners for unresolved interpretation or approval; do not describe drafted tables as owner-reviewed.

## Fictional equipment-loan policy (developer-authored)

Version `loan-v1`: 2026-01-01 inclusive through 2026-07-01 exclusive, selected by requested pickup date. `loan-v2`: from 2026-07-01. Scope: community equipment loans, integer calendar days.

| Clause / priority | Condition | Result / reason |
|---|---|---|
| L1 / 1 | Item unavailable | ineligible / unavailable |
| L2 / 2 | Exception requested, unless L1 matched | review / exception |
| L3 / 3 | Requested duration exceeds limit (v1: 7; v2: 5) | ineligible / duration |
| L4 / 4 | Otherwise, with complete valid facts | eligible / within_limit |

All facts are required; validation occurs before rule evaluation. Missing facts, non-boolean availability/exception, or non-positive/non-integer days produce review / invalid_input. Version gaps/overlaps produce review / policy_selection. For unavailable plus exception, L1 wins. No exception is automatically approved.

Copy `templates/BUSINESS-POLICY.md` for real work. Run the synthetic evaluator from the repository root with Python 3.10+ (standard library only):

```sh
python3 spec-driven-development/scripts/business_policy.py --input spec-driven-development/evals/loan-request.json
python3 -m pytest spec-driven-development/scripts/test_business_policy.py
```

The evaluator is read-only and prints structured JSON; malformed JSON exits nonzero. It does not release policy or execute loans. Adapt the rules only after replacing this fictional source with owner-approved clauses and independent fixtures.
