# Agent Production Contract

Defines the contract between an agent and its production operating environment.
Every agent promoted to production MUST have a completed production contract.
The contract is reviewed at each production-readiness cycle and updated when
model, prompt, tools, or authority surface change.

## Contract fields

### 1. Identity

| Field | Description | Required |
|---|---|---|
| `agent_id` | Unique identifier for the agent instance | Yes |
| `agent_name` | Human-readable name | Yes |
| `agent_version` | Semantic version of the agent (model + prompt + tools + policy) | Yes |
| `owner_team` | Team accountable for the agent in production | Yes |
| `escalation_channel` | Channel or contact for human escalation | Yes |

### 2. Capability contract

Defines **what** the agent can do, independent of whether it is permitted to do
it (authority gates that separately).

| Field | Description | Required |
|---|---|---|
| `capability_class` | `read-only`, `side-effect-internal`, `side-effect-customer` | Yes |
| `domain` | Problem domain the agent operates in (e.g., "CI triage", "customer support") | Yes |
| `user_population` | Who the agent serves: `internal-developers`, `internal-support`, `customers`, `public` | Yes |
| `max_concurrent_sessions` | Maximum concurrent agent sessions | Yes |
| `supported_languages` | Languages the agent handles | No |
| `model_list` | Models the agent may use, with min/fallback designation | Yes |
| `prompt_version` | The prompt version identifier in use | Yes |
| `tool_list` | Tools registered to the agent, each with a tool ID and version | Yes |
| `evaluator_list` | Evaluators applied to the agent's outputs, each with version | Yes |

### 3. Authority contract

Defines **what the agent is permitted to do**. Authority is scoped by target,
operation, and user context.

| Field | Description | Required |
|---|---|---|
| `authority_profile` | `read-only`, `read-write-internal`, `read-write-customer-gated` | Yes |
| `permitted_actions` | List of `(operation, target_resource, condition)` triples | Yes |
| `user_data_access` | `none`, `anonymized-only`, `pii-read-only`, `pii-read-write` | Yes |
| `max_cost_per_request` | Hard ceiling on cost per individual request (USD) | Yes |
| `rate_limit` | Maximum requests per second/minute | Yes |
| `side_effect_approval` | `none` (no side effects), `log-only` (record but allow), `gate` (require human approval per side effect), `auto` (autonomous within budget) | Yes |
| `authority_review_cadence` | How often authority is reviewed (e.g., "every 30 days", "per release") | Yes |

### 4. Uncertainty contract

Defines **how the agent handles low-confidence situations**.

| Field | Description | Required |
|---|---|---|
| `confidence_threshold` | Minimum confidence score below which the agent must escalate or degrade (0.0–1.0) | Yes |
| `uncertainty_action` | What the agent does at threshold: `escalate`, `degrade-to-read-only`, `ask-user`, `log-and-proceed` (only for read-only profile) | Yes |
| `uncertainty_signal` | How uncertainty is measured: `model-logprob`, `classifier-score`, `heuristic` | Yes |
| `ambiguous_input_policy` | Behavior when the user request is ambiguous: `clarify`, `best-effort-with-disclaimer`, `escalate` | Yes |

### 5. Escalation contract

Defines **when and how the agent hands off to a human**.

| Field | Description | Required |
|---|---|---|
| `escalation_triggers` | Ordered list of `(trigger_type, threshold, action)` triples | Yes |
| `escalation_channel` | Where the escalation notification is sent (Slack channel, PagerDuty, Jira) | Yes |
| `escalation_response_sla` | Maximum time before a human must acknowledge the escalation | Yes |
| `escalation_context_payload` | What state is included in the escalation: `full-trace`, `summary-only`, `redacted-trace` | Yes |
| `auto_resume_policy` | Whether the agent can auto-resume after escalation: `never`, `after-ack`, `after-resolution` | Yes |

### 6. Side-effect contract

Defines **the side effects the agent can produce and how they are managed**.

| Field | Description | Required |
|---|---|---|
| `side_effect_types` | Types: `database-write`, `api-mutation`, `notification-send`, `file-create`, `file-modify`, `file-delete`, `credential-use` | Yes |
| `reversibility` | Per side-effect type: `reversible` (rollback exists), `compensatable` (can be undone via compensating action), `irreversible` (cannot be undone) | Yes |
| `side_effect_audit` | Whether every side effect is logged with before/after state | Yes |
| `max_side_effects_per_session` | Hard limit on side effects per user session | Yes |
| `side_effect_rate_limit` | Maximum side effects per minute | Yes |

## Production-readiness input

Every production contract MUST reference the most recent production-readiness
review outcome for the agent (or the agent's host service, if the agent is
embedded). The readiness outcome gates authority expansion:

| Readiness outcome | Authority allowed |
|---|---|
| `go` | Full authority per the authority contract |
| `go-with-conditions` | Authority restricted to the conditions; any condition not met = escalation trigger |
| `defer` | Read-only authority only; side-effect authority suspended until re-review |
| `no-go` | Agent disabled; no authority of any kind |
| `exception` | Authority per the exception grant, with an expiration date |

The production-readiness review is owned by
[production-readiness](../../production-readiness/SKILL.md). This contract
records the outcome and the review date; it does not perform the review.

## Incident-learning input

Every production contract MUST reference any open incident-learning records
attributed to the agent. Incident records gate authority and escalation:

| Incident state | Effect on contract |
|---|---|
| `open`, severity-1 or severity-2, agent-attributed | Agent disabled until verified closure |
| `open`, severity-3 or below, agent-attributed | Authority reduced to read-only; escalation threshold lowered (confidence threshold raised by 0.1) |
| `closed-verified`, root cause fixed | Authority restored per readiness outcome; incident record linked in trace-to-eval feedback |
| `closed-verified`, root cause accepted as residual risk | Authority restored with documented residual risk; escalation threshold unchanged |

Incident-learning records are owned by
[incident-learning](../../incident-learning/SKILL.md). This contract consumes
the verified-closure status and follow-up work map; it does not perform
incident analysis.

## Contract lifecycle

1. **Draft**: created when an agent is first proposed for production. Authority
   is `read-only` maximum.
2. **Reviewed**: reviewed alongside a production-readiness review. Authority may
   be expanded per readiness outcome.
3. **Active**: the agent operates under this contract. Tool-authority-health
   records accumulate.
4. **Suspended**: authority reduced or disabled due to incident, breach, or
   readiness deferral.
5. **Retired**: agent decommissioned. Contract archived with trace-to-eval
   feedback summary.
