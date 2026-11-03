# Tool interfaces, permissions, events, and hooks

## Tool contract

Record purpose/non-goals, typed input/output, authority/resources, errors, latency
and output limits, cancellation, concurrency, idempotency/reconciliation, and
observable postconditions. A model-facing description must let a competent user
choose the correct tool; overlapping tools need a principled distinction.

Use a clear error taxonomy: invalid_input, denied, dependency_unavailable,
timeout, cancelled, execution_failed, partial_effect, success. Include retryable
only when replay is safe; success means the documented postcondition, not merely
HTTP 200. Return enough evidence to distinguish empty results from inaccessible
results. Bounded responses need an explicit truncation/retrieval path.

For task-to-tool matching and outputs too large for the model context, follow
[tool discovery and bulk results](tool-discovery-and-bulk-results.md). A valid
input schema alone does not establish that a tool is ready to call or that its
result can be safely resumed.

## Authorization at the execution boundary

Policy evaluates identity, scope, exact normalized operation, target resources,
and current state. Validate before authorization; revalidate if a pre-execution
hook changes arguments. Bind any approval to the final operation. For filesystem
or shell tools, address aliases, paths, symlinks, shell expansion, and subprocess
behavior in the security owner design rather than trust a prompt rule.

Permissions, sandboxing, and semantic review are distinct controls. A worktree
isolates checkout changes, not secrets, network, process privileges, or shared
services. Read-only can still expose confidential data. Denial must be visible;
do not retry under a different tool merely to evade policy.

For brokered login, browser cookies, or worker session handoff, read
[credential/session authority](credential-session-authority.md). Authentication,
session custody, and action approval need separate grants.

## Per-call concurrency and side effects

Declare resource keys and conflict classes. Two writes to distinct files may be
safe; a read during schema change may not be. Claim ownership via lease or lock,
and use fencing/version checks so an expired worker cannot publish stale results.
Cross-file or external effects need reconciliation beyond a local checkpoint.

For a replayable action: prepare operation ID/intended effect → authorize →
execute → reconcile observed effect → checkpoint → acknowledge. A crash after
execute but before checkpoint is an unknown-effect state, not a failed action
safe to repeat. Exactly-once behavior must not be promised from retries alone.

## Event pipeline and plugin seams

Separate durable events from extension callbacks. A useful pipeline is task
claimed → context assembled → proposal validated → permission decided → action
started → result observed → checkpoint persisted → continuation decided.
For each event define identity, ordering, payload version, retry semantics,
subscriber failure policy, retention, and sensitive fields. Not every callback
needs durable recording; consequential transitions do.

Hooks need explicit criticality:

| Hook role | Timeout/failure policy |
|---|---|
| Authority gate | Block/escalate; do not silently continue |
| Acceptance gate | Outcome unknown/failed; no completion |
| Optional telemetry | Degrade visibly within declared policy |
| Context enrichment | Continue only if required facts remain available |

Avoid recursive stop hooks and hook storms. Include an invocation ID, reentrancy
policy, latency bound, and cancellation/drain behavior. A Stop hook can refuse a
completion claim but does not automatically prove acceptance. Provider-specific
hook schemas/events belong in verified adapters, not a universal template.

