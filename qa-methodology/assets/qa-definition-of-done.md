# QA Definition of Done

> QA contribution to the team's definition of done. Adapt to your project's risk profile and release cadence. Check each item that applies before declaring a feature or release complete.

## Scope

| Field | Value |
|-------|-------|
| Feature / Release | <name> |
| Team | <team> |
| Date | <YYYY-MM-DD> |

## Functional Verification

- [ ] All acceptance criteria verified with evidence attached
- [ ] AC→verification-method traceability is 100% (no unmapped ACs)
- [ ] Happy path tested at each applicable level (unit / integration / E2E)
- [ ] Known failure modes tested (error handling, edge cases)
- [ ] Regression suite passes (no new failures introduced)

## Risk-Based Coverage

- [ ] Risk register reviewed; all P0/P1 risks have corresponding tests
- [ ] Test allocation proportional to risk scores (P0 items receive exhaustive coverage)
- [ ] Residual risk documented and accepted by stakeholders

## Test Quality

- [ ] No flaky tests in the suite (quarantined or fixed before release)
- [ ] Test data uses synthetic or masked data (no production PII)
- [ ] Tests are deterministic (non-deterministic code verified with N-run sampling)
- [ ] Mutation testing run on critical paths (if applicable)

## Non-Functional Requirements

- [ ] Performance thresholds met (p95 latency, throughput under load)
- [ ] Security scan clean (zero critical/high findings from SAST/SCA)
- [ ] Accessibility checked for user-facing changes (WCAG 2.1/2.2 AA)
- [ ] Contract tests pass for all API consumers (if applicable)

## Automation and CI

- [ ] New tests automated and committed to the repository
- [ ] Tests integrated into CI pipeline at the correct stage
- [ ] Every fixed bug has a regression test ("every fixed bug becomes a regression test")
- [ ] CI pipeline green on the release branch

## Documentation and Handoff

- [ ] Test strategy document up to date (if changes affect scope)
- [ ] Exploratory session debriefs recorded (if sessions were run)
- [ ] Known issues and workarounds documented
- [ ] Risk register updated with new or changed risks

## Release Gate

| Gate Item | Owner | Status |
|-----------|-------|--------|
| All P0 exit criteria met | <QA lead> | Pending / Met / Waived |
| All P1 exit criteria met | <QA lead> | Pending / Met / Waived |
| Stakeholder sign-off on residual risk | <product / eng lead> | Pending / Met / Waived |
| Release decision | <release manager> | Pending / Approved / Blocked |

## Exceptions Log

| Item | Reason for Exception | Approved By | Risk Accepted |
|------|---------------------|-------------|:-------------:|
| <which DoD item> | <why it was skipped> | <name> | Yes / No |
