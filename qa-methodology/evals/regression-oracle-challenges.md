# Regression oracle eval challenges

The following examples distinguish satisfying, contradictory and missing evidence for `regression-test-independent-expectation`.

| Assertion | Satisfying | Contradictory near miss | Omission |
|---|---|---|---|
| Independent expected header | Reads the contract and asserts the parsed downloaded header against it. | Takes the expected header from the exporter's helper. | Says to check the header and leaves its expected value unexplained. |
| Meaningful fail-to-pass | Keeps the assertion fixed. Known-bad reaches export and fails for the missing column. Corrected candidate passes. | Counts a fixture crash as proof that the assertion catches the bug. | Reports only candidate green. |
| Faithful substitute | Records the baseline setup failure and a controlled missing-column variant with its evidence limit. | Uses an unrelated exception as the negative control. | Describes no fallback or limitation. |
