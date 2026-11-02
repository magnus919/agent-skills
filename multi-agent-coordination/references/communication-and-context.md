# Communication and distributed context

## Build a message contract

Separate notification, observation, assignment, proposal, decision, authorization,
cancellation and artifact delivery. A human message may contain several intents;
classify each before changing work. Status queries must not replan silently.
Use stable message/transfer ID, task ID, sender principal/run, recipient role,
causal parent, requirement revision, expiry, payload or access-controlled artifact
ref, and required acknowledgement. Preserve sent, received, adopted, executed
and accepted as separate observations.

Prefer directed messages and pull-based artifact retrieval over full transcript
broadcast. Share necessary facts and uncertainty, not persuasive private reasoning.
A recipient needs enough evidence to challenge the conclusion. Preserve missing,
denied, stale and conflicting source states. A summary that drops the decisive
constraint is a failed handoff even if its text is fluent.

Define duplicate, late, reordered and unavailable-recipient behavior. Deduplicate
by durable operation identity, not similar wording. Retain causal parent IDs and
source revisions; cross-machine wall clocks alone do not establish causal order.
[Lamport's event-ordering work](https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/)
provides the foundation; the envelope above is our engineering synthesis.

## Decision placement

Before asking an approver, assemble: proposed action, exact target, current scope,
local facts, governing intent, options, uncertainty, side effects, reversibility
and authority source. Use the decision-packet template. Domain expertise and
formal permission are distinct requirements: neither substitutes for the other.
If either is missing, obtain the missing evidence/authorized owner instead of
shopping for a peer that says yes. A deadline cannot grant rights.

## Intent reconstruction after compaction or drift

Follow the authoritative chain from current task to parent outcome to project
purpose. Load each accepted version and explicit exclusions; identify the next
action's contribution and any scope/authority change. Keep the packet bounded by
including source pointers and only decision-relevant facts. Compare with the
current assignment, not a remembered slogan. A higher-level purpose cannot
override narrower accepted scope: being a good dog owner does not authorize
building every potentially useful structure.

Repeat at handover, material change, failed assumption or observed drift. A fixed
periodic reminder is optional and must be evaluated for noise/cost. Verify the
worker used the updated constraint with a decision or artifact test; delivery
alone is insufficient. If the host cannot interrupt safely, checkpoint and
replace under current authority rather than claiming live adoption.

## Protocol is not coordination policy

[A2A](https://a2a-protocol.org/latest/specification/) provides interoperability
concepts including task lifecycle, messages and artifacts. Record negotiated
version and supported transport/auth/cancel behavior when using it. MCP exposes
tools; ACP connects clients and agents; neither name proves shared task ownership
or a team's acceptance semantics. Signed messages authenticate an origin under a
key model; they do not establish correctness, authorization or community scope.

OpenRig's [context documentation](https://openrig.dev/docs/context) explicitly
separates served context from consumption and automatic synchronization. Preserve
that distinction in any vendor-neutral adapter.