Primary sources:
[Anthropic tool design](https://www.anthropic.com/engineering/writing-tools-for-agents),
[Claude Code hook reference](https://code.claude.com/docs/en/hooks).
Use them for mechanism-specific implementation and recheck the installed version.
Use [templates/tool-contract.json](../templates/tool-contract.json) and
[templates/event-contract.md](../templates/event-contract.md).

## Provider adapters and recovery

A model provider is an adapter boundary, not just an API key and model name.
Keep backend flags, provider-scoped model identities, context/output/image limits,
stream conversion and failure classification with the provider. Keep task budgets,
authority and the decision to continue with the runtime. Explicitly assign request
initiation and stream-stall timeout ownership: a nonblocking tool loop does not
make a stalled model request bounded. Avoid competing watchdogs that turn a slow
but valid response into repeated billable work.

| Provider observation | Runtime response | Evidence / boundary |
|---|---|---|
| Transient connection or stream failure | Bounded retry under the same task budget | Discard or separately mark incomplete output; never dispatch a partial tool proposal |
| Throttling | Backoff within deadline and shared quota | Distinguish rate pressure from invalid configuration |
| Context overflow | Diagnose committed history versus new input before shrinking | Preserve user intent and call/result structure; do not replay tool effects to recover missing text |
| Fatal credentials/model/request error | Stop or explicit approved fallback | Do not retry the same invalid request indefinitely |
| Capability mismatch | Transform only through an explicit compatible path or hold | An image placeholder preserves syntax, not the image's evidence |

Use typed error classes instead of parsing provider prose to decide recovery.
Record whether output is tentative, accepted into a turn, or durably committed.
A displayed stream fragment is not necessarily a replayable completion.

For context overflow, challenge a single oversized new tool result separately
from new user instructions or ambiguous mixed input. A placeholder may settle the
former without claiming its omitted evidence was seen; provide a retrieval path
when the task still needs it. If the latest user constraint cannot be retained,
stop visibly and obtain a smaller/recoverable input rather than silently act on
older instructions. Committed-history overflow may require compaction before
retry; replacing fresh input cannot solve every case. These are design rules;
the inspected Infinity implementation has narrower recovery paths and an explicit
remaining committed-history limitation. See [source findings](infinity-design-findings.md).

## Reattach clients without a replay-to-live gap

Treat client detachment, worker idleness, stopping an agent, and closing a task as
different lifecycle events. Choose background behavior explicitly; reconnecting
must not create a second execution of the same task.

For an active conversation, serialize snapshot capture and subscriber installation
with event emission, or use a cursor/sequence protocol that demonstrably closes
the equivalent gap. Register in the same serialized operation as rendering the
snapshot; taking a snapshot now and subscribing in a later task can lose events.
Resolve attach only after installation. Test one event immediately before, during
and after attach: each belongs in replay or subsequent live delivery, exactly once
within that attach protocol. This narrow UI guarantee says nothing about exactly-once
tool effects or delivery across every disconnect.

Persist pending choices before publishing them as actionable UI state; include
unresolved choices in reconnect snapshots. Persist dismissal/settlement before
removing them from the display. Bind responses to the current pending call, task
revision and authority; do not accept an obsolete choice after interruption.
Observers used for display/telemetry should remain fast and must not be mistaken
for an authorization gate. Export only approved visible content; internal or
hidden reasoning in a runtime snapshot is not permission to expose it.

Route interaction/review decisions to
[product-design-and-ux](../../product-design-and-ux/SKILL.md), returning the
reconnect and choice contracts to the runtime owner. Source: Infinity's
[observer contract](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/observers.md)
and corresponding pinned driver/thread paths in [findings](infinity-design-findings.md).

## Choose a bridge by session lifetime

| Tool behavior | Suitable adapter choice | Acceptance probe |
|---|---|---|
| Independent calls reconstruct state from explicit durable identity | Per-invocation bridge | A second call in a new process sees the intended durable state |
| Tool relies on in-memory MCP/session state across calls | Session-preserving bridge or redesign to externalize state | Create state in call A; read/use it in call B, then repeat after bridge restart |
| Mixed catalog with unknown state assumptions | Classify each tool before migrating | Record which calls need affinity, OAuth/session recovery and retained compute |

Infinity documents a long-lived local MCP proxy and fresh per-invocation Lambda
sessions. A tool that creates a temporary in-memory handle in A and consumes it
in B is a counterexample to transparent migration. Session-preserving bridges
retain process/connection cost and still need crash recovery. Externalizing state
requires access control, lifetime and reconciliation contracts; an MCP session ID
alone cannot recreate a vanished subprocess. Do not treat “MCP compatible” as a
session-equivalence or scale-to-zero guarantee. Source: pinned
[MCP compatibility](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/about/mcp-compatibility.md).
