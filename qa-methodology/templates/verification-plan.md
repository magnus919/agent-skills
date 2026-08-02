# Verification Plan

> Plan independent verification for a spec, feature, or AI-generated implementation. Fill in the traceability table, assign verifiers, define evidence, and set exit criteria. See [ai-code-quality-gates.md](../references/ai-code-quality-gates.md) for gate context and the independent-verification principle.

## Metadata

| Field | Value |
|-------|-------|
| Feature / Spec | <name or spec document reference> |
| Author | <who wrote this plan> |
| Date | <YYYY-MM-DD> |
| Gate Entry | Gate 1 (spec review) / Gate 3 (implementation) / Gate 4 (acceptance) |
| Status | Draft / In Review / Active / Complete |

## AC → Verification-Method Traceability

Every acceptance criterion must map to at least one verification method. No AC may be unmapped.

| AC ID | Acceptance Criterion | Verification Method | Verifier | Evidence Format | Status |
|-------|---------------------|--------------------:|----------|-----------------|--------|
| AC-1 | <criterion text> | Test / Inspection / Analysis / Demonstration | <who or what> | <artifact that proves it> | Pending / Pass / Fail |
| AC-2 | <criterion text> | Test / Inspection / Analysis / Demonstration | <who or what> | <artifact that proves it> | Pending / Pass / Fail |
| AC-3 | <criterion text> | Test / Inspection / Analysis / Demonstration | <who or what> | <artifact that proves it> | Pending / Pass / Fail |

### Verification Method Definitions

| Method | When to Use |
|--------|-------------|
| **Test** | Executable check: automated script, unit/integration/E2E test |
| **Inspection** | Static review: code review, spec walkthrough, checklist audit |
| **Analysis** | Computed or derived evidence: metrics, logs, statistical sampling |
| **Demonstration** | Live or recorded walkthrough showing behavior under controlled conditions |

## Verifier Assignment

> The implementing agent (or developer) MUST NOT self-verify. Assign verification to a separate agent session, a different human, or an independent automated process.

| AC ID(s) | Verifier | Independence Mechanism |
|-----------|----------|----------------------|
| <AC-1, AC-2> | <separate agent session / human reviewer / CI pipeline> | <fresh context, no shared priors / different team member> |
| <AC-3> | <separate agent session / human reviewer / CI pipeline> | <fresh context, no shared priors / different team member> |

## Evidence Format

| Evidence Type | Format | Storage / Link |
|---------------|--------|----------------|
| Test output | <log file, JSON report, CI run URL> | <path or URL> |
| Inspection record | <review comments, checklist sign-off> | <path or URL> |
| Metrics snapshot | <dashboard screenshot, exported CSV> | <path or URL> |
| Demonstration | <screen recording, live session recording> | <path or URL> |

## NFR Verification

| NFR | Category | Measurement Approach | Threshold | Evidence |
|-----|----------|---------------------|-----------|----------|
| <e.g., API latency> | Performance | <p95 under load test> | <e.g., p95 < 200ms> | <perf report link> |
| <e.g., error rate> | Reliability | <soak test + monitoring> | <e.g., < 0.1%> | <monitoring snapshot> |
| <e.g., auth bypass> | Security | <SAST scan + manual review> | <zero critical findings> | <scan report link> |
| <e.g., response shape> | Contract | <contract test (Pact)> | <all consumers pass> | <contract test output> |

## Non-Determinism Handling

| Condition | Verification Approach |
|-----------|----------------------|
| Output is deterministic (same input → same output) | Single-run equality check |
| Output varies across N runs but has invariants | Property-based assertions + N-run sampling (N ≥ 5) |
| Output is probabilistic with known distribution | Statistical tolerance bands (e.g., p95 < X) |
| Output depends on external state | Pin external state; verify under controlled conditions |

**Decision rule:** Run the implementation 5 times with identical inputs. If any output differs, use property-based or statistical verification.

## Exit Criteria

Verification is complete when:

- [ ] 100% of ACs have a mapped verification method (no unmapped ACs)
- [ ] All verifications executed with evidence attached
- [ ] Zero critical or high severity findings remain open
- [ ] NFR thresholds met with evidence
- [ ] Verifier independence confirmed (implementer ≠ verifier)
- [ ] <Additional project-specific criteria: ___>

## Findings Log

| Finding ID | AC | Description | Severity | Status | Resolution |
|------------|-----|-------------|----------|--------|------------|
| VF-001 | <AC-ID> | <what was found> | Critical / High / Medium / Low | Open / Resolved / Accepted | <how resolved> |
| VF-002 | <AC-ID> | <what was found> | Critical / High / Medium / Low | Open / Resolved / Accepted | <how resolved> |
