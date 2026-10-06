# Repair design: discovery and authorization

## Failure hypothesis

The repeated wrong calls suggest two distinct defects: the agent-facing catalog exposes an ambiguous search contract that accepts a human channel label where the operation requires a service-scoped channel ID, and the discovery index can remain stale after catalog changes. Denials are a separate authority outcome. I would not respond by adding more tools or trying alternate tools after a denial; first establish which failures are reproducible and at what boundary.

## Smallest repair

Keep the existing tool set and improve the discovery path and tool contracts. The catalog should expose a short task-oriented index, then load only relevant operations and their dependency order. Each operation description should state purpose, non-goals, prerequisite identifiers and how to obtain them, scope, side-effect class, and expected postcondition. For message search, distinguish `channel_id` from a display name in the field description and schema. Require the API-issued ID, name its namespace/account, and offer a separate explicit resolution operation only if the service supports that capability and the actor is authorized to use it. Do not silently reinterpret a name as an ID.

On no matches, stale-version indication, or suspected index lag, permit one bounded refresh against the authoritative catalog, then search once more. Preserve the index/catalog revision and refresh result so the agent can tell “no capability exists” from “index unavailable.” If the refreshed search still has no suitable operation, report that and stop or escalate. An API validation error should identify the bad field and next valid step without leaking protected existence details. A denied call remains denied; do not retry via a different route or weaker permission.

## Acceptance evidence

Use a fixed set of representative tasks with baseline and candidate catalog/runtime revisions. Include: a task naming a channel by display name; a valid ID lookup; a catalog mutation that makes a formerly missing tool discoverable after refresh; a true no-match after refresh; a malformed ID; a missing connection/prerequisite; and an operation denied by permission. Capture discovery queries, catalog revision, selected tool and arguments, calls, authorization decisions, and resulting state. Verify the name-only request causes the supported ID-resolution path or a clear request for the ID, never a search call with the wrong value. Verify exactly one bounded refresh occurs and no-match remains distinct from denied and dependency-unavailable.

The task oracle should check the intended message set and source scope, not just a successful response. A separate trajectory review checks that no unnecessary definitions were loaded and that no alternate route followed denial. Compare on identical tasks, state, model/runtime, permissions, service version, and result semantics. Repeat stochastic tasks as needed. Report task outcome, wrong/extra calls, authorization violations, failures, context usage, latency, and actual monetary cost separately; missing measures stay unavailable. A successful synthetic design example or lower token count alone does not establish improved task completion. Roll back the catalog or routing change if it causes a missed capability or unauthorized attempt.
