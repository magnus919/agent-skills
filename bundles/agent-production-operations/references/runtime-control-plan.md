# Runtime Control Plan

Defines the versioning, rollout, and fallback strategy for an agent operating
under the [agent-production-contract.md](agent-production-contract.md).

## 1. Versioning

All five dimensions of an agent are independently versioned and recorded in the
production contract.

### 1.1 Model versioning

| Field | Description |
|---|---|
| `model_id` | Unique model identifier (provider + model name + version hash) |
| `model_version` | Provider-assigned version or deployment timestamp |
| `model_fallback` | Fallback model to use if the primary model is unavailable |
| `model_capability_baseline` | Reference eval scores against the current eval suite |
| `model_regression_threshold` | Maximum acceptable score drop before the model version is blocked (e.g., "no more than 5% drop on any eval case") |

**Change procedure**: a new model version must pass the full eval suite before
it can be referenced in a production contract. Model regression in production
(observed via trace-to-eval feedback) triggers an automatic eval re-run. If
regression exceeds the threshold, the runtime falls back to the previous model
version.

### 1.2 Prompt versioning

| Field | Description |
|---|---|
| `prompt_id` | Unique prompt identifier (hash of prompt template + system message) |
| `prompt_version` | Monotonically increasing version number |
| `prompt_change_summary` | Human-readable description of the change |
| `prompt_eval_baseline` | Reference eval scores for this prompt version |

**Change procedure**: prompt changes must be evaluated against the eval suite.
A prompt-only change that does not alter the tool surface or authority may use
a reduced eval subset. Prompt regression triggers fallback to the previous
prompt version (not model fallback, unless both regress).

### 1.3 Tool versioning

| Field | Description |
|---|---|
| `tool_id` | Unique tool identifier |
| `tool_version` | Semantic version of the tool implementation |
| `tool_api_version` | API version the tool exposes to the agent |
| `tool_health_check` | Endpoint or command that verifies the tool is operational |
| `tool_deprecation_date` | Date after which the tool version is unsupported |

**Change procedure**: a new tool or tool version must be registered in the
production contract with its health check and authority scope. Tools that
change their side-effect surface (new mutation capability) require a
production-readiness re-review. Tool version rollback is immediate if the new
version fails its health check.

### 1.4 Policy versioning

| Field | Description |
|---|---|
| `policy_id` | Unique policy identifier |
| `policy_version` | Monotonically increasing version number |
| `policy_rules` | The set of rules governing agent behavior (authority, escalation, cost, privacy) |
| `policy_change_log` | Ordered list of policy changes with dates and rationales |

**Change procedure**: policy changes that expand authority MUST be gated by a
production-readiness review. Policy changes that restrict authority (tightening
thresholds, adding constraints) may be applied immediately but must be recorded
in the tool-authority-health record.

### 1.5 Evaluator versioning

| Field | Description |
|---|---|
| `evaluator_id` | Unique evaluator identifier |
| `evaluator_version` | Semantic version of the evaluator |
| `evaluator_suite` | The set of eval cases this evaluator runs |
| `evaluator_gate` | Whether this evaluator is a release gate (`blocking` or `advisory`) |

**Change procedure**: evaluator changes that add or modify eval cases must be
reviewed for case quality. A blocking evaluator must pass before any
corresponding agent version can be promoted to production. Evaluator regression
(an evaluator that incorrectly passes or fails) is treated as a production
incident and routed through incident-learning.

## 2. Staged rollout

Rollout proceeds through four stages. Authority expands at each stage only when
the stage's exit criteria are satisfied.

### Stage 1 — Shadow / dry-run (0% traffic, read-only)

| Parameter | Value |
|---|---|
| Traffic | 0% of production traffic; replay of logged production requests |
| Authority | Read-only; side effects logged but not executed |
| Duration | Minimum 24 hours or until 1,000 requests processed, whichever is longer |
| Monitoring | Model latency, prompt compliance, uncertainty distribution |
| Exit criteria | p95 latency within 2x baseline; no authority breach attempts; uncertainty distribution within expected range |

