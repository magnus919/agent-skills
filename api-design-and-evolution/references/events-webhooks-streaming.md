# Events, Webhooks, And Streaming

## Events And AsyncAPI

An event expresses a fact; a command requests an action. Specify producer authority,
event type and schema ownership, channel/topic, retention/replay, compatibility, and
what consumers may infer from absence.

AsyncAPI 3.0.0 `send` and `receive` are from the described application's perspective.
State that perspective before writing operations; do not invert another party's
document mechanically.

CloudEvents 1.0.2 standardizes an envelope, not delivery policy. In CloudEvents,
duplicate identity is the pair `source` + `id`, not `id` alone. Choose structured or
binary mode deliberately and document required attributes, payload schema/version,
extension attributes, and trace propagation.

Timestamps do not create a total order. Define ordering scope, sequence or causal token semantics, and consumer behavior for duplicates, gaps, reordering, poison messages, replay, and schema-version transitions. State delivery guarantees precisely; at-least-once and at-most-once have different producer and consumer obligations. Do not claim end-to-end exactly-once behavior without defining its scope, transaction boundary, failure model, and evidence; many systems still require consumer idempotency or deduplication.

## Webhooks

A webhook is an outbound callback plus a delivery and security contract. Define
subscription authority, allowed destination policy, DNS/IP and redirect handling,
payload envelope, acknowledgement semantics, retry classification, pause/disable and
replay policy, delivery audit visibility, and consumer deduplication.

Never invent an HMAC header format or replay interval. A signature profile must state
the exact bounded raw body, covered components/canonicalization, algorithm, key ID and
rotation, constant-time comparison where applicable, freshness/replay policy, and
failure handling. RFC 9421 and RFC 9530 are optional HTTP integrity/signature building
blocks, not a universal webhook profile. Treat callback URLs as untrusted and route
deep design to `secure-software-engineering`.

## Streams

For SSE, WebSocket, gRPC, or another stream, define handshake/auth renewal, framing,
subscription/filtering, backpressure, checkpoints/resumption, retention, reconnect
behavior, ordering scope, closure/error frames, and how a consumer detects loss.
Streaming does not remove the need for a query or recovery path.
