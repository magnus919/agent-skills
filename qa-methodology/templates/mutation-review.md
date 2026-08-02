# Mutation Review

Use this artifact for a bounded mutation-guided test-hardening review. Keep the project's native tool output as the authoritative raw report; this is a review record, not a portable report schema.

## Change And Scope

- Review/change concern:
- Expected behavior:
- Base commit:
- Exact candidate/head commit:
- Target files/lines:
- Scope rationale:

## Run Configuration

- Tool and version:
- Configuration:
- Operator set:
- Seed:
- Test command:
- Mutant budget:
- Per-mutant timeout:
- Exclusions and rationale:
- Environment:
- Raw report location:

## Baseline Result

- Command and commit:
- Result:
- Relevant output/evidence:

## Mutants

| Stable ID | Location | Operator | Status | Disposition | Evidence |
|---|---|---|---|---|---|
|  |  |  | killed / survived / equivalent-or-likely-equivalent / no coverage / timeout / flaky / invalid / infrastructure-tooling failure |  |  |

## Accounting

- Denominator formula:
- In-scope mutants:
- Classified mutants:
- Excluded mutants:
- Unknown or incomplete mutants:
- Infrastructure/tooling failures:
- Explanation of any difference:

Unknown, incomplete, excluded, and failed outcomes must remain visible; they do not silently become killed or leave the denominator.

## Candidate Test

- Proposed test and expected behavior:
- Why this tests behavior rather than implementation:
- Behavioral relevance:
- Non-tautology/non-vacuity check:
- Non-redundancy and maintainability check:
- Flake-risk check:
- Implementation-coupling check:

## Independent Verification

- Baseline-test result:
- Exact-mutant-kill result:
- Repeat/flake result:
- Independent verifier:
- Verification timestamp/identity:
- Evidence locations:

## Decision

- Human reviewer decision:
- Uncertainty and limitations:
- Rerun/reproduction command:
- Follow-up owner and due date:
