# In-memory store assertion challenges

Added 2026-11-03. Existing case IDs and assertions are unchanged. These are authored rubric challenge fragments, not generated model outputs, executed tests, human adjudication or release evidence. Each row isolates an assertion. The omission response is intentionally non-evidential.

## valkey-vector-feature-matrix

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Preserves the stated Valkey/BSD preference while requiring technical qualification. | Keep Valkey as the preferred candidate, subject to the required compatibility evidence. | Disregard the BSD preference because Redis offers AGPL. | I will prepare a proposal. |
| Rejects assuming complete RediSearch or full-text parity from Valkey-search vector API compatibility. | A compatible subset of vector APIs does not establish all full-text operators. | The module name guarantees every Redis Query Engine operator works. | I will prepare a proposal. |
| Requires dimension, metric, filter and query-quality checks beyond latency. | Compare dimensions, distance metric, filter semantics and recall against an exact reference. | The fastest top-k response alone proves equivalent query quality. | I will prepare a proposal. |
| Requires update/delete freshness and index rebuild or recovery evidence. | Verify deletion/update visibility and rebuilding from authoritative data after failure. | A successful first query proves future freshness and recoverability. | I will prepare a proposal. |

## stream-checkpoint-trimmed-pending

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Identifies the sink-commit-before-ACK duplicate-delivery window. | Redelivery can repeat the already committed warehouse effect. | The crash proves the warehouse write could not have happened. | I will prepare a proposal. |
| Rejects reading only new messages as recovery of another consumer's pending work. | New-only reads do not recover the abandoned pending work. | Starting a new consumer on new messages completes pending recovery. | I will prepare a proposal. |
| Treats trimmed required payloads as a replay gap needing authoritative repair or explicit incompleteness. | Repair missing payloads from the authority or report replay coverage incomplete. | Pending IDs guarantee payloads remain available after trimming. | I will prepare a proposal. |
| Requires source-to-sink reconciliation before declaring completion. | Reconcile stable event/entity IDs and sink effects before marking the backfill complete. | Equal aggregate row counts alone prove every event was processed correctly. | I will prepare a proposal. |

