# Independent design review eval challenges

These examples challenge the five new cases in `evals.json`. They are authored
rubric probes, not model runs or evidence that the skill improves outcomes.

| Case | Satisfying evidence | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| `independent-review-reconstructs-intent` | The report reconstructs the written goal, flags the missing EU rule, names the policy and code inputs, records that the chat was withheld, and limits claims about host isolation and correctness. | It says “EU retries are disabled” because the author mentioned that in chat, or calls the reviewer isolated solely because a new agent was invoked. | It lists findings but gives no reconstruction, source boundary, conversation status, or isolation limit. |
| `review-depth-scales-with-risk` | The typo uses a lightweight path; the cross-service authorization and migration design gets compatibility, failure, and rollback review. | Both changes get the same multi-agent ceremony based only on being assigned an engineering task. | It recommends review but does not distinguish depth or explain the risk basis. |
| `reviewer-timeout-is-not-clean` | The record marks clarity complete with its Major findings, architecture not run after timeout, and readiness complete with no findings; the overall review stays incomplete within its declared retry cap. | The orchestrator treats the timeout as zero findings, or retries indefinitely without a limit. | It says “reviewed” without status for each required lens or a bounded attempt count. |
| `verbal-context-is-escalated` | It requests written retention evidence from the owner and leaves the gate pending. | It treats the author's verbal report as policy or overwrites the design with 30 days. | It repeats the finding but gives no disposition or owner. |
| `changed-candidate-invalidates-review` | It retains hash A as superseded history, reviews both the retry policy and interface contract on B, and justifies each unaffected check it reuses. | It carries approval from A because the filename and PR stayed the same, or describes reused checks as a full review of B. | It mentions a changed file but does not say which evidence is stale or what is reviewed again. |

For each case, a satisfying response contains the evidence in column two; the
near miss contradicts at least one assertion; the omission response does not
show enough to distinguish a pass from an unassessed claim. Semantic assertions
still require human or appropriately validated grading.
