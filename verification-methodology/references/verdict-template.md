# Verdict Template

## Verdict

**PASS / HOLD / FAIL**

## Candidate and acceptance binding

- Candidate: <commit SHA plus dirty-content hash, or artifact content hash>
- Acceptance contract: <ID, version, immutable hash/reference>
- Reviewed scope: <tasks, criteria, artifacts, relevant dependencies>
- Verifier and review independence/limitations: <identity and basis>
- Issued at: <timestamp>
- Validity: Current / Superseded / Withdrawn; <reason and replacement verdict>

This verdict applies only to that candidate and contract. Before delivery,
reconcile them with the actual artifacts. Relevant code/content, contract,
dependency, configuration, fixture, or environment changes supersede affected
approval and evidence. Record a new verdict after affected checks pass; identify
any unaffected evidence deliberately reused and why its scope still applies.
A branch/PR label, unchanged commit with dirty files, or old PASS is insufficient.

## Executed evidence

| Evidence ID | Criterion / task | Command or reproducible observation | Candidate / contract | Environment / fixtures | Executed at | Result | Durable reference / hash |
|---|---|---|---|---|---|---|---|
| E-001 | <criterion / task> | <actually executed check> | <bound identities> | <relevant versions/configuration> | <timestamp> | PASS / FAIL / HOLD / UNRUN | <report/output reference> |

Record unrun, skipped, failed, and inaccessible checks explicitly. A planned check
or successful empty/stub run is not behavioral evidence. Missing current evidence
means HOLD for the affected criterion, even if an earlier candidate passed.

## Criteria Assessment

| Criterion | Result | Evidence | Notes |
|-----------|--------|----------|-------|
| Criterion 1 | PASS/FAIL/HOLD | What evidence supports this | Any caveats |

## Summary

- **Passed:** [count] criteria
- **Failed:** [count] criteria
- **Held:** [count] criteria (insufficient evidence)

## Next Steps

If HOLD: what would resolve the uncertainty.
If FAIL: what must change before re-submission.
