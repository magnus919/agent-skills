# Make distributed knowledge discoverable before search

Use when a competent agent reinvents an existing capability, cannot formulate a
useful query, misses a specialist, or loses its route after compaction. The
second OpenRig video motivates the pattern; source records S28–S39 distinguish
author reports, documented mechanisms and independent foundations. This is our
portable synthesis, not a claim that a spatial metaphor makes models competent.

## Orient before retrieving depth

Start from one representative job. Identify what a newcomer must recognize before
choosing tools or implementation: major capabilities, ownership boundaries,
unfinished prior work, accepted interfaces, consequential constraints and where
status is authoritative. Build a small, broad capability map with a question or
condition for every route. Use templates/orientation-map.md. A list of filenames
is insufficient when the reader does not know why any one matters.

Expose enough breadth to discover neighboring domains, then retrieve relevant
detail. Different roles may need different views over the same sources. Leave
context for execution, verification and reporting; there is no universal map
size, token percentage or requirement to load every domain. Reuse the project's
existing README, architecture index, skill router and state owner rather than
creating a competing knowledge portal.

Before constructing a new subsystem, follow the capability/architecture routes
and inspect existing or unfinished implementations. Record why reuse, completion,
extension or replacement fits the actual contract. A keyword search with no
match is not proof a capability is absent. Conversely, discovering an existing
implementation does not make it suitable: inspect current behavior, constraints
and defects before choosing reuse.

## Define the edges, not only the nodes

Give a route a purpose and relationship: implements, explains, depends on,
supports, supersedes, owns or knows-about. Keep navigation, evidence, task
dependency and authority edges distinct. A link to an expert means ask about a
domain; it does not authorize that expert to approve a mutation. Human-readable
labels and aliases help discovery, while typed relationships prevent an adjacent
concept from being mistaken for the same system.

[SKOS Primer](https://www.w3.org/TR/skos-primer/) offers vocabulary for labels,
broader/narrower and related concepts. [PROV Primer](https://www.w3.org/TR/prov-primer/)
offers provenance distinctions among entities, activities and agents. Borrow
only what the problem needs; neither standard requires a graph database, proves
truth, or supplies an agent permission system.

A route may terminate at a versioned document section, code/test artifact,
authorized historical record, live specialist or human decision owner. Include
how to proceed when the answer is outside the map: search owning code/help,
consult an adjacent map or authorized expert, or report the missing route.
Missing content, inaccessible content, broken routing and incorrect synthesis
are different defects. Do not create a note for each symptom before locating
which defect actually occurred.

## Stable addresses, changing content

Prefer one maintained source with a stable locator over copied summaries. A
section reference can reduce irrelevant retrieval, but Markdown heading anchors
are renderer-dependent and may collide or change when headings are renamed.
Verify the actual resolver; use explicit IDs/aliases or an owned redirect where
needed. Preserve the source revision consumed, access scope, last-checked version
and cache dependencies. A stable address may serve new content without changing
its name; prior acceptance receipts remain bound to their original bytes.

When composing a role/situation view from sections, preserve source references,
versions, order, conflicting claims and required exclusions. A route's existence
does not prove its destination is appropriate, current, authorized or read.
Test heading rename, missing source, denied access, stale cache and contradictory
sources. Never silently discard authority/acceptance constraints to fit a budget.

## A directory of knowledge holders

Use templates/expert-directory.md to record domain, supporting work/artifact,
stable role, current occupant, availability, permitted contact route, question
scope, freshness and fallback. Peers need enough awareness of each other's
expertise to route questions beyond the lead. The lead remains responsible for
integrating the answer; expert testimony is not ground truth.

Distinguish three operations: consulting an existing authorized artifact,
querying retained session evidence, and waking/launching an agent. They have
different cost, privacy and authority implications. OpenRig documents historical
`ask` without wake as excerpt retrieval, not a generated expert answer. Historical
statements may be stale, mistaken or injected; corroborate them against current
sources. Do not silently wake a dormant session, export private logs, expose
hidden reasoning or inherit its old grant. An unavailable expert needs an owned
fallback rather than invented testimony or endless retry.

The [transactive-memory design paper](https://arxiv.org/abs/2305.05115) motivates
explicit knowledge of who knows what, with encoding/storage/retrieval distinctions.
It is a human-robot design proposal, not evidence that this directory improves
LLM-fleet outcomes. Evaluate the transfer locally.

## Test minimum useful competence

In a fresh session and again after interruption/compaction, ask a representative
worker to identify the relevant existing capability, find its current source,
locate an appropriate expert and recognize the map's boundary. Inspect the
actual path, mistaken branches, necessary constraints retained and resulting
work. Include a task requiring a real new capability, so the procedure does not
force reuse of an unsuitable component. A link checker establishes navigability
only; a real task probes discovery and application.

Record human findability too: can the responsible person explain which route
failed, why a source is trusted and what repair is proposed without reading every
worker transcript? Human inspectability is a design objective, not a claim of
shared human/model cognition. Fix the earliest failed edge/content/decision and
verify the fresh and resumed paths. Route single-agent loading mechanics to
harness-engineering and evaluation design to agent-evals-and-observability.
