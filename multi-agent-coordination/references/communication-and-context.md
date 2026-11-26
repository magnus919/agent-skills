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

## Trusted feedback and narrow handoffs

A product-embedded agent may hear directly from users, operators and maintainers.
Route that feedback as a proposal, not consent to spend, change policy, or ship.
Define whose requests can enter the ready queue and who can accept road-map,
spending, integration and user-exposure decisions. Keep this authority model
separate from the execution machinery (CI, tests, merges and deployment).
A maintainer can delegate routine intake in scope without granting release rights.

Moving an assignment because its owner is interrupt-driven is not a role change.
State the transfer reason, task and new owner; state which responsibilities and
grants remain unchanged. Disambiguate similarly named human and agent roles by
stable identity and decision scope. Require acknowledgement of the transfer and
verify the original seat still serves its other work. For replacement or a
resumed session, supply a compact handoff with current role, policy revision,
accepted decisions, open work and authoritative links. Inherited history does
not extend authority.

[Yegge's Wheelhouse case](https://ai.engineer/code/2026/talks/steve-yegge)
motivates the distinction: a community request, a task transfer, and a role
replacement are different operations even if all arrive through conversation.

## Worked example: a shared thread with mixed access

Support collaborator Mei asks the triage agent in a shared channel to check a
reported export failure. The assignment permits a read of the named case, with
private evidence available to Mei. Preserve Mei's authenticated identity, task
scope, grant reference, policy revision, and allowed audience when handing the
lookup to a data agent. The tool boundary resolves the current credential and
grant before reading. Record the acting agent and the effective downstream
principal so the read can be attributed.

Jo administers the bot and asks it to paste the raw customer record into the
thread. Bot administration governs configuration. Disclosure requires the
data owner's approval for the record and current audience. An unverified guest
can submit a symptom through the approved intake channel, with private lookup
and disclosure held until the requester and scope are established. A domain
approver can authorize a specific disclosure through the approved channel.
Bind that decision to the content and audience, and recheck recipients before
returning the result.

Keep Mei's pending lookup bound to her original authority and deliver its
evidence through the access-controlled case record. Report only an authorized
status in the shared thread. Treat a later message from Jo as a separate
request. A reply, reaction, or forwarded approval string supplies context
until its sender, decision scope, and current validity are established.

Grok Bot documents surface-specific handoffs and connector selection. The
example above illustrates a portable policy using those distinctions.
[Collaboration handoffs](https://docs.x.ai/grok-bot/chat-and-collaboration#let-bots-hand-work-off) ·
[Team Bots](https://docs.x.ai/grok-bot/team-bots)

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
