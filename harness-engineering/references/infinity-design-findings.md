# Infinity architecture follow-up findings

Checked 2026-11-03 against source pin
`1abc6fcff1f186124f924b56aa92c3a3684c90c5`. Extends
[initial source records](infinity-sources.md), S1–S9. Static implementation and
primary-document inspection; no upstream Rust execution or live model/cloud runs.
The procedures are design synthesis, not a claim that every proposed control is
implemented in Infinity.

## S10 — Engine composition and reconstruction

[Engine customization](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/customizing-the-engine.md),
[step mode](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/step-mode.md),
[dynamic configuration](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/dynamic-configuration.md),
[config types](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/config.rs),
[thread](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/thread.rs),
[model source](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/model.rs).

The builder exposes independent store, model, configuration and scheduling seams.
The conversation store owns messages/ancestry/summaries; runtime state includes
processed IDs, subscriptions and pending choices. Local scheduling and platform
step execution retain the standard engine; low-level pipeline replacement
transfers preparation/commit/dispatch responsibility to the application.

ThreadConfig reconstructs tools, extra prompt and notifier, whereas root launch
overrides can be process-local. Child-to-root lookup is an application choice for
tenant-wide configuration; narrower leaf capability sets need explicit mapping.
`Thread::resolved_config` caches for the loaded thread. `Thread::step` resolves a
model before `run_completion`; internal synchronous tool loop-back reuses those
arguments. Therefore the docs' “per completion round” language must not be read as
re-resolving the model between every provider invocation. Both-store compatible
restore and configuration-version references are required design questions;
the recovery manifest recommended here is our proposal, not an upstream feature.

Applied in [runtime design](runtime-design.md) and [state/recovery](context-and-state.md).

## S11 — Provider boundary and incomplete evidence

[Model providers](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/model-providers.md),
[protocol errors](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-provider-protocol/src/completion.rs),
[event processor](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/event_processor.rs).

Providers own backend flags, model catalogs/capabilities, stream adaptation and
classified errors. The core branches on transient, throttled, context-overflow and
fatal classes; it does not parse error prose to decide recovery. The inspected
completion code deliberately lacks generic initiation and stream-inactivity timers;
those belong to provider behavior or an explicitly designed application control.
Partial streams, known-safe turn content and fresh unvalidated input differ.

`recover_from_overflow` can substitute a placeholder for one identifiable new
replaceable result/event. Ambiguous input or oversized user input stops rather
than silently continuing without the user's words. Committed-history overflow
still has a noted compaction/deferral limitation. Image degradation can preserve
message syntax without preserving the missing visual evidence. Do not copy the
source's numerical retry/backoff defaults as universal operational thresholds.

Applied in [tool/provider contracts](tool-and-event-contracts.md#provider-adapters-and-recovery)
and positive evaluation cases. Mechanism behavior has not been reproduced here.

## S12 — Lifecycle, observer and attach boundary

[Observers](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/agent-systems/observers.md),
[background agents](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-code/background-agents.md),
[thread](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/thread.rs),
[driver](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/local/driver.rs),
[router](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/local/router.rs).

`on_event` is synchronous display/derived-state delivery, not an authorization
policy. Stateful pending-choice creation/removal is awaited before its event;
`Thread::load` restores choices and replay exposes them. The documented local
attach guarantee depends on snapshot plus registration in `on_subscribe`, with
installation acknowledged before attach resolves. Moving registration to a later
task can reopen an event-loss window. This is a limited replay/live boundary,
not exactly-once remote effects. Snapshots include transient output; their existence
does not authorize exporting hidden reasoning or other private content.

The idle-thread router drops event inputs for nonexistent/stopped threads when
store checks succeed. But `is_thread_stopped` defaults false, user text bypasses
these gates, and existence/stopped lookup errors proceed fail-open. Store-backed
lifecycle screening therefore cannot be the sole current-authority enforcement.
The application must define detach, idle, stop, close and revocation separately.

Applied in [client reattachment](tool-and-event-contracts.md#reattach-clients-without-a-replay-to-live-gap),
[operations](../../agent-production-operations/references/event-driven-operations.md),
and the [worked task](event-runtime-worked-example.md).

## S13 — Tool-session and workspace lifetime

[MCP compatibility](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/about/mcp-compatibility.md),
[sandbox server](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-core/src/server.rs),
[Git helper](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-core/src/git.rs),
[Jujutsu helper](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-core/src/jj.rs),
[mode providers](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-local/src/providers.rs),
[child preservation test](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-local/tests/subagent_no_squash.rs),
[stale cleanup test](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-local/tests/stale_workspace_cleanup.rs).

The MCP docs describe a local session-preserving proxy versus fresh connections
per Lambda invocation. Cross-call process memory is not automatically portable.
A handle created by call A and consumed by B is a useful compatibility probe;
it must run against the chosen adapter before a migration claim.

Sandbox cloning maps `base_thread_id` to the parent's bookmark. The shared squash
handler invokes the backend, then removes child metadata on success. Jujutsu's
helper executes squash then bookmark deletion; Git's helper performs a normal
merge then best-effort branch deletion. A tool name is not identical history
semantics. Close-thread returns 200 while cleanup runs in a spawned task and can
log an error later. Upstream tests describe preserving unsquashed child work and
cleaning stale workspaces. Test files were inspected, not executed. Full backend
security, all suspension paths and every conflict case were not assessed.

Applied in [workspace integration](loops-and-coordination.md#integrate-workspace-descendants-explicitly)
and the worked task. Independent source and workspace ancestry, retention before
cleanup, integration conflict disposition and combined verification are our
transferable design requirements, not a claim that all are enforced upstream.

## S14 — Selected literature, beyond abstracts

Reading now covers selected passages in the named sections below, not a full
paper or proof audit. The
previous S9 abstract-only record describes the initial pass. The dissertation
remains background at abstract/contents depth; it adds no needed implementation
prescription to this follow-up.

[Flo v1](https://arxiv.org/html/2411.08274v1), sections 2.1–2.3, 3.1, 3.3,
3.5 and 3.6: finite-window aggregation and incremental output are different
responses to an unbounded input. Its eager-execution property constrains
interleavings; streaming progress rules out waiting for unbounded input to finish.
**Design inference:** identify an operation's finite completion condition separately
from its subscription lifetime. Test event scheduling; do not assume an LLM
continuation has the deterministic operator properties required by Flo.

[Protocol rewrites v2](https://arxiv.org/html/2404.01593v2), sections 2.5,
3.1–3.3 and 4.1–4.2: asynchronous decoupling changes timing; safe transformations
need dependency/order conditions. Partitioning must keep jointly needed facts
together, possibly using functional dependencies. **Design inference:** conversation
keys alone cannot establish independence of shared repository/account effects.
Separate report generation from authoritative integration; define the dependency
and observable outcome before changing placement. The paper's Dedalus semantics
and failure assumptions are not a proof for Infinity or arbitrary agent work.

Applied as design questions in the worked task and event procedure. We did not
reproduce paper experiments, audit all proofs, or locate an Infinity-specific
formal/performance paper in this investigation.
