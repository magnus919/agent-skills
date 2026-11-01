# Intent routing review — #755 and #761

Source baseline: `64f78597c23f7f073509f57e4381e1e03bcb766d`.

## Smallest surface and ownership

The existing README lists skills by canonical name. Add a plain-language entry
map and a focused agent-trust handoff guide instead of a new routing skill or pack.
This gives a reader explicit links without another activation unit or duplicate
method. Runtime discovery behavior is not established by this choice.

Reviewed descriptions, tags, existing README summaries and cross-links for:

| Existing owner | Metadata review | Routing change and boundary |
|---|---|---|
| neckbeard | Description already owns change lifecycle; tags include SDLC/delivery/evidence | Opaque name now reached by “Take an issue through implementation and a verified PR”; it composes specialists |
| harness-engineering | Description already owns instructions/tools/state/recovery/loops/factories | “Fix an unreliable agent or build its runtime”; model training and production operations remain separate |
| implementation-planning | Description and tags already name approved plans, dependencies and rollout | “Plan implementation of an approved spec”; does not approve needs or implement |
| code-review | Description/tags already name patch/PR review and verdict | “Review this patch or pull request”; does not implement the fix |
| verified-delivery | Description already requires end-to-end authority and gates | “Finish an authorized change through merge and verify it”; cannot grant authority |
| ai-governance | Capability admission, earned autonomy and engineering decision rights have explicit entry sections | Separate admission from action grants; policy is not proof of enforcement |
| agent-production-operations | Runtime control-plane description and tags already cover rollout/fallback/escalation | Consumes grants and enforces current scope; not permission or evaluation owner |
| agent-evals-and-observability | Description now covers monitor independence and oversight quality (#760) | Task, conduct, detection and delivery evidence remain distinct |
| ai-operating-economics | Description/tags already cover adoption/scale/constrain/redesign/retire and cost/outcome evidence | Common pilot-scaling question routes here, with specialist handoffs |
| product-discovery | #757 added external problem path while preserving draft review | Distinguish customer evidence, internal requirements and artifact-first modes |
| chief-of-staff-methodology | #756 added founder/executive language and tags | Founder operations and operating rhythm route without granting executive authority |

No skill description needs another speculative keyword expansion for this README
change; no skill directory or eval manifest is modified. Generated projections were
checked and remain current. No alias or client feature is assumed. The existing
metadata work in #756/#757/#760 remains canonical rather than copied here.

## Static before/after probes

`static-probes.json` preserves a fixed 14-intent literal README lookup. At baseline,
none had an exact question/job entry; after the change, all 14 do. This measures
explicit navigation coverage only: readers can follow the named links from those
entries. It is not a model activation score, general semantic retrieval result,
search-engine ranking, or evidence that the old skills were undiscoverable by other
phrasing. All 369 local link targets across the README, trigger index, and new guide
exist. Anchors are supplied explicitly for the three detailed routes.

`discovery-probes.json` supplies 19 expected routes/modes, including near misses.
Manual review compares those expectations with current owner descriptions and
handoff sections; no live client was executed. Seven trust routes each identify
skills, evidence exchanged, decision owner, stop/escalation, disposition and limits.
Synthetic examples cover correct-answer/unauthorized-action failure, control
weakening, and review overload. Synthetic throughput numbers illustrate arithmetic,
not observed organizational evidence.

Challenge review: a satisfying route chooses the named owner and retains the case's
boundary. A contradictory near miss chooses a neighboring owner that loses that
boundary (e.g. admission treated as an action grant, draft interview for a diff,
harness for fine-tuning). Missing evidence is an answer naming no owner, omitting
the decision authority, or claiming unperformed handoffs. Refusal cases must not
turn into surveillance or self-approved authority workflows. These are semantic
review anchors, not executable grader bindings or human adjudication.

## Dependencies and no-build limits

Protected-control detail is tracked by #759; monitor quality landed through #760.
The router names the dependency and does not claim #759 is merged merely because
it is linked. Supervisory-capacity assessment remains explicitly gated by #762;
solo-business orchestration by actual-user evidence in #758. Existing skills are
usable without claiming that either proposed bundle has been validated. No demand
or value claim is derived from raw install events, unique-user assumptions, or
popularity.

## Suggested GitHub topics for maintainer consideration

`ai-governance`, `agent-evaluation`, `agent-observability`, `product-discovery`,
`engineering-leadership`, `agent-operations`.

These map to existing capabilities, not proposed ownership. Repository topics are
outside tracked PR artifacts; this PR records recommendations and makes no topic
mutation or search-ranking claim. A future topic change should preserve useful
existing topics and be measured separately if ranking impact is claimed.

## Validation and limits

Skill structure/link validation and all three catalog freshness checks passed.
No new skill or loadable bundle exists, so no new generated registration is needed.
The static probes and link scan were executed; discovery labels and semantic
handoff expectations were source-reviewed, not run in a client harness. Actual
activation rates, user outcomes and external ranking remain unassessed.
