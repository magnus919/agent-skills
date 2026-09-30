# DevOps and escalation eval authoring review

Added 27 September 2026. All previous case IDs, prompts, expected outcomes, and
assertions are preserved. Nine new output-quality cases exercise the new DevOps
and selective-judgment guidance. The table below gives reviewable satisfying,
contradictory, and missing-evidence response shapes; it is an authoring challenge
ledger, not a run of a model or a validated semantic grader.

| Stable case ID | Satisfying response shape | Contradictory near miss | Evidence not shown |
|---|---|---|---|
| devops-telemetry-economics | Independent archive, conservative analysis lane, delivery checks, complete cost versus severity rules | Replaces archive because recall is high; calls less than 1% filtering a proven saving | Mentions a filter without archive or cost boundary |
| devops-hypothesis-coverage | Competing hypotheses and discriminating read-only probes; expansion lane and fresh evidence | Claims high-confidence ranking can discover an omitted selector fault | Gives a ranked list without candidate-coverage or execution responsibilities |
| devops-repair-invariants | Current symptom/cause evidence plus executable rollout and credential invariants, unknowns and stability window | Declares resolved from Ready pods or restores old credentials | Names verification but supplies no governing invariant/check plan |
| devops-selective-ci | Optional allowlist, mandatory jobs, deterministic dependency closure, full conservative fallback and omission evaluation | Lets model skip mandatory security or its selected job's prerequisite | Lists jobs without eligibility/dependency or failure policy |
| devops-durable-response-loss | State/expiry-bound decision and authority; separate operation ID, reconcile effect before retry and reobserve after change | Retries a possibly completed rollback because workflow history exists | Mentions retries without operation identity or state freshness |
| selective-judge-frozen-policy | Relative versus absolute accuracy distinction, local selection/frozen grouped test, risk gates and live/replay distinction | Copies 0.9 to Laya and calls 99% retention 99% correct | Names a threshold without provenance, holdout, or acceptance-risk evidence |
| selective-judge-confident-unsupported | Missing-evidence review route, separate calibration/error ranking, confident-error and voting-policy tests | Accepts 0.90 mean confidence despite near-chance error ranking | Says confidence is imperfect without a routing/evaluation response |
| selective-judge-fallback-complementarity | Deferral-band rescue/regression/shared-error counts, fresh test, invalid-case denominator, unknown cost and controls | Claims agreement proves rescue or retunes on the report cases; drops failed calls | Names fallback but omits conditional error analysis |
| selective-judge-order-and-evidence | Identity-aligned full distributions, preserved extra classes, two-call costs, qualified adjudication, interval-based margin and live limits | Uses binary complement with tie/unknown or claims noninferiority from point estimate alone | Names averaging and accuracy without mapping/provenance/inference limits |

Each assertion is a semantic claim about the design or analysis visible in the
response. These cases ask for controls or evidence requirements, not for a judge
to infer that a deployment, repair, calibration study, or side effect happened.
Execution claims require external artifacts or actual run evidence. The current
prose grader can route these claims to manual review; structural validity and an
advisory model verdict do not establish a verified semantic pass or release gate.

For each case, review the assertions individually against all three shapes.
A response may meet one assertion and omit another. Allow equivalent valid
implementations; exact wording, threshold choices, and a named provider are not
requirements. Record any material rubric revision under the same stable case ID.
The CI resource-cap adjustment covers both generated response sides for the
expanded manifest; it does not increase the five-skill selection cap or promote
Jev's advisory audit to a required semantic gate.

## Separate trigger-boundary review

These are routing probes, not portable output-quality cases or measured runs.
The current description and route table were manually checked against them:

| Prompt | Expected routing | Reason |
|---|---|---|
| Rank bounded read-only incident probes with a typed model | Load System One, then DevOps reference | Semantic decision support; executor remains separate |
| Qualify a local model's confidence-based escalation to a stronger judge | Load System One, then selective judgment | Explicit cascade qualification, no assumed threshold parity |
| Use semantic relevance to select optional CI jobs | Load System One plus QA/release procedure as needed | Bounded relevance judgment, deterministic dependencies |
| Write exact RBAC rules for who can restart a deployment | Do not load System One solely for this task | Exact authorization belongs to policy and tool control |
| Explain Kubernetes rolling-update settings without a model judgment | Do not load System One solely for this task | Tool operations and availability design belong to Kubernetes/SRE |
