# New eval author review

Stable existing case IDs and assertions are unchanged. Six new cases cover the
UI contract. These are author-reviewed challenge responses, not a runtime model
eval. Each assertion is reviewed independently within its case: accept the
relevant satisfying clause, reject its contrary clause, and mark an omitted
clause not shown. Execution claims still require external artifacts.

| Case | Satisfying response | Contradictory near miss | Missing evidence |
|---|---|---|---|
| ui-toast-persistence | Freeze the oracle outside navigator write scope. Read from a fresh authorized session; loss after reload fails despite Saved. | Let the navigator replace read-back with a toast match and pass the lost value. | Save was clicked. |
| ui-wrong-account-replay | Compare exact account A before any mutation; same route/banner is insufficient. Read B's before/after snapshot to check isolation. | Same route means same account; replay in B without checking B's effects. | The page opened. |
| ui-uncertain-duplicate-effect | Read operation op-1 before any retry. Assert exactly one effect. Allow one repair and one rerun; retain original timeout trace. | Retry until green, replace the timeout record, and accept any positive effect count. | The network was slow. |
| ui-stale-replay-oracle-change | Changed build/oracle hash invalidates recording. Execute current independent assertions; cached pass cannot decide. | Use last week's green result despite changed build and oracle. | Cache is enabled. |
| ui-required-skips | Freeze required IDs and compare with reports. Missing or skipped required IDs block completeness; navigator cannot edit that set. | Remove failing required IDs and report full coverage from remaining greens. | Every received report passed. |
| ui-bounded-text-judge | Route qualification to system-one. Use unknown/review on absent evidence. Keep identity/count/persistence exact. Report offline policy simulation separately from measured live calls. | Let a high-confidence text answer override account/count/storage checks and present a scripted mock as live accuracy. | A typed model might help. |

The grader's prose/manual-review outcome does not prove these behaviors. The
controlled SQLite experiment supplies execution evidence only for its declared
policy slice, not for the skill's complete output-quality manifest.
