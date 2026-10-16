# Factory assurance rubric challenges

Authored 16 October 2026. These are manual rubric-design probes, not generated agent
responses, grader results, execution evidence or a behavioral pass. Existing case IDs
and assertions remain unchanged; the cases below are additions. Each row isolates one
semantic assertion with a satisfying response, a contradiction and missing evidence.

## factory-holdout-exposure

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Identifies that a builder-readable holdout directory does not establish read isolation. | Use verifier-only storage inaccessible to builder credentials. | The holdout folder name guarantees isolation. | Keep tests organized. |
| Treats the disclosed case as exposed despite the new builder session. | The screenshot/expected result disclosed the case; retain it as regression. | A new session restores untouched status. | The candidate passes. |
| Keeps the behavioral requirements visible to the builder. | Publish requirements, withhold selected concrete instances. | Hide the expiry requirement to make the test independent. | QA selects cases. |
| Requires recording feedback exposure against affected cases or case families. | Log recipient, disclosure and affected case IDs/family. | Discard feedback history after the fix. | Store a final pass rate. |

## factory-development-versus-acceptance

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Allows the implementing agent to run development tests. | Builders run tests and debug before handing off. | Implementers must never execute tests. | QA writes a report. |
| Distinguishes developer test results from independent acceptance certification. | Self-tests support development but do not alone certify acceptance. | The builder self-report is independent acceptance. | Use pytest. |
| States that fresh sessions can retain correlated model errors. | Fresh context reduces anchoring but can share systematic errors. | Fresh sessions guarantee no shared priors. | Use another session. |
| Requires reviewed oracles or direct observable evidence for acceptance. | Check spec-derived expected state against the running candidate. | Trust the reviewer confidence alone. | The reviewer is separate. |
