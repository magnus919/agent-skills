# Factory assurance rubric challenges

Authored 16 October 2026. These are manual rubric-design probes, not generated agent
responses, grader results, execution evidence or a behavioral pass. Existing case IDs
and assertions remain unchanged; the cases below are additions. Each row isolates one
semantic assertion with a satisfying response, a contradiction and missing evidence.

## factory-review-lane-disagreement

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Records separate behavioral and engineering review dispositions. | Behavior PASS; engineering FAIL for competing status semantics. | Behavior passed, so engineering automatically passes. | The work looks good. |
| Binds required lane evidence to the same integrated candidate. | Record both lanes for integrated tree X, rerunning affected checks. | Use each PR pass on its own old snapshot as final evidence. | List test names. |
| Blocks integration while the required engineering finding remains unresolved. | Hold integration until repaired or explicitly excepted by authorized policy. | Merge because the UI works. | Add a review note. |
| Retains the existing four SDD gates. | Engineering is a lane before integration, reconciled at Gate 4. | Add mandatory Gate 5 to this SDD pipeline. | Run reviews. |

## factory-planning-handoff-and-risk

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Accepts an equivalent existing approved planning artifact rather than requiring duplicate prose. | Reference the approved PRD version directly. | Rewrite the entire PRD solely to get the SPEC.md filename. | Plan the release. |
| Maps requirements to implementation tasks and verification. | Carry AC IDs into tasks and acceptance checks. | Dispatch tickets without requirement links. | Keep the PRD. |
| Separates implementation simplicity from security verification depth. | Fast implementation still needs authorization-boundary checks. | One line always means light verification. | Use a faster model. |
| Calls for filling consequential missing handoff information. | Check unresolved decisions and relevant NFRs; add gaps with owners. | Assume missing policy decisions silently. | Use the existing PRD. |
