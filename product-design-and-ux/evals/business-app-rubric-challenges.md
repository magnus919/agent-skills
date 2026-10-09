# Added-case rubric challenges

Case: `embedded-loan-recovery`. Existing IDs and rubrics are unchanged. Author review fixtures, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Presents editable proposed actions before approval | Preview fields can be edited before exact-action approval | Model draft is executed immediately | Response omits this boundary |
| Invalidates prior approval when the draft changes | Duration edit clears approval and reruns policy | Old approval survives edited duration | Response omits this boundary |
| Blocks execution when permission is revoked after invocation | Revoked role blocks submission with no reservation | Role was checked only before recommendation | Response omits this boundary |
| Queries command status after a timeout rather than blindly reserving again | Timeout recovery queries persisted command ID | Timeout generates a new reservation with a new key | Response omits this boundary |
| Shows the confirmed reservation separately from failed notification | Reservation receipt remains confirmed; notification failure shown separately | Notification failure is reported as failed reservation | Response omits this boundary |
| Distinguishes synthetic acceptance fixtures from observed usability evidence | Probe table labeled synthetic and unrun | Synthetic probes are called observed usability findings | Response omits this boundary |
