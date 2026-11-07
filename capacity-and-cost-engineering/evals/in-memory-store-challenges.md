# In-memory store assertion challenges

Added 2026-11-03. Existing cases are unchanged. These are authored assertion-level challenge fragments, not executed tests, real-user responses, model verdicts or independent human labels.

## in-memory-per-node-headroom

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Calculates 38 GiB steady and 50 GiB assumed peak per node from the supplied nonoverlapping components. | The supplied components total 38 GiB steady and 50 GiB peak per node. | The per-node peak is only the 24 GiB value payload. | I will prepare a proposal. |
| Accounts for both copies rather than treating replicas as free memory. | Both copies total 76 GiB steady or 100 GiB if the stated peaks overlap. | Only the primary consumes memory; the replica is free capacity. | I will prepare a proposal. |
| Rejects equating maxmemory with a safe total-RSS or container limit. | Derive maxmemory below the total limit using measured overhead; it does not cap RSS. | Setting maxmemory to 64 GiB guarantees a 64 GiB container cannot OOM. | I will prepare a proposal. |
| Labels the model as assumed and requires load/soak plus persistence/recovery peak evidence. | These are assumptions requiring representative load/soak and recovery-peak measurement. | The arithmetic proves production capacity without running the workload. | I will prepare a proposal. |

## in-memory-cost-durability-boundary

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Calculates node-only cost as $730 per month and $7.30 per million successful useful operations. | Node-only cost is $730/month, or $7.30 per million successful operations. | The complete service TCO is $365/month for both nodes. | I will prepare a proposal. |
| States that storage, network, operations and other omitted costs prevent treating the node-only figure as full TCO. | This excludes storage, network and operations, so it is not full TCO. | The node charge covers every service cost. | I will prepare a proposal. |
| Rejects silently weakening durability to improve cost. | Do not disable AOF without an explicit accepted durability change and evidence. | Disable AOF; durability is unchanged because the store is in RAM. | I will prepare a proposal. |
| Keeps errors and completion evidence visible despite the successful-operation unit denominator. | Report failed attempts and completion rate beside cost per successful operation. | Discard failed attempts so the savings report looks better. | I will prepare a proposal. |

