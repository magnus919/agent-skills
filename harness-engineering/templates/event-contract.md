# Event and hook contract

- Event name/version and durable event versus callback:
- Emission point and relation to action/checkpoint/acknowledgement:
- Run/task/event/correlation/operation IDs:
- Ordering and duplicate delivery semantics:
- Allowed fields and redaction/retention/access:
- Hook criticality: authority gate / acceptance gate / enrichment / telemetry:
- Input/output schema and whether arguments may change:
- Reauthorization requirement after mutation:
- Timeout, failure, cancellation and reentrancy policy:
- Replay behavior and subscriber idempotency:
- Drain/ack/retention/eviction ordering:
- Failure exercise and observed evidence:

Do not erase worker output before the result is durably recorded and the consumer
can recover it. Storage cleanup is distinct from losing the only evidence.
