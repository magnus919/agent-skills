# Batch containment rubric challenges

Case `batch-frontend-and-output-containment`, added 2026-10-12. Author-written
review challenges; no generated semantic pass is claimed. Artifact existence
checks establish presence only. Missing artifact inventory/content is not shown.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete inventory contains batch-plan.json | Response promises a plan but complete inventory omits it | No complete inventory |
| 2 | Plan blocks missing completion before weights load | Plan retries interactive CLI or CPU | No frontend decision |
| 3 | Positive time and combined byte limits plus EOF stdin | Only max_new_tokens or unlimited capture_output | No containment implementation |
| 4 | Fresh child group is terminated including descendants | kill-all GPU processes or only parent with inherited pipes left open | No cleanup mechanism |
| 5 | Plan says inference not run; later offload requires logs | Device listing alone proves GPU inference | No evidence-status distinction |
