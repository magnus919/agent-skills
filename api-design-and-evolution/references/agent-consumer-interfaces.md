# Interfaces for Agents and Automations

Use this review when an agent, script, or another automated consumer must discover
capabilities, pass results between operations or services, recover from failures, or
retrieve a large result. The question is whether the interface lets that consumer
complete a real task with bounded, interpretable steps. It is not a requirement to
adopt MCP, tool search, a gateway, or any particular agent framework. A small static
tool set or ordinary API can be the best fit.

## Start with the Task

Write down the task outcome, the information and actions needed, the accountable
system for each fact or change, the consumer's authority, and the evidence of
completion. Trace the task across services and note hand-offs and failure points.
Design for the actual consumer mix: an agent may act alongside people, and a human
interface can remain valuable for exploration, oversight, exceptions, and review.
Treat claims that agents replace dashboards or all human-facing interfaces as
hypotheses, not design constraints.

For each operation the consumer may need, specify:

- **Discoverability:** a recognizable task or domain name, a concise purpose, when to
  use it, when not to use it, required authority, and its side-effect class. Group
  related names consistently and distinguish similarly named operations by scope or
  intent. A description or searchable catalog helps only if the intended client
  exposes and uses it. Use static documentation or a short list when discovery is
  already easy; add search or deferred loading only when catalog scale or measured
  confusion justifies it.
- **Prerequisites and identifiers:** required inputs, where to obtain each one, and
  the namespace and authority under which it is meaningful. Preserve stable IDs for
  follow-up calls, alongside human-readable labels where useful. Say whether an ID is
  service-local, tenant-scoped, versioned, opaque, or portable. Never imply that a
  value from one service can be passed to another without a documented mapping.
- **Actionable failure:** distinguish invalid input, missing prerequisite, denied
  authority, not found, conflict, transient dependency failure, and partial or
  uncertain completion when these require different next steps. Return safe, bounded
  detail: what failed, which input or prerequisite needs attention, whether retry is
  safe, and the next valid step or operation. Keep protocol/transport errors
  distinct from operation-level failures. Avoid tracebacks, secrets, or sensitive
  object-existence hints.
- **Bounded results:** state default and maximum result size, sorting and tie-breaks,
  filter or range support, truncation behavior, and continuation semantics. The
  caller should know whether it has a complete result, how to get the next slice,
  and whether records can repeat or disappear during continuation. Avoid silently
  returning an unbounded collection or a truncated result that looks complete.
- **Artifact retrieval:** for large or non-text results, return a small summary and
  an explicit, authorized retrieval reference with content type, size or limits,
  expiry/version behavior, and the operation for fetching it. State whether the
  reference is opaque and whether it can be passed across service boundaries. A
  resource link or URI is useful only when the consumer can actually read it; do not
  assume every linked resource is globally listed or automatically available.
- **Safe composition:** define how one operation's output satisfies another's
  inputs, including identifier translation, authorization context, state/version
  preconditions, and completion status. Define retry and idempotency at each side
  effect. A successful tool call may mean only “accepted”; identify how to observe
  terminal completion and partial outcomes. Composition can be explicit in code,
  a workflow, or agent planning; it does not require one mega-operation.

## Discovery and Protocol Choices

Choose discovery based on catalog size, change frequency, task ambiguity, and the
target client's behavior. An explicit list, generated API reference, OpenAPI
operation tags, CLI help, MCP `tools/list`, or a search/deferred-loading layer can
each work. In MCP, tools are model-controlled actions while resources are
application-controlled context; clients decide how to present or use resources.
MCP supports paginated tool/resource listing, resource reads, and tool results that
can include resource links, but protocol support does not prove a given host will
show, search, or fetch them. Listing and URI-read mechanics also do not promise
cursor durability, snapshot consistency, authorization portability, artifact
lifecycle, or task-level completeness. Define those properties in the interface
contract and verify the deployed client and server together.

Structured schemas can make inputs and outputs easier to parse and validate, but
they do not establish domain correctness, authorization, or whether a downstream
operation accepts an identifier. Keep machine-readable data and actionable human
context aligned. Where the chosen protocol has multiple error channels, explain
which failures the client is expected to expose to the model and how the user sees
them.

## Review Evidence

Use [templates/agent-consumer-interface-review.md](../templates/agent-consumer-interface-review.md).
Probe one representative multi-step task, an invalid or missing prerequisite, a
permission denial, an oversized result, a failed artifact read, and an ambiguous
completion or retry. Record the actual tool/API trace and task outcome for the
intended client. A schema pass, static inspection, one successful mock, or vendor
demo is useful preliminary evidence, not proof of reliable task completion. Compare
with a baseline on the same tasks and preserve failures as cases. See
[contract-verification.md](contract-verification.md) for the wider provider,
consumer, compatibility, and deployed-boundary evidence model.
