# Agent interface enrichment: evidence and validation plan

Scope issue: [#656](https://github.com/magnus919/agent-skills/issues/656).
Planned on 2026-10-04 against `4e843ac` before candidate task responses.

## Orientation and decision

[Dashboards Are Dead](https://www.youtube.com/watch?v=YiFqcu9YA38), Sarah
Simionescu, Composio, supplies hypotheses only. The transcript introduces the
bug-fix demo as a mockup (4:54), comparative results as early and unreleased
(6:27), discovery with prerequisites (5:16–5:46), and externally processed
cross-app results (8:06–8:39). None establishes independent efficacy, universal
context degradation, or dashboard obsolescence.

Improve four existing skills, covering five suggestions. Do not create a vendor
skill, add a gateway dependency, or change the repository's release/grader policy.
Rollback is a normal revert of this documentation/eval change; no external product
configuration or user data is changed.

## Work and evidence ownership

| Suggestion | Owner | Gap to investigate | Evidence needed | Validation |
|---|---|---|---|---|
| Discovery plus prerequisites | harness-engineering | Existing tool contracts and JIT retrieval may omit dependency-bearing discovery | Official discovery/tool-search behavior and task dependencies; retain static alternative | Wrong-tool and unresolved-identifier challenge; dependency denial |
| Bulk artifacts outside context | harness-engineering | Context references may omit completeness and durable retrieval contracts | Official code execution/resource mechanisms; documented limits vs proposed artifact contract | Pagination, expired handle, missing IDs, cross-source mismatch |
| Agent API consumer | api-design-and-evolution | Generic API contracts may omit discovery-to-completion review | Official tool/resource/interface semantics | Consumer scenario with prerequisites, actionable errors, bounded retrieval |
| Human delegation through own agent | product-design-and-ux | In-product AI guidance may omit external entry and cross-app recovery | Primary human-AI and authorization guidance | Revocation/partial completion with review and recovery |
| Evaluation of these mechanisms | agent-evals-and-observability | General eval methods may lack a matched mechanism-specific protocol | Primary agent evaluation guidance plus actual repository grader behavior | Comparable conditions, failure inclusion, separate task/trajectory evidence |

Each worker uses a separate worktree and Luna-pinned model, checks existing
coverage first, records claim-to-source mappings and source dates, adds only
conditional useful instructions, preserves old eval IDs, and challenges each new
assertion with satisfying, contradictory, and absent evidence. Root reviews and
integrates. Generated catalog files are regenerated only after integration.

## Frozen task-response screen

Use fresh Luna sessions for the old and candidate versions of each skill. Supply
the same task, output budget, available skill resources, and no internet or
external mutation. Both conditions can read their full skill and relevant
references/templates. Hide expected outcomes and rubrics from generation.
Record model, skill/source hashes, prompt, actual outputs, finality/failures,
elapsed time, and available usage; mark unavailable metrics explicitly. These
synthetic design tasks test guidance application, not live tool execution.

Before generation, freeze these task prompts and review criteria:

| ID | Identical prompt for both conditions | Independently reviewable criteria |
|---|---|---|
| discovery | An agent has 240 support tools. It repeatedly calls message search with a channel name where the API requires an ID. Catalog search sometimes returns no matches because an index is stale; some tools are denied. Design the smallest repair and its acceptance evidence. | Task-relevant selection with a valid small/static alternative; identifier prerequisite ordering; distinguishes stale/no-match/denied; explicit safe recovery; comparison using accepted outcomes |
| artifacts | A cohort query returns 80,000 IDs in pages; only page one is saved. An agent uses a stored handle to join against another app with different user identifiers, then reports a distribution. The handle can expire during resume. Design a safe workflow and completion contract. | Completeness before claims; identity mapping and unmatched/duplicate accounting; external computation with bounded inspection; provenance and protected retrievable handle; expiry/resume recovery |
| api-consumer | Review an API for an agent that resolves a customer name, reads paginated events, and requests an export. Some names are ambiguous and export creation can time out after taking effect. Provide a consumer review contract with acceptance evidence. | Explicit identifier/ambiguity prerequisite; bounded read completeness; actionable failure outcomes; idempotency/reconciliation after timeout; scope checks and verified task postconditions |
| delegation | A customer uses their own agent to request a billing correction across two services. One service applies the change before the customer revokes authorization; the other is still pending. Specify the product flow, human review, and recovery behavior. | Human outcome/accountability; external actor/authority/scope; revocation stops remaining work; partial effects visible with reconciliation; human review/intervention and observable completion |
| eval-design | A team claims tool discovery and external result handles improved its agent because token counts fell and a demo succeeded. Design a comparison and release decision for those changes, including fresh-session repetition and a permission-denied case. | Separate hypotheses/ablations; matched old/new tasks and configuration; correct completion plus resource measures; discovery miss/denial/partial artifact/repeat failure slices; explicit evidence limits and safety decision |

Root records model-review verdicts with output excerpts and distinguishes met,
not met, and not shown. Model judgments are advisory model review, not human
labels or calibrated accuracy. Structural CI's fake adapter and prose assertion
`manual_review` cannot establish a semantic pass. Keep negative/neutral results;
do not change rubrics to manufacture uplift. Narrow or remove unsupported guidance.

## Integration and delivery gates

1. Independently check primary sources and meaningful deltas; review authority,
   completeness, identity, and failure boundaries across the combined change.
2. Validate all manifests, format/quality, reference size/link rules, eval coverage,
   generated catalogs, and relevant existing script tests. Review actual screen
   outputs and adverse cases; disclose what remains untested.
3. Create one ready-for-review PR closing #656 with validation, AI assistance, and
   final-head review evidence. Four changed skills stay within the five-skill cap.
4. Resolve actionable findings, await required checks on the exact head, merge,
   synchronize local main, and verify matching revisions and clean state.

Completion means supported, useful guidance merged with honest evidence. It does
not mean these patterns are proven to improve production task success across
models, applications, or tool catalogs. That requires representative execution
traces, controlled repeats, and appropriate independent adjudication.
