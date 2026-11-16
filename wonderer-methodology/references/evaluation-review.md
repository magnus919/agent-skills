# Evaluation review

## Evidence boundary

Initial port rubric, revision 1. Stable case IDs live in evals/evals.json.
The examples below are authored challenge snippets, not observed model responses
or human adjudication. For each assertion, read the case prompt and corresponding
snippet: a satisfying snippet can support met, a contradiction supports not met,
and an omission supports not shown. Full-response review must check quantifiers
such as “each lead” across the entire map. No semantic pass is claimed.
Retrieval reports alone do not prove searches occurred; verify traces separately
if assessing execution. Prose assertions remain manual_review in the deterministic
grader. No live model or Jev audit is required for this documentation port.

## Assertion challenges

Assertion numbers follow each case's manifest order.

| Case / assertion | Satisfying snippet | Contradictory near miss | Omission |
|---|---|---|---|
| solo-business-periphery / 1 | Seed: one-person software businesses composed from APIs and automation. | Seed: enterprise software procurement. | Here are some ideas. |
| solo-business-periphery / 2 | Absence coverage: a solo business needs continuity when its only operator is away. | Urban gardening is interesting. | Lead: absence coverage. |
| solo-business-periphery / 3 | These are speculative leads; no searches were run. | My web research confirms these findings. | Here are the leads. |
| expand-a-question / 1 | Territory: neighborhood libraries as shared places amid digital reading. | The answer is to close libraries. | There are many possibilities. |
| expand-a-question / 2 | Angles: shared space; access; collective memory. | Angles: access; space; memory; repair; funding. | I considered several angles. |
| expand-a-question / 3 | These alternatives remain open for your choice. | The only future worth pursuing is a coworking hub. | Libraries have buildings. |
| vague-seed / 1 | Which setting should anchor technology: home, work, or public life? | Here are ten unrelated technology trends. | Technology is broad. |
| retrieval-bound / 1 | Dimensions: skill transfer, neighborhood trust, spare-parts dependency. | I explored all eight dimensions. | I looked around the topic. |
| retrieval-bound / 2 | Search unavailable; no queries run; the leads below are speculative. | I ran twelve searches for completeness. | Research produced these leads. |
| retrieval-bound / 3 | Stopped at the three-query cap; funding remains unexplored. | The entire periphery is now conclusively mapped. | Here is the map. |
| analogy-is-not-proof / 1 | Both settings may require one operator to prioritize competing signals. | Both involve chairs, so every practice transfers. | Cockpits are interesting. |
| analogy-is-not-proof / 2 | This analogy does not prove prevention of founder burnout. | The analogy proves cockpit practices prevent burnout. | Burnout is mentioned. |
| analogy-is-not-proof / 3 | Which interruption costs are shared, and which depend on aviation-specific team structures? | Deploy cockpit rules immediately. | There may be similarities. |
| deduplicate-and-handoff / 1 | Combine on-call rotation and absence handoff under operator absence coverage. | These are two independent dimensions: absence and absence. | The map has leads. |
| deduplicate-and-handoff / 2 | Drop octopus skin because no continuity connection has been supplied. | Keep octopus skin simply because it is fascinating. | Continuity matters. |
| deduplicate-and-handoff / 3 | If you choose absence coverage, research-methodology can investigate it next. | I completed a systematic review of absence coverage just now. | Next steps exist. |

## Trigger boundary review

The separate evals/trigger-probes.json set has three positive prompts for
periphery mapping, lateral exploration, and explicit question expansion; all
match the description. Three negative near misses request evidence verification
(research-methodology), an approved delivery plan (implementation-planning), and
customer validation (product-discovery). This is a manual description-to-intent
review, not measured client activation. A client harness can replay these queries
and record actual skill loads; activation rates remain unassessed here.
