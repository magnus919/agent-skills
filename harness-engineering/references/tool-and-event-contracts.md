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
