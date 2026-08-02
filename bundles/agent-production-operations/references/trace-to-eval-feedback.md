# Trace-to-Eval Feedback

Defines the production-to-evaluation feedback loop: how production traces,
incidents, and operational signals feed back into evaluation cases, release
gates, and agent improvement.

## The feedback loop

```
Production traces ──► Sampling ──► Review ──► Eval case generation
       ▲                                               │
       │                                               ▼
       │                                     Eval suite update
       │                                               │
       │                                               ▼
       └──────────────────── Release gate ◄── Eval re-run
```

Production evidence flows in one direction (production → eval) and eval results
gate production promotion (eval → production). The loop is closed: every
production incident attributed to agent behavior must produce at least one new
eval case or update an existing case.

## 1. Trace sampling

### What to sample

Not every production trace becomes an eval case. Sampling is triggered by:

| Trigger | Sampling rate | Rationale |
|---|---|---|
| Authority breach | 100% (every breach) | Breaches reveal eval gaps; every breach is reviewed |
| Escalation event | 100% (every escalation) | Escalations reveal ambiguous or unsafe agent behavior |
| Tool failure with unexpected output | 100% | Tool failures may indicate edge cases not covered by evals |
| Cost budget breach | 100% | Budget breaches may indicate runaway behavior |
| Latency spike (p95 > 3x baseline) | 100% of spike-period requests | Latency spikes may indicate model or prompt degradation |
| User-reported incorrect output | 100% | Direct user feedback is the highest-signal input |
| Random sample of normal-operation traces | 1% of requests | Baseline drift detection |
| Model version change (first 24h) | 10% of requests | Increased sampling after model changes to detect regression early |

### Privacy constraint

All sampled traces MUST be scrubbed of PII before entering the feedback
pipeline. The scrubbing process is owned by
[privacy-engineering](../../privacy-engineering/SKILL.md). At minimum:
- Remove names, email addresses, phone numbers, physical addresses.
- Remove or tokenize user IDs.
- Remove conversation content that contains personal information not relevant
  to the agent's task.
- Redact credentials, tokens, and secrets.

## 2. Review

Sampled traces are reviewed by the agent's owning team. The review answers:

1. **Did the agent behave correctly?** If yes, no action. If no, classify the
   failure mode.
2. **Was this failure mode covered by existing evals?** Check the current eval
   suite for a case that would have caught this behavior.
3. **If not covered, what eval case would have caught it?** Define the new case.
4. **Is this a model regression, prompt regression, tool regression, or policy
   gap?** Classify so the fix targets the right dimension.

### Failure mode classification

| Failure mode | Example | Fix target |
|---|---|---|
| **Incorrect output** | Agent gave wrong information | Prompt refinement, model update, or new eval case |
| **Authority overreach** | Agent attempted an action outside its permitted scope | Authority contract update, new eval case for authority boundary |
| **Unsafe side effect** | Agent performed a mutation that should have been gated | Side-effect contract update, tool registration change |
| **Missed escalation** | Agent should have escalated but didn't | Escalation threshold tuning, new eval case |
| **Over-escalation** | Agent escalated for a trivial reason | Escalation threshold tuning |
| **Cost runaway** | Agent consumed excessive budget on a single request | Cost budget tuning, rate limiting |
| **Latency degradation** | Agent response time degraded beyond threshold | Model fallback tuning, timeout configuration |
| **Privacy violation** | Agent accessed or exposed PII outside scope | Authority contract restriction, immediate security review |

## 3. Eval case generation

For each reviewed trace that reveals a gap, generate an eval case:

### Case template

```
id: trace-<ISO-date>-<failure-mode>-<N>
prompt: [The production prompt or a close equivalent, scrubbed of PII]
expected_output: [Describes the CORRECT behavior the agent should have exhibited]
assertions:
  - [Observable property the correct behavior must satisfy]
  - [Observable property the incorrect behavior would violate]
  - [If applicable: authority/escalation/fallback behavior required]
case_set: regression
source_trace: [Reference to the scrubbed production trace]
source_incident: [Reference to the incident-learning record if applicable]
```

### Case quality gates

Before a trace-generated eval case enters the eval suite:

1. The case must be reviewed by a human (not auto-generated).
2. The case must not be a duplicate of an existing case (check by semantic
   similarity to existing cases).
3. The case must test observable behavior, not internal state.
4. The case must be placed in the appropriate case set: `dev` (under
   development), `regression` (in the regression suite), or `release` (in the
   release-gate suite).

## 4. Eval suite update

When new cases are added:

1. Run the full eval suite with the new cases against the current agent version.
2. If the agent fails the new cases, the cases are added to the release gate
   (`case_set: release`) and the agent version is blocked from promotion until
   the failures are resolved.
3. If the agent passes the new cases, the cases are added to the regression
   suite (`case_set: regression`) to prevent future regression.
4. Record the eval suite update in the agent's production contract.

## 5. Release-gate feedback

Trace-to-eval feedback affects release decisions:

| Feedback signal | Release-gate effect |
|---|---|
| New `release`-set cases added from recent production incidents | Block promotion until cases pass |
| Regression detected by `regression`-set cases | Block promotion; investigate regression source |
| No new cases or regressions in the last review cycle | Evidence of stability; supports promotion |
| Incident-learning record shows verified closure for all agent-attributed incidents | Required for promotion past Stage 2 of rollout |

## 6. Incident-learning integration

When an incident-learning record attributes root cause to agent behavior:

1. The incident record is linked in the trace-to-eval feedback log.
2. All traces from the incident window are sampled at 100%.
3. At least one eval case is generated per distinct failure mode identified in
   the incident.
4. The eval cases are added to the release gate (`case_set: release`).
5. The agent's authority is reduced per the production contract incident-input
   rules until the new cases pass AND verified closure is recorded.

This ensures that every agent-attributed incident produces a durable eval
artifact that prevents recurrence — closing the loop from production back to
evaluation.
