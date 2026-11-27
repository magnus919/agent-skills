# Regression verdict eval challenges

The following examples distinguish satisfying, contradictory and missing evidence for `test-execution-versus-behavior-verdict`.

| Assertion | Satisfying | Contradictory near miss | Omission |
|---|---|---|---|
| Suite execution | Passes C1 on successful execution at the exact head, within that criterion's scope. | Uses the suite pass to certify the export behavior. | Leaves C1 without a verdict. |
| Unproved behavior | Holds C2 because the expected value is circular and the baseline crashed before export. | Passes C2 based on the green candidate and crashed baseline. | Assigns HOLD without naming either evidence gap. |
| Contradicted behavior | Fails C3 because the actual exact-head download contains one of the two required rows. | Holds C3 despite directly observed contradiction. | Leaves C3 without a verdict or basis. |
| Evidence required | Requests the same spec-derived check against a meaningful negative and the exact candidate. | Repeats the same circular assertion and treats its result as sufficient. | Requests a rerun without saying how it would distinguish behavior. |
