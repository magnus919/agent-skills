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

## Match the evidence to the claim

For the [saved settings journey](../../spec-driven-development/templates/FEATURE-MAP.md),
match each claim to the cheapest check that can actually falsify it:

| Claim | Evidence that can support it | Inadequate substitute |
|---|---|---|
| The interface shows the requested state | Screenshot or UI assertion from the exact running candidate and setup | An isolated mock or a screenshot of the wrong build |
| The setting persists | Exercise save, reopen the app with the same test profile, and read the value back independently | A screenshot taken before reopening |
| Save behavior is consistent across supported sequences | Generate representative valid sequences, assert the property, and retain seeds and failing traces for replay | One successful journey or examples selected after the fact |
| A consequential transition cannot violate a well-defined invariant | A checked model with explicit assumptions and a separate check that the implementation matches the relevant behavior | Treating a model proof as evidence that the integrated app works |

Use invariants and small models where the added coverage matters. A video,
property test, model check and human judgment can complement one another;
none silently expands the authority to expose a change.

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
