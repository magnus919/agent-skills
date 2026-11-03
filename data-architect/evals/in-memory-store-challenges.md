# In-memory store assertion challenges

Added 2026-11-03. Existing case IDs and assertions are unchanged. These are authored rubric challenge fragments, not generated model outputs, executed tests, human adjudication or release evidence. Each row isolates an assertion. The omission response is intentionally non-evidential.

## valkey-open-source-preference

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Recommends Valkey for the supplied permissive-license and community-governance preference. | For your stated BSD and community-governance priorities, start with Valkey. | AGPL exists now, so select Redis and disregard the BSD preference. | I will prepare a proposal. |
| States that Redis 8 offers an AGPLv3 option while distinguishing it from permissive BSD licensing. | Redis 8 offers AGPLv3; that copyleft option differs from Valkey's permissive BSD license. | All current Redis releases are proprietary with no open-source license option. | I will prepare a proposal. |
| Treats continuing vendor-trust concerns as a distinct selection factor after the AGPL addition. | The new license option does not by itself restore the trust affected by relicensing. | Adding an OSI-approved license necessarily resolves every governance and trust concern. | I will prepare a proposal. |
| Avoids inferring a business-community preference from the supplied open-source preference. | This recommendation reflects your open-source priorities, not business-user sentiment. | The business community therefore prefers Valkey too. | I will prepare a proposal. |

## in-memory-zero-loss-primary

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Identifies the fsync-policy loss exposure rather than equating AOF configuration with zero loss. | Every-second AOF leaves loss exposure; enabling AOF does not prove the ledger requirement. | AOF enabled means no acknowledged write can ever be lost. | I will prepare a proposal. |
| Identifies asynchronous failover as a separate acknowledged-write loss risk. | A promoted asynchronous replica may lack an acknowledged write. | Automatic failover eliminates acknowledged-write loss. | I will prepare a proposal. |
| Requires representative failure and invariant evidence before accepting the zero-loss requirement. | Require independently recorded accepted writes and representative failure/invariant checks before acceptance. | Approve the ledger solely from the configuration screenshot. | I will prepare a proposal. |

## redis-newer-files-valkey-migration

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Rejects assuming Redis 7.4 data files can be loaded directly into Valkey. | The documented Redis 7.4 file incompatibility rules out treating an RDB copy as a proven route. | Copy the Redis 7.4 RDB directly; RESP proves file compatibility. | I will prepare a proposal. |
| Requires checking JSON/search features against the exact candidate versions. | Inventory JSON and search operators against the chosen engine/module versions. | All Redis search and JSON features are automatically identical in Valkey. | I will prepare a proposal. |
| Requires reconciliation and a rollback plan that accounts for target-side writes. | Define reconciliation and how target writes are preserved or replayed if cutover is reversed. | Rollback means switching the hostname back even after accepting target writes. | I will prepare a proposal. |

