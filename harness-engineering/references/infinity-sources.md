# Infinity source and claim records

Accessed 2026-11-03. These S1–S9 records describe the initial pass;
[follow-up findings](infinity-design-findings.md) add S10–S14 and deeper selected
paper-section reading. Source pin: `1abc6fcff1f186124f924b56aa92c3a3684c90c5`.
Links under that commit refer to inspected files, not a floating release. Static
inspection is evidence of code structure, not executed behavior. Paraphrases below
preserve distinct reusable claims; they do not copy upstream implementation.

## S1 — Supplied video identity

[Video](https://www.youtube.com/watch?v=os5eNeAVRpc), Let's Get Rusty:
“Amazon built a new AI agent runtime in Rust”, 2026-11-02. YouTube oEmbed confirmed
title/author; watch-page metadata supplied publication date, description and
chapters. The description directly links S2, resolving the Infinity identity.

Description chapters: 0:00 introduction, 0:26 waiting resources, 0:56 asynchronous
tools, 2:07 slices/durable state, 3:08 Rust async analogy, 4:09 messages/synthetic
calls, 5:41 Lambda scale-to-zero. These are publisher navigation metadata, not
transcript observations. Auto-caption metadata existed; the caption request
returned zero bytes. No full transcript, speech verification, visual inspection,
or claim of complete video coverage. Source-level technical conclusions use S2–S8.

## S2 — Author announcement and benchmark report

[AWS announcement](https://aws.amazon.com/blogs/opensource/introducing-infinity-a-runtime-for-extreme-agent-concurrency/),
Shadaj Laddad, 2026-10-23. Primary author explanation; not independent testing.
The author frames tool boundaries as suspension points. Conversation persistence
releases waiting runtime compute, and callbacks re-enter through an input queue.
The announcement identifies the Apache 2.0 release and describes synthetic events,
thread communication, and serverless hosting. Its unanswered research questions
include model behavior under interleaving, scheduling, conversation-tree
compaction, and event authenticity.

Reported measurement: 80,000 agents, twenty turns each, two completions per turn,
3.2 million simulated completions, approximately 1.2 KB streamed completion,
in-memory stores, single AMD EPYC 9R14 thread, approximately 100 KB/idle agent.
The Raspberry Pi figure is a projection to an 8 GB capacity, not that experiment's
hardware. Treat this as an author-reported resident-memory result, not a quality
or throughput comparison against other harnesses. Preserve tool-server, storage,
queue, and model costs when estimating system cost; no runtime compute during a
wait does not make the whole service free.

## S3 — Public source identity and layer boundaries

[README](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/README.md), [license](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/LICENSE.txt),
[workspace](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/Cargo.toml). Public repository with Apache 2.0 license.
Core runtime, Lambda embedding, daemon/CLI, sandbox packages, provider protocol,
MCP bridge, RAP client and protocol are separate workspace components. Runtime
scheduling, tool transport, model adapters and user interface can evolve
separately. Existence of an adapter does not establish its tested operational
limits or security properties.

## S4 — Execution, ordering and durability

[Architecture](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/architecture.md),
[HistoryManager and event processor](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/event_processor.rs),
[thread step](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/thread.rs),
[local router](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/local/router.rs),
[local driver](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/local/driver.rs).

- `HistoryManager::new_with_history` restores ancestor-aware history and processed
  IDs. The continuation needs runtime metadata and configuration references as
  well as model-visible text. Reconstruct external resources separately.
- `handle_content` matches normal tool results to unanswered calls, ignores
  already answered results and rejects unmatched results. Stable message IDs
  suppress known repeats. This is correlation/dedup, not authentication.
- A turn buffer separates in-flight output from persisted messages. The step
  calls `history.sync()` before asynchronous dispatch. This establishes a
  commit-before-dispatch barrier for that path, not a transaction with the tool.
- Synchronous tools and unknown-tool errors loop back within completion
  processing. A slice can contain more than one model completion. Bound such
  loops explicitly when designing a serverless runtime.
- The router owns `FuturesUnordered` drivers and per-thread channels; idle drivers
  can exit and be recreated. The implementation is more specific than the
  common “task per agent” shorthand; a thread here is a conversation identity.
- Serialization is per conversation. It does not serialize different threads'
  writes to the same repository, account or other external resource.

**Important atomicity limit:** `HistoryManager::sync` appends history before
adding user/subscription message IDs through a separate `StateStore` operation;
the latter result is discarded with `let _ =`. The
[Lambda state store](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-lambda/src/state_store.rs)
uses DynamoDB, while
[conversation history](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-lambda/src/conversation_history.rs)
uses DSQL. No cross-store/tool atomic commit was established by this review.
Crash after append but before dedup persistence, crash after commit before dispatch,
and crash after a tool effect before callback require fault injection and
reconciliation. We did not reproduce a duplicate effect or claim a proved defect.

## S5 — Event presentation, deferral and compaction

[Subscription specification](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/spec/server/subscription-events.md),
[threading](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/built-in/threading.md),
[deferral implementations](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/defer.rs),
[stores](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/stores.rs), and S4.

A subscription's original call has already been answered. A later event gets a
new synthetic assistant-call/result pair tied to the original invocation;
`receive_event__injected` is reserved and direct model attempts must be rejected.
Tool results use `id`; subscription events use `tool_call_id`. Neither a synthetic
assistant role nor a valid originating ID makes payload instructions authoritative.

Default subscription handling spawns a child inheriting history to a settled
spawn point, processes the event, then reports or closes silently. This is not an
empty context by default. Explicit `fresh_context: true` is a different choice;
child instructions then need sufficient standalone task data. “Associative” is a
protocol flag for inline delivery, not a proof that payloads commute algebraically.
Inline delivery is useful for related command output, but increases parent context.

The current local runtime can defer child reports, parent messages and subscription
events during active tool waits to avoid settling the call as interrupted. Its
`InMemoryDeferQueue` loses held events on process death. `NoDeferral` processes
events immediately and accepts interruption semantics; a transport-backed adapter
could make a different choice. The inspected Lambda handler passes `NoDeferral`
(see S7). Thus documentation about event responsiveness is
not a portable latency or durability guarantee. At the lower processing layer a
new nonmatching input can settle a pending call as interrupted, and a late result
can be stale. Interruption does not establish that the tool stopped.

Compaction stores a summary with an absolute history position; reconstruction
must respect child spawn boundaries and explicit fresh-context boundaries. Source
contains tests for repeated compaction and compaction during tool calls. A correct
position calculation cannot establish that a model summary preserved constraints.

## S6 — RAP's asynchronous boundary and adapter limits

[Invocation](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/spec/basic/tool-invocation.md),
[result](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/spec/basic/tool-result.md),
[transport](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/spec/basic/transport.md),
[cancellation](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/spec/basic/tool-cancellation.md),
[spec overview](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/rap/spec/overview.md),
[shared RAP dispatch](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/tools/rap_tool.rs).

RAP sends an HTTP invocation carrying operation/arguments, call ID, group/thread,
callback and optional user/ancestor information. HTTP acknowledgement confirms
acceptance only; the eventual result arrives at the callback. Subscriptions retain
callback and originating-call information across waits. Auth and tenant binding
must be enforced externally; self-asserted `user_id` and ancestry cannot confer
permission. Callback authentication is implementation-specific in the spec.

Normative transport guidance recommends exponential backoff for unreachable/5xx
endpoints and no retry for 4xx. The inspected shared `invoke_rap_tool` makes one
POST; transport errors propagate, and non-2xx statuses become error tool results.
It accepts the 2xx range whereas the spec describes HTTP 200. Do not infer that
all recommended retry behavior is implemented by this function. Inspect the chosen
transport and embedding before assigning delivery guarantees.

Cancellation is advisory, may race with completion, has no retry/delivery/order
guarantee, and cannot certify rollback. A callback after cancellation needs a
stale-result and external-effect reconciliation policy. The protocol defines no
universal tool execution timeout; the application must bound pending work.

[MCP bridge](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-mcp-bridge/src/lib.rs) supports lazily connected
stdio/Streamable HTTP sessions. Compatibility preserves access to existing tools;
it does not establish that every legacy MCP server becomes stateless or that its
processes and connections disappear while a core agent yields.

## S7 — Serverless composition

[AWS architecture](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/docs/docs/infinity-runtime/serverless/architecture.mdx),
[Lambda handler](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-lambda/src/event_handler.rs), S4.
SQS FIFO groups serialize threads, Lambda drives slices, Bedrock provides model
calls, DSQL stores conversations, and a RAP receiver places callback messages back
on the queue. StateStore is a distinct DynamoDB component in source. Short timers
use delayed SQS delivery; longer ones use EventBridge schedules. Receiver supports
several callback kinds; view updates are acknowledged/dropped on this embedding.

A platform queue can provide a thread's single-writer guarantee only within its
configured delivery/visibility/timeout contract. Hibernation still depends on
persistent storage, queue retention, callback routing, timers, permissions and tool
servers. No cloud infrastructure was deployed, no account credentials used, and
no platform reliability or billing measurement was made here.

## S8 — Benchmark and executable upstream challenges

[Scale example](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/examples/agent_scale.rs)
implements a scripted provider and synthetic async tool against real queue/stream
paths, using in-memory stores and idle wave RSS sampling. Defaults are 10,000
agents, twenty turns, wave size 500; the reported 80,000-run settings must be set
explicitly. RSS reads `/proc/self/status`, making this measurement Linux-specific.
The example does not invoke the shell command embedded in its mock tool arguments.

[Core tests](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/tests.rs) include
`subscription_event_deferred_during_async_tool_wait`,
`stale_result_does_not_flush_deferred_events_during_async_tool_wait`, and
compaction/reboot recovery challenges. Event processor tests include duplicate,
unmatched, interruption, inline subscription, sync-loop and oversized-input paths.
These were inspected, not executed. They inform local drill design; their existence
alone supplies no pass receipt or distributed fault-tolerance proof.

## S9 — Literature, with scope boundaries

[Hydro research index](https://hydro.run/research/) was searched alongside targeted
web queries for Infinity/Hydro/Laddad papers. No Infinity-specific paper was located
in that bounded search. This is an absence-of-found-evidence statement dated above,
not proof that no paper exists.

- [Flo: a Semantic Foundation for Progressive Stream Processing](https://arxiv.org/abs/2411.08274),
  Laddad et al.; listed as POPL 2025 by Hydro. Read abstract and bibliographic
  record. Bounded/unbounded stream distinctions and progress semantics help ask
  whether waiting for completion of an endless subscription can terminate. This
  is a design analogy, not proof of Infinity behavior or model determinism.
- [Optimizing Distributed Protocols with Query Rewrites](https://arxiv.org/abs/2404.01593),
  Chu et al., SIGMOD 2024 technical report, v2. Read abstract and bibliographic
  record. Partitioning/decoupling have semantic preconditions: separate thread
  queues do not remove shared external-resource dependencies. This implication
  is our engineering synthesis, not the paper's evaluation of an agent runtime.
- [Programming Models for Correct and Modular Distributed Systems](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-85.pdf),
  Laddad, Berkeley dissertation, 2025-05-16. Read abstract and contents only.
  Provides provenance for Hydro's stream/type/staging research; it was not
  exhaustively reviewed and is not an Infinity performance report.
