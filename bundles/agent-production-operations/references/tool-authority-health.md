# Tool and Authority Health Record

Captures tool availability, tool failure, and authority usage/breach state over
time for an agent operating under a
[production contract](agent-production-contract.md) and
[runtime control plan](runtime-control-plan.md).

## Record schema

### Header fields (set once per agent instance)

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier from the production contract |
| `record_start` | ISO 8601 timestamp | When this health record began |
| `record_end` | ISO 8601 timestamp or null | When this health record ended (null if active) |
| `observation_window` | string | Granularity of observations: `1m`, `5m`, `15m`, `1h` |

### Per-tool health fields (one block per registered tool per observation window)

| Field | Type | Description |
|---|---|---|
| `tool_id` | string | Tool identifier from the production contract |
| `tool_version` | string | Tool version in use |
| `window_start` | ISO 8601 timestamp | Start of this observation window |
| `window_end` | ISO 8601 timestamp | End of this observation window |
| `total_calls` | integer | Total tool invocations in the window |
| `successful_calls` | integer | Tool invocations that returned success |
| `failed_calls` | integer | Tool invocations that returned an error |
| `failure_rate` | float | `failed_calls / total_calls` (0.0–1.0) |
| `failure_modes` | map[string, integer] | Counts per failure type (e.g., `timeout: 3`, `auth_error: 1`, `5xx: 2`) |
| `avg_latency_ms` | float | Average tool response latency in milliseconds |
| `p95_latency_ms` | float | 95th percentile latency in milliseconds |
| `health_status` | enum | `healthy` (failure_rate < 1%), `degraded` (1–5%), `unhealthy` (> 5%) |
| `health_check_passes` | integer | Health-check endpoint successes in the window |
| `health_check_failures` | integer | Health-check endpoint failures in the window |

### Authority usage fields (per observation window)

| Field | Type | Description |
|---|---|---|
| `authority_profile` | string | Active authority profile from the production contract |
| `total_actions` | integer | Total actions attempted by the agent in the window |
| `permitted_actions` | integer | Actions that passed the authority gate |
| `blocked_actions` | integer | Actions blocked by the authority gate (NOT breaches — correctly blocked) |
| `authority_breaches` | integer | Attempted actions outside the permitted scope (breaches) |
| `breach_details` | array of objects | Per-breach: `{timestamp, action, target, reason_blocked}` |
| `side_effects_total` | integer | Total side effects produced in the window |
| `side_effects_audited` | integer | Side effects with complete before/after audit trail |
| `side_effects_unexpected` | integer | Side effects whose result diverged from the expected outcome |
| `escalation_count` | integer | Number of escalations triggered in the window |
| `escalation_reasons` | map[string, integer] | Counts per escalation trigger type |

### Cost fields (per observation window)

| Field | Type | Description |
|---|---|---|
| `cost_total` | float | Total cost accrued in the window (USD) |
| `cost_model` | float | Cost attributed to model inference |
| `cost_tools` | float | Cost attributed to tool calls |
| `cost_budget_remaining` | float | Remaining budget for the billing period |
| `cost_budget_pct_consumed` | float | Percentage of budget consumed (0.0–100.0+) |
| `cost_breach` | boolean | Whether cost exceeded the budget in this window |

### Latency fields (per observation window)

| Field | Type | Description |
|---|---|---|
| `p50_latency_ms` | float | 50th percentile end-to-end latency |
| `p95_latency_ms` | float | 95th percentile end-to-end latency |
| `p99_latency_ms` | float | 99th percentile end-to-end latency |
| `latency_baseline_ms` | float | Baseline p50 from the production contract |
| `latency_breach` | boolean | Whether latency exceeded any threshold this window |
| `latency_breach_detail` | string | Which threshold was breached and by how much |

## Health state transitions

The record tracks cumulative state transitions over the agent's lifetime:

| State | Definition | Transition trigger |
|---|---|---|
| `healthy` | All tools healthy; 0 authority breaches; cost within budget; latency within baseline | Default starting state |
| `degraded-tool` | One or more tools unhealthy or degraded; authority still in effect for healthy tools | Tool failure_rate > 1% for any tool |
| `degraded-authority` | Authority reduced (fallback triggered); agent operating in reduced mode | Fallback trigger per the runtime control plan |
| `escalated` | Human escalation active; agent awaiting disposition | Escalation trigger per the production contract |
| `disabled` | Agent fully disabled; no authority of any kind | Disablement trigger per SKILL.md operational parameters |

## Record retention

- Active records: retained for the lifetime of the agent instance.
- Closed records: retained for 90 days after agent retirement.
- Breach records: retained for 1 year (compliance/audit).
- Record location: appended to the agent's operational log; summarized in
  production-readiness review inputs.

## Integration with trace-to-eval feedback

Authority breach details and tool failure patterns from this record are sampled
into the [trace-to-eval feedback pipeline](trace-to-eval-feedback.md). Breaches
that reveal an eval gap (the eval suite did not catch a behavior that led to a
breach) generate new eval cases. Tool failures that follow a pattern (e.g.,
timeout spikes after deploy) feed release-gate updates.
