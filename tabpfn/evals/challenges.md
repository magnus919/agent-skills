# Assertion challenges

Author-written review examples, not executed model evaluation. Each row maps to an assertion; omission means not shown.

## version-license

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Exact weight terms reviewed. | Code license substitutes for weight terms. | No checkpoint terms. |
| 2 | Commercial scope explicitly checked. | Non-commercial weights assumed production-approved. | No use-scope decision. |
| 3 | No download or acceptance performed. | Automatic login accepts terms. | No action status. |

## fit-versus-adaptation

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Fit supplies context; fine-tuning changes weights. | Fit always trains transformer weights. | No distinction. |
| 2 | Context/schema/class map retained. | Only weights retained. | No bundle record. |
| 3 | Reload and task test required. | Saved file proves quality. | No runtime test. |

## time-context-leakage

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Availability cutoffs enforced. | Future labels/features used. | No temporal evidence. |
| 2 | Sealed labels excluded. | All labels enter context. | No context-label handling. |
| 3 | Deployment-matched split. | Shuffle dependent rows. | No split design. |

## capacity-offline

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Joint shapes measured. | Both maxima always fit. | No capacity comparison. |
| 2 | GPU peak/concurrency probe. | CUDA metadata proves fit. | No measurement. |
| 3 | Verify egress/device. | Local file proves offline. | No egress policy. |

## audit-not-runtime

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Inventory not model execution. | Metadata called inference pass. | No stage status. |
| 2 | Actual permission evidence needed. | Nonempty string certifies license. | No authorization distinction. |
| 3 | Calibration/task stages need evidence. | Audit proves quality. | No calibration/test evidence. |
