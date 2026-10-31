# Software factory validation boundaries

This addition has five output-quality cases and fifteen authored assertion challenges. Existing case IDs and assertions are preserved. Trigger probes remain separate. Schema validity and helper regression tests do not establish agent behavior or factory efficacy.

The new helper is exercised with synthetic snapshots, including transitive drift, late artifacts, cancellation, missing acknowledgement, budget exhaustion and malformed declarations. These validate only the helper behavior. No factory host, provider routing policy, live worker steering, service twin fidelity or semantic judge was reproduced. No live model/Jev evaluation was requested or dispatched for this work. CI may skip optional generation; that remains unassessed, never complete semantic coverage.

Research closure: original video captions were rate-limited; mediated transcript provenance and audiovisual limits are explicit in the video ledger and research log. Primary technical sources support bounded documented claims. Derived procedures are identified as synthesis. See the PR validation record for commands and results on the final candidate revision.

## Local execution receipt

Executed 2026-10-31 on macOS with Python 3.14.7 in the repository development environment:

- `python -m pytest harness-engineering/scripts -p no:cacheprovider -o addopts= -q`: 80 tests passed, 84 subtests passed.
- New helper CLI on the example snapshot: flags contract/export/verify, leaves docs as a review candidate; behavior and acceptance remain not_assessed.
- Ruff checks and formatting for the changed scripts passed; Bandit found no issues in the new helper.
- Repository structural validation: 191 skills; changed-skill quality: one skill, zero errors/warnings.
- Eval validator: 191 valid manifests; focused validator tests: 27 passed; coverage remains 100 percent and the modified-skill ratchet passed.
- Script-test discovery, bundle validation and all three generated catalog freshness checks passed.
- `skills-ref` was unavailable; repository structural/link/quality validators supplied the available checks. No upstream reference-validator pass is claimed.

The PR records exact-head CI and review results separately. The authored challenges remain rubric-design examples; these receipts do not resolve their semantic assertions.
