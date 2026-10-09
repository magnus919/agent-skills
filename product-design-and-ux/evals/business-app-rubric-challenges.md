# Added-case rubric challenges

Case: `embedded-loan-recovery`. Existing IDs and rubrics are unchanged. These are author review examples, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Presents editable proposed actions before approval | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Invalidates prior approval when the draft changes | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Blocks execution when permission is revoked after invocation | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Queries command status after a timeout rather than blindly reserving again | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Shows the confirmed reservation separately from failed notification | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Distinguishes synthetic acceptance fixtures from observed usability evidence | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
