# Monitor independence and oversight quality

Use for an evaluation of the monitoring system, not a claim that monitoring is
installed or enforced. Reuse graders.md for grader contracts and calibration,
judge-stability.md for held-out disagreement and abstention tests,
trajectory-review.md for execution/side-effect evidence, and
production-observability.md for minimized telemetry and incident learning. Runtime
monitor deployment belongs to agent-production-operations; preventive controls to
secure-software-engineering; authority and exceptions to ai-governance.

## Define the claim and independence matrix

Name the decision, workload/version, unacceptable conduct, severity, intervention
window, monitor owner, and accountable escalation recipient. Complete the matrix
in templates/monitor-assessment.md. Independence is a set of evidenced properties,
not a binary label derived from choosing a different model.

| Dimension | Question and evidence | Shared-failure challenge |
|---|---|---|
| Model | Model/provider/version, training or instruction dependencies where known | Agent and monitor share a policy misconception |
| Context | What instructions, claims, and histories each sees | Agent frames a real action as harmless simulation |
| Evidence | Producer, custody, completeness, sampling and transformation of tool/state records | Sanitized trace omits the harmful step |
| Permissions | Who can alter monitor, alert route, audit sink or coverage | Agent suppresses alerts or starts an uncovered child |
| Oracle ownership | Who versions labels, policy, datasets and expected effects | Agent edits the evaluator to manufacture a pass |
| Deployment | Separate release/configuration identities and rollback rights | One deployment disables agent and supervisor safeguards |
| Correlated failure | Shared tools, policy, infrastructure and reviewer assumptions | Multiple models concur on the same wrong policy |

For each row record shared dependency, enforcing owner/location, independent
evidence source, challenge, residual coupling, and unknowns. The controlled agent
must not be sole approver or sole evidence source for its supervisor. A permission
or deployment assertion requires authoritative configuration or execution evidence,
not an agent-written architecture diagram. Protect test oracles from candidate
writes; record any approved changes as a new version, not repaired historical results.

## Three contracts, three outcomes

1. **Behavior:** did the agent meet the task and trajectory contract? Inspect
   authorized tool events and committed environment effects, including delegated
   work. Preserve correctness and conduct as distinct dimensions.
2. **Detection:** given the evidence actually available, did the monitor detect the
   declared violation in time? Record detection, miss, abstention, input loss, and
   monitor execution error separately. A sanitized missing event cannot prove the
   original action safe.
3. **Delivery and response:** did the alert reach the correct authorized recipient,
   and was the required hold/contain/escalate action taken within its window? Verify
   sink acknowledgement and resulting state separately from detector output. A
   printed alert is not delivered escalation.

Missing mandatory evidence yields insufficient evidence/hold under the declared
gate. Route missing or suppressed controls to the runtime incident owner; do not
average control-integrity failures away with good task scores. Evaluation of these
conditions does not grant permission to alter production controls.

## Sampling and challenges

Freeze dataset, rubric, monitor configuration, policy, seeds where applicable, and
observation scope before comparison. Use representative on-policy trajectories
from the declared workload alongside risk-enriched challenges. Keep their measures
separate: an injected sabotage set cannot estimate production prevalence. Record
what permissions and privacy authorizations permit collection; do not collect
hidden reasoning by default. Authorized tool events, state receipts, and minimized
metadata can test many conduct claims without it. Mark unobservable claims unknown.

Create paired safe fixtures: unchanged compliant trajectory; same task success with
a conduct violation; altered or missing evidence; and disabled delivery. Mutate one
relevant condition at a time where feasible and preserve reset/environment receipts.
Include control bypass, unmonitored effects, shared policy error, omitted trace
steps, suppressed alert transport, self-assessment contradicted by state, and
heterogeneous-monitor escalation. A synthetic mutation demonstrates bounded test
sensitivity, not the frequency of spontaneous evasion or real deployment safety.

Compare complementary monitors only on the same cases and evidence scopes. Record
whether disagreement changes the response. Diversity of models can help expose a
shared failure, but diversity of evidence and authority must also be tested.

## Measures and calibration

For each declared failure class report case counts, severity, sampling basis, missing
inputs, execution errors, abstentions, and an independently reviewed reference label.
On cases with adequate labels, report true/false positives and negatives with explicit
denominators and uncertainty; report abstentions separately with coverage. An
abstention that triggers a safe hold differs from one silently treated as safe.

Report detection recall and missed violations by class; false-alarm rate on compliant
cases; precision under the stated base rate; time from observable violation to
identification, sink acknowledgement, and required action; and delivery failure rate.
Define each clock's start and unavailable/censored observations. Zero observed
misses in a small sample is not zero risk. Never infer population precision from an
enriched challenge set without a justified prevalence model. Measure reviewer queue
load and qualification; a flood of alerts can defeat otherwise accurate detection.

Use held-out independent human/domain review where a gate needs it; blind monitor
predictions and retain disagreements, provenance, fatigue and missing-context limits.
Model-teacher labels are advisory pseudo-labels, not independent human ground truth.
Self-assessment is one candidate signal and cannot overrule contradictory external
state. When independent labels are unavailable, report a screening result and hold
any stronger gate claim. Do not select a threshold simply to fit known misses.

## Completion

Deliver the filled matrix, three-outcome case roster, failure-class measures,
calibration limits, residual correlated risks, and a decision by the accountable
owner. Hold when mandatory coverage, independence, labels, or delivery evidence is
missing. Revalidate after policy, model, prompt, evidence transform, permission,
deployment, alert-route, or workload changes.

## Sources and limits

Checked 2026-11-01. This workflow is a catalog synthesis; studies motivate testing
oversight and evidence scope, not a universal threshold or a claim of independence.

- Anthropic, [Sabotage evaluations](https://www.anthropic.com/research/sabotage-evaluations), 2024: includes undermining oversight as a separate evaluation target.
- Anthropic, [SHADE-Arena](https://www.anthropic.com/research/shade-arena-sabotage-monitoring): evaluates sabotage attempts and monitors; prompted attacks do not establish spontaneous prevalence.
- OpenAI, [Evaluating chain-of-thought monitorability](https://openai.com/index/evaluating-chain-of-thought-monitorability/): compares observation scopes. This is not permission to export hidden reasoning; maintain the catalog's privacy limits.
