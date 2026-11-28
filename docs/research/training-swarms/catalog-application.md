# Applying the research to the coordination experiment

This documents the revision and two output-quality eval cases for [multi-agent-coordination](../../../multi-agent-coordination/SKILL.md). The [research brief](research-brief.md) ranks the changes, and the [research log](research-log.md) records their provenance. Reviewed on 2026-11-28.

## Extend the existing experiment template

Capture the reason work is distributed, who can see each prerequisite, and which information the acceptance owner is authorized to receive. Record the comparison arms, accessible search surface, independent selection method, communication paths, and how a protocol difference would change an observable action.

| Question | Minimum useful comparison | Diagnostic evidence |
| --- | --- | --- |
| Can we combine facts held by different workers? | Candidate versus a simple authorized collector or fixed handoff under the same access rules. A no-sharing run tests the prerequisite. A centralized full-input run can provide a synthesis ceiling if that access is in scope. | Required source IDs, missing or stale facts, duplicated deliveries, use of the facts and exact acceptance. |
| Does sharing improve parallel exploration? | Strong single agent with the aggregate allowance, independent best-of-N with an operational selector, and communicating N. Add a fixed partition with the same selector when disjoint work is a credible alternative. For channel attribution, add a communication-disabled version of the same harness. | Branch changes after a verified checkpoint, useful reuse, avoidable overlap and coverage, alongside final acceptance. |
| Does the team make delivery faster? | Compare actual end-to-end time at comparable accepted quality, with a shared deadline and explicit cost accounting. | Critical-path elapsed time including coordination waits and integration, plus total spend and reviewer effort. |

Freeze the model revision, tools, access, held-out roster, acceptance rule and relevant total allowances. Use clean state between arms. Keep the selector blinded to reference answers and charge its work. If an offline verifier can retrospectively find a correct candidate but the running system cannot, report that oracle result as a ceiling. For deterministic tasks where the verifier is available by design, its permitted execution can be part of the operational selector. If testing training too, report training interventions and budgets separately from serving costs and distinguish independently trained best-of-N from a same-policy communication ablation.

Record actual input and output tokens where available, including received messages and rereads, and record tool, selector, reconciliation, review and integration costs. Treat timeouts and spending-limit stops as outcomes in the attempted roster. Measure the acceptance denominator at the task level. Record authorization or isolation violations separately and apply the declared conduct gates. A harmless per-arm marker can check for cross-arm visibility without storing sensitive data. Record the tested surface and unknown coverage. Predeclare meaningful effect, sample size and uncertainty method, then report the paired difference and any material budget or scope mismatch.

For information transfer, use source or assignment IDs to distinguish a repeated delivery from equal facts from distinct sources. Record sent, read, used and accepted separately. For exploration, test whether a verified finding causes a useful continuation or avoids a redundant one. Preserve independent checks where corroboration is deliberately required. Use directed, evidence-linked updates or a bounded shared artifact as testable designs. A small-team broadcast with identical audience needs can be a legitimate control. Count its recipient fan-out and context costs.

## Eval cases and rubric challenges

The examples below check whether reviewers can distinguish satisfying evidence, contradictory evidence and omissions. They are authored examples and have no executed behavior results. The implemented prompts and assertions live in the [eval manifest](../../../multi-agent-coordination/evals/evals.json).

### communication-versus-independent-attempts

| Assertion | Satisfies | Contradicts | Omits |
| --- | --- | --- | --- |
| Withhold attribution | Reports the observed counts and the resource, access and judge differences | Credits the 14-case gain to sharing | Gives a rerun without assessing the observed result |
| Compare the three arms | Extended solo, independent best-of-four and shared notes with four workers | Labels a note-sharing arm independent | Proposes solo and a communicating team only |
| Match aggregate budget | Gives each arm 40k including overhead | Sets 40k for each worker versus 40k for solo | Specifies a team count without a budget |
| Match eligible search scope | Gives all arms access to the standard collections | Gives the team additional collections | Mentions the roster without stating allowed sources |
| Match the roster | Uses the same held-out cases for every arm | Gives solo and team different case sets | Reports only a cohort size |
| Match acceptance | Applies the same evidence and correctness rule to every arm | Accepts team cases on a lower evidence standard | Counts accepted cases without stating the rule |
| Use a practical selector | A reviewer applies a blind, available rubric to the four artifacts | Picks the candidate matching a secret answer key | Says best-of-four without a selection method |
| Charge selection | Deducts reviewer or judge resources from the arm's allowance | Grants the judge a free call outside the allowance | Gives a selector without cost accounting |
| Count attempts | Divides accepted integrated cases by the attempted cohort including timeouts | Removes budget-stopped cases from the denominator | Lists accepted counts with no denominator |

### distributed-facts-versus-synthesis

| Assertion | Satisfies | Contradicts | Omits |
| --- | --- | --- | --- |
| Authorized comparison | Collects four permitted narrow summaries in a fixed handoff | Gives an unauthorized agent unrestricted raw records | Proposes adding peers without a simpler comparison |
| No-sharing interpretation | Uses it to show whether the required inputs can reach the decision owner | Calls its failure proof that the peer protocol beats a fixed collector | Discusses a collector without assessing what a no-sharing run could show |
| Trace A | Identifies the absent source separately from the retransmission | Says all four sources arrived | Reports only the duplicate delivery |
| Trace B | Identifies a synthesis error after all four inputs were read | Calls the dropped value a missing delivery | Discusses trace A only |
| Keep distinct sources | Replays the same source once and preserves two equal values with different IDs | Deduplicates by value | Recommends deduplication without a key |
| Require evidence at scale | Holds expansion pending accepted aggregation on representative twelve-worker cases | Treats increased message volume as proof of correct scaling | Diagnoses the traces without addressing the proposed expansion |
