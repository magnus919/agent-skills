# Task-relevant tool discovery and bulk results

## Match tools to a task, not only to its arguments

Begin with the user task, required outcome, authority, and available source state.
Find the capability that can produce that outcome, then surface enough of its
operating contract to choose and call it safely:

- purpose, scope, and meaningful non-goals;
- typed input and output schemas, examples, and observable postconditions;
- prerequisites such as connection, authentication, setup, permissions, or
  required source identifiers;
- dependency ordering, including which result or identifier must flow into the
  next call;
- errors that distinguish empty/no-match from denied access, missing prerequisites,
  unavailable dependencies, and partial or failed execution;
- result size, pagination or retrieval, and recovery after timeout or restart.

For example, a migration task may require `inspect_schema` → `plan_migration` →
`apply_migration`; schemas alone do not show that ordering, the required backup,
or how to recover if apply times out. Show the dependency graph and prerequisites
alongside the relevant schemas. Avoid exposing unrelated operations just because
they share a server.

Use the simplest reliable discovery surface for the catalog. A small, stable set
can remain statically visible with a concise index and complete contracts. For a
large, changing catalog, evaluate search, routing, or deferred loading against
representative tasks and record missed matches, wrong matches, latency, and
context cost. Discovery can be semantic, lexical, manually curated, or a mix;
regex matching is one implementation option, not a universal design. When a
catalog changes, invalidate or refresh cached indexes according to the actual
provider/runtime contract. On a stale-index or no-match result, allow a bounded
refresh against the authoritative catalog, then report no suitable capability or
escalate if the required operation is still unavailable. Do not treat a discovered
tool as authorized: validate its final arguments and enforce permissions at
execution time. A denial remains a denial; do not search for a weaker tool or
alternate route to evade it.

## Keep large results addressable outside model context

When a result exceeds a useful context budget, compute, filter, or store it in an
environment suited to the data and return a compact summary plus a durable or
explicitly expiring artifact handle. The model should be able to inspect a sample,
ask follow-up questions, retrieve bounded pages, or pass the artifact to another
approved step without silently losing the full result.

Define the artifact contract before implementation. It should say:

- **Identity and schema:** handle; artifact kind and schema/version; exact or
  estimated row/item count; sample and sample method; source identity and source
  revision/snapshot; query or operation identity; creation time and relevant
  filters. Record a content hash when it helps detect change or corruption.
- **Completeness:** complete, partial, or unknown; whether counts are exact;
  truncation, paging, timeout, permission, or source limitations; and a cursor or
  recovery procedure when continuation is possible. Empty complete results remain
  distinguishable from missing, denied, failed, or incomplete results.
- **Identity semantics:** namespace/source-qualified record keys and versioning;
  whether identifiers are stable; whether two records are known equal, merely
  candidates, or unresolved; and how conflicts, duplicates, and deleted records
  are represented. Represent unmatched and duplicate identifiers explicitly;
  preserve source snapshot/time-window differences that can change join meaning.
  Never merge records based only on matching display names.
- **Access and lifecycle:** who/which runtime can read or share the handle, scope
  and sensitivity, expiry/retention policy and owner, and what an expired or
  revoked handle returns. Deletion/eviction must preserve a documented recovery
  route and respect the system's authorization and retention rules.

Keep this metadata in the model context and the bulk payload outside it. Follow-up
tools should accept the handle and a bounded operation such as a page, projection,
aggregate, or filter. Avoid forcing the model to reconstruct a large result by
repeating an unbounded source query. The runtime or storage layer must enforce
handle access; prose in a prompt cannot do that.
An included sample illustrates the artifact shape; it is not evidence that every
row or identity match has been validated.

If code or tools move data between sources, authorize that exact transfer and
preserve each source's scope; model-generated orchestration does not broaden
authority. Keep computation sandboxed with explicit time, memory, network and
output limits, plus monitoring appropriate to the operation. Route custom runtime
and security design to [runtime design](runtime-design.md) and the repository's
security owner; do not infer that an MCP connection or code sandbox supplies
every required control.

This is an architecture-neutral contract, not a demand to add artifact storage to
every agent. Small bounded responses may remain inline. Use [the bulk result
contract](../templates/bulk-result-contract.json) when an externalized result
needs a concrete starting point, and adapt it to the source's actual guarantees.

## Evidence boundary

MCP documents tool listing and schemas, structured outputs, and resource links;
those protocol features do not prescribe task planning, artifact authorization,
identity resolution, or retention semantics. Anthropic documents tool discovery
for large catalogs and code-assisted filtering for some search results. These
are product mechanisms, not comparative evidence that dynamic discovery or
externalized results improve task success in a particular harness. Verify the
target runtime and test realistic tasks, including no-match, denied access,
prerequisite failure, partial results, expiry, and resume.

See [source notes](primary-sources.md#tool-discovery-and-large-results) for
first-party references and checked date.
