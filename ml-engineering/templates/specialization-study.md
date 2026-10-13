# Preregistered model-selection and specialization study

Study ID/revision/date/owner:
Status: proposed / frozen / running / complete / rejected / inconclusive.
Changes after outcome inspection require a new study or an explicit exploratory label.

## Falsifiable question

- User outcome and measurable task failure:
- H1 simplest sufficient baseline; H2 adaptation benefit; H3 sampling/leakage explanation:
- Output: class/probability/ranking/extraction/text/code/agent actions:
- Harm/cost constraints and decision authority outside the model:

## Candidate comparison matrix

| Candidate | Permitted information | Training/labels | Harness/policy | Resource budget | Why included |
|---|---|---|---|---|---|
| Existing rules/system | | | | | |
| Linear/boosted-tree or text classifier | | | | | |
| Zero-shot NLI/embedding baseline where task-appropriate | | | | | |
| Base model with prompt/retrieval control | | | | | |
| SFT candidate | | | | | |
| RL/preference candidate if warranted | | | | | |

Equal context/feature cutoff and fair tuning budgets:
Different feature/representation, threshold or policy comparison separately named:
Zero-shot label wording/set/multi-label normalization and calibration limits:

## Data freeze

- Immutable source/dataset hashes and rights/provenance decisions:
- Source/repository/user/family groups and temporal availability/maturity cutoff:
- Train / development / calibration / sealed final splits:
- Exact/semantic duplicate audit and public benchmark/pretraining limits:
- Expected task roster IDs, group identities and immutable reference/test suite:
- Delayed outcomes, intervention censoring, sampling prevalence adjustments:

## Metric and acceptance contract

- Primary task metric, minimum improvement and baseline:
- Classification: precision/recall at fixed error/review budget, calibration and harm/value:
- Code: independent solve rate, preserved tests and task-critical regressions:
- Timeouts remain budget failures; infrastructure/missing evidence cause HOLD:
- General-capability and multi-turn regression ceilings:
- Complete-task latency/resource/cost ceilings, including selection and verification:
- Sample-size rationale; training seeds and generation seeds separately specified:
- Independent-group interval method; multiplicity/selection policy:
- Release requires all registered guardrails, not an aggregate score or helper exit:

## Reproduction contract

Model/tokenizer/adapter revisions; code/config/environment/container hashes:
Dataset/harness/decoding/budget hashes; expected_case_ids; raw output/receipt pointers:
Fixed max attempts, generated tokens, tool calls, wall time and timeout rules:
Rollout/verifier/training resources and checkpoint selection:
Fresh reload, resumed state, merged artifact and target-runtime tests:

## Stop and decision

Hard spend/resource ceilings and diagnostic stop conditions:
Who can change the study; exploratory outcomes and rejected runs preserved:
Decision: no adaptation / data or harness repair / proceed to bounded pilot / reject /
inconclusive / promote with all gates evidenced.
Evidence that would change the decision:

For descriptive saved-receipt comparison, use `scripts/compare_task_runs.py` and
synthetic `templates/task-run-{baseline,candidate}.json` as contract examples.
Those examples are authored fixtures, not model outcomes or release evidence.
