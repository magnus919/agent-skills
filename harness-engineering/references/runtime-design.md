# Tools, environment, and lifecycle

A custom runtime needs an explicit action loop: assemble context, call model,
validate the requested action, authorize, execute, observe, checkpoint, and decide
continue/stop/escalate. Keep the model's proposal separate from execution authority.

## Tool affordances

Use bounded typed inputs, structured results, timeouts, cancellation, and errors
that distinguish denial, bad input, unavailable dependency, and execution failure.
Report enough context to correct a call without leaking secrets. A tool that hides
stderr or truncates a decisive error makes feedback unreliable.

Classify concurrency per call and resource, not merely by tool name. Two reads may
be safe; a read during a migration or two writes to one file may not be. Keep
permission decisions tied to target, identity, current scope, and exact operation.
Do not cache an authorization result across changed arguments or state.

Fail closed on sensitive actions and enforce controls outside the prompt. Sandbox
untrusted code and treat retrieved instructions as data. Log minimal redacted
operation/decision references, not unrestricted command output or personal data.

## Reproducible environment

Inspect lockfiles, runtime pins, CI, service health, credentials handling, and
network assumptions. Split setup/readiness from verification: installing packages
on every check can mutate lockfiles and consume time. Use an isolated checkout for
concurrent work, and explicit service teardown ownership. A process being alive
is weaker evidence than readiness for the requested task.

## Lifecycle

Startup reads authoritative intent/state, checks the current revision and dirty
work, validates environment, and picks bounded work. End-of-session records what
actually happened, incomplete checks, and recovery instructions. Clean means
restartable with known state; it does not authorize git reset, deleting files, or
committing someone else's work.

Test denial, dependency failure, timeout, partial write, cancellation, and resume.
Hooks must use the runtime's actual trust and failure semantics; product-specific
claims need pinned primary documentation or source before implementation.

## Choose the engine seam before replacing its loop

For an event-driven runtime, keep engine policy separate from platform scheduling.
Use the highest-level seam that can express the actual requirement:

| Requirement | Choose | Retain / take ownership of |
|---|---|---|
| One process owns input delivery and active conversations | Resident system with local scheduler | Standard engine ordering, state synchronization and dispatch; application owns process/queue durability |
| A durable platform queue already schedules each conversation | Platform-driven step API | Same engine, externally supplied input sender; platform owner handles serialization, acknowledgement, visibility, redelivery and retention |
| Different stores, tools, model backend or UI | Replace the corresponding interface | Keep the loop; test the replacement against its behavioral contract |
| Preparation/completion/dispatch semantics must change | Low-level pipeline composition | Application now owns commit-before-dispatch, interruption, dedup, replay, cancellation and partial-output policies |

Do not drop to a low-level API merely to add a provider or change persistence.
Draw the ownership map before implementation:

| Seam | Responsibility | Selection / challenge |
|---|---|---|
| Conversation store | Messages, ancestry, spawn positions and summaries | Reconstruct children before/after compaction |
| Runtime state store | Processed IDs, metadata, subscriptions, pending choices | Restore it consistently with the conversation store |
| Input sender and scheduler | Deliver resumptions, serialize each conversation | Lost/duplicate delivery and acknowledgement-order tests |
| Thread configuration source | Reconstruct tools, extra instructions and notifier | Restart without process-local launch objects |
| Model source | Resolve a provider/model/capability selection | Missing model, changed context/image support, root/leaf policy |
| Provider adapter | Backend options, stream conversion, limits and classified errors | Initiation failure, stalled stream and capability mismatch |
| Observer / client adapter | Display events, derived state and live reattachment | Snapshot-to-live race and recovered pending choices |

The split makes one engine reusable in a local daemon and a platform handler.
Portability depends on preserving those contracts, not merely implementing the
same trait names. Use the
[worked coding task](event-runtime-worked-example.md) to follow the seams across
a detach, CI wait, restart and integration. For provider behavior use
[tool/event contracts](tool-and-event-contracts.md#provider-adapters-and-recovery).

### Reconstruct configuration, then bind it deliberately

Persist the inputs needed to reconstruct tool instances and instructions: tenant,
repository, configuration revision, server definitions and provider-scoped model
selection. Process-local objects are not a durable configuration store. Resolve
child configuration through an authenticated root-to-tenant mapping when it belongs
to the conversation; use leaf-specific records for narrower child capabilities.
Generated thread-ID shape and inherited prose cannot establish tenant identity.

Record when each value becomes bound:

- Launch-time overrides may exist only in the creating process. For restartable
  work, supply a reconstructable configuration source instead.
- A loaded thread may cache its resolved tools/prompt/notifier until idle/reload.
  Specify invalidation or a controlled reload for configuration changes; refreshing
  a stored record alone need not affect an already active worker.
- A model selection can be resolved at a different boundary. In the inspected
  Infinity step, resolution happens before `run_completion`; synchronous
  loop-back inside that call reuses the resolved provider/model. A selection
  change must not be promised to apply between every internal model invocation.
- Validate persisted selections against the current catalog. On unavailable
  configuration/model, hold or use an explicitly approved compatible fallback;
  never silently choose a broader tool set or another tenant. Reassess context
  budget and multimodal inputs when capabilities change.

Cached configuration is not cached authority. Recheck current grants at the
execution boundary even if tool objects remain loaded. Revoke through external
controls while arranging any required reload. Test configuration loss, root/leaf
mix-up and model removal after process death.

Source: [Infinity engine customization](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/customizing-the-engine.md),
[dynamic configuration](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/dynamic-configuration.md),
[thread implementation](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/thread.rs),
checked at the pin in [follow-up findings](infinity-design-findings.md). The tables
are reusable design guidance, not a claim that every runtime implements these APIs.