### Stage 2 — Canary (1–5% traffic, read-only with logged side effects)

| Parameter | Value |
|---|---|
| Traffic | 1% of production, ramping to 5% over the observation window |
| Authority | Read-only in production; side effects logged but not executed (dual-write comparison against existing system output) |
| Duration | Minimum 48 hours |
| Monitoring | All stage-1 metrics plus: cost-per-request, dual-write divergence rate, user-satisfaction-equivalent signal |
| Exit criteria | Cost-per-request within budget; dual-write divergence < 2%; no escalation events |

### Stage 3 — Limited production (5–25% traffic, side-effect-gated)

| Parameter | Value |
|---|---|
| Traffic | 5% ramping to 25% in 5% increments each 24 hours |
| Authority | Side-effect-capable per the authority contract, with `side_effect_approval: gate` (human approval required per side-effect class until proven safe) |
| Duration | Minimum 72 hours; each increment gates on the previous increment's exit criteria |
| Monitoring | All stage-2 metrics plus: side-effect audit trail, authority breach counter, escalation rate, tool health |
| Exit criteria | Side-effect audit clean (no unexpected mutations); authority breach count = 0; escalation rate < 1%; all tools healthy (health-check pass rate > 99%) |

### Stage 4 — Full production (25–100% traffic)

| Parameter | Value |
|---|---|
| Traffic | 25% to 100% in 25% increments each 24 hours |
| Authority | Full per the authority contract; `side_effect_approval` may move from `gate` to `auto` after 7 days of clean audit |
| Duration | Continuous monitoring |
| Monitoring | All stage-3 metrics plus: cost-budget tracking, trace-to-eval feedback sampling, production-readiness re-review trigger |
| Exit criteria | N/A — continuous operation; triggers for fallback or disablement remain active |

### Rollout abort triggers (any stage)

If any of the following occurs during rollout, abort the current stage and fall
back to the previous stage's authority level:

- Any authority breach (stage 2+).
- Tool health-check failure for a critical tool (stage 3+).
- Cost-per-request > 150% of baseline for > 1 hour (stage 2+).
- p95 latency > 3x baseline for > 30 minutes (stage 2+).
- Escalation rate > 5% (stage 3+).
- Production-readiness review outcome changes to `defer` or `no-go`.

## 3. Fallback

Fallback is a predetermined safe behavior when the agent, model, or a tool
cannot operate at normal capability. Fallback is distinct from disablement:
fallback preserves reduced capability; disablement removes all capability.

### Fallback paths by trigger

| Trigger | Fallback action | Rollback to |
|---|---|---|
| Model endpoint 5xx > 30s | Switch to `model_fallback` from the production contract | Previous model version |
| Model regression detected (eval score drop > threshold) | Switch to `model_fallback`; trigger eval re-run | Previous model version |
| Prompt regression detected | Revert to previous `prompt_version` | Previous prompt version |
| Critical tool unhealthy > 2 min | Degrade authority: revoke that tool's actions; agent continues with remaining tools | Previous tool-set configuration |
| Cost budget 100% consumed | Degrade to read-only; queue mutations | Read-only mode |
| Cost budget 110% consumed | Disable agent entirely | Offline |
| Latency p95 > 5x baseline > 2 min | Degrade to read-only; switch to `model_fallback` if model is the latency source | Read-only mode |
| Authority breach detected | Immediate: block the action; escalate; if breach count ≥ 3 in 24h, disable | Disabled |
| Privacy breach (PII access outside scope) | Immediate: revoke all data access; escalate; mandatory security review | Read-only, no data access |

### Fallback verification

Every fallback path must be exercised in a non-production environment before
the agent enters Stage 2 (canary) of rollout. The fallback exercise record
includes:

- Trigger simulated.
- Fallback action executed.
- Time to fallback completion measured.
- Post-fallback agent behavior verified (reduced authority, correct degraded
  response).
- Recovery path tested (return to normal operation after trigger clears).

Fallback exercises are repeated at each production-readiness review cycle.
