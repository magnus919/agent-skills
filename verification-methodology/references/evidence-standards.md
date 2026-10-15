# Evidence Standards

## Evidence Levels

| Level | Standard | Example |
|-------|----------|---------|
| **Primary** | Direct observation, original data, reproducible experiment | Test output showing a passing result |
| **Secondary** | Report from a credible source, cited with provenance | Quoting an API documentation reference |
| **Circumstantial** | Indirect evidence that suggests but doesn't prove | Logs showing the system was up, but not that it processed correctly |
| **Assertion** | Claim without supporting evidence | "The system should work" |

## Verification Rules

- Claims require evidence at the level specified by the criteria
- A primary-source criterion cannot be satisfied with secondary evidence
- Missing evidence for a criterion is a HOLD, not a FAIL
- Contradictory evidence (claim says X, evidence shows Y) is a FAIL

## Uncertainty Handling

When evidence is insufficient:
1. Document what evidence is available
2. Document what evidence would be needed
3. Report as HOLD with a clear description of what would resolve the uncertainty

## Candidate changes and evidence reuse

Record candidate commit/content identity, acceptance contract ID/version/hash,
check procedure, relevant environment/fixture versions, execution time, result,
and durable evidence reference. Preserve old attempts as history, not standing
permission. A relevant code/content, contract, dependency/configuration, fixture,
or environment change invalidates the affected verdict. Identify that scope,
rerun affected checks, and issue a new verdict; document why any reused evidence
remains applicable. Missing fresh evidence is HOLD, not automatic PASS or a claim
that the new implementation failed. The record declares evidence; runtime state
integrity and independent review remain separate requirements.
