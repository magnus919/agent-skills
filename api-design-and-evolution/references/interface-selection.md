# Interface Selection

Choose the smallest interface that preserves the consumer job and domain semantics.
An API may use more than one style; record why each boundary exists.

| Style | Fits when | Design focus | Compatibility surface |
|---|---|---|---|
| REST/HTTP | Resource-oriented reads and broadly interoperable request/response | HTTP semantics, representations, cache and conditional behavior | Methods, media types, fields, defaults, status/error behavior |
| GraphQL | Consumers need shaped traversals across a governed graph | Schema ownership, query cost, nullability, resolver authority | Types, fields, arguments, enums/unions, query cost and generated clients |
| RPC | A named domain command is clearer than resource state transfer | Command intent, input/output schema, deadlines and side effects | Operation names, request/response fields, error model and client stubs |
| Event/message | Facts must reach independent consumers asynchronously | Event ownership, delivery and replay semantics | Topic/channel, envelope, schema, delivery and ordering guarantees |
| Webhook | A provider must notify a consumer over HTTP | Subscription, callback safety, verification and delivery contract | Registration, payload, signature profile, retries and disablement behavior |
| Streaming | Consumers need an ongoing sequence or bidirectional session | Session lifecycle, flow control, resume and ordering scope | Framing, cursors/checkpoints, backpressure, reconnect and retention behavior |

Ask before choosing:

- Who initiates interaction, and who owns the authoritative state or schema?
- Is the consumer querying current state, issuing a command, receiving a fact, or
  maintaining a live view?
- What failures are tolerable: delay, duplicate, loss, reordering, or partial work?
- Which client types, networks, generated tools, intermediaries, and caching layers
  participate?
- What must evolve independently, and what contract must remain stable?

Do not select GraphQL only to avoid endpoint design, events only for "real time," or
URL versions only because a semantic change is difficult. A style decision is a local
trade-off, not an organization-wide rule unless it belongs in an ADR.
