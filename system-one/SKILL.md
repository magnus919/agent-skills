---
name: system-one
description: >-
  Design, integrate, evaluate, self-host, and troubleshoot typed System One
  decision models including TypeSafe Jev, Convai Innovations Laya, and CLM. Use for
  Choice/Score/Noul judgments inside deterministic software, app-control loops,
  routing, ranking, guardrails, calibration, semantic code linting and
  post-edit feedback, DevOps decision support, confidence-based escalation, or
  private open-model inference. Do not use for syntactic/style linting, exact
  policy or authorization, open-ended generation, or generic LLM serving without
  a bounded decision contract.
license: MIT
compatibility: Current provider/model documentation needs network access; local open-model operation needs a compatible runtime and model-weight storage.
metadata:
  author: system-one contributors
  version: "1.1"
---

# System One decision models

Use a model for a constrained judgment, not for permissions or side effects:

```text
authorized state + trusted typed questions -> validated model answers
-> deterministic policy -> act / wait / review / abstain -> observed outcome
```

Keep hard business rules, authority checks, thresholds, action execution,
confirmation, and rollback in code or human control. A legal response shape
does not imply a correct judgment; a high probability is not permission.

## Start here

1. Inspect the real application's state source, action boundary, tests, and
   deployment before changing it. Preserve existing deterministic/no-key
   behavior unless explicitly changing it is in scope.
2. Fill `templates/decision-contract.md`: trusted state, question IDs/types,
   allowed answers, unknown/review lane, side effects, owner, deadlines, and
   rollback. For tool control, also use `templates/action-control-contract.md`.
   New to this model class? Start with `references/worked-decision-pilot.md`
   to choose one bounded decision, then use `references/concepts-and-patterns.md`
   for primitive semantics and composition.
3. Open **only the matching reference** below. Keep exact question instructions,
   criteria, state paths, and thresholds in trusted configuration, not
   user-supplied state. IDs are for application code; TypeSafe documents that
   Jev does not send question IDs to the model, so put complete judgment
   meaning in each instruction. Other providers may have different contracts.
   For question wording or candidate extraction, read
   `references/question-design.md`.
4. Validate response IDs, types, option sets, distributions, score rubric,
   and finite values before policy code; record returned model/version and
   enforce the pinned deployment identity. Treat malformed,
   unavailable, stale, or low-evidence results as the specified fallback.
5. Verify on representative held-out data and the actual delivery boundary;
   record provider/model, question/policy revision, outcome, and failure lane
   without raw secrets or unnecessary personal data.

Before expanding a cross-model battery, complete
`templates/decision-battery-design-review.md` and review a small varied pilot.
Define whether a test counts a distinct scenario, a question, or a request;
freeze the answer rubric, comparison contract, and timing conditions before
generating more cases. If those definitions or reviewer labels disagree, stop
expansion and revise the design. Keep benchmark outputs outside this skill's
tracked corpus unless publication is explicitly requested.

## Route by task

| Task | Read next |
|---|---|
| Design questions, choose candidates, or extract values from source text | `references/question-design.md`; for broader application compositions, `references/use-case-patterns.md` |
| Hosted Jev API or SDK integration | `references/jev.md`; run `scripts/decision_demo.py` offline first |
| CLM typed decisions, candidate ranking, Qwen3 encoder, fine-tuning, or private serving | `references/clm.md` |
| Laya checkpoints, routing, language, CPU/GPU/MPS | `references/laya.md` |
| Fine-tune the English Laya checkpoint on labeled typed decisions | `references/laya-fine-tuning.md` |
| Native C++ Laya inference, CUDA/Vulkan, or Jev-compatible HTTP | `references/laya-cpp.md` |
| Local or private/VPC Laya service | `references/laya-self-hosting.md`, then `references/hosting-and-troubleshooting.md` |
| Skill suggestions with progressive disclosure and no-fit rejection | `references/implementation-audit.md` |
| Narration-to-media matching through captions or metadata; catalog answer/component selection | `references/use-case-patterns.md` |
| Browser/desktop/voice control, agent routing, ranking, guardrails, deadlines | `references/use-case-patterns.md` |
| Semantic code-lint rule design, local post-edit checks, graph scans, or feedback evaluation | `references/semantic-lint-feedback.md`; fill `templates/semantic-lint-rule.md` and `templates/feedback-evaluation.md` before a pilot |
| First System One pilot or worked evaluation of a decision, QA runner, or semantic CI gate | `references/worked-decision-pilot.md` |
| Learn from the 1,305-build field survey; identify implementation patterns and anti-patterns | `references/field-patterns-and-antipatterns.md` |
| Audit original browser, skill-router, supervisory, or moderation implementations | `references/implementation-audit.md` |
| Production QA step routing, cached replay, selector repair, or model substitution | `references/qa-automation-pattern.md`, then `references/evaluation-and-calibration.md` |
| DevOps telemetry routing, diagnostic test ranking, repair evidence, optional CI jobs, deployment transitions, or durable incident decisions | `references/devops-decision-patterns.md` and `templates/decision-execution-record.md`; operational procedures remain in SRE/QA/release and tool skills |
| Review the DevOps/escalation eval assertions and their satisfying, contradictory, or missing-evidence challenges | `references/devops-escalation-eval-review.md` |
| Confidence-based acceptance and escalation to a stronger judge | `references/selective-judgment.md` and `templates/cascade-qualification.md` |
| Probability, threshold, calibration, model comparison | `references/evaluation-and-calibration.md` and `templates/benchmark-record.md` |
| Design a matched comparison, qualify adapters, separate fixed-contract from model-adapted tracks, or assess equivalence | `references/comparison-design.md` and `templates/benchmark-record.md` |
| Compare singleton and batched request quality or calibration | `references/request-shape-evaluation.md` and `templates/benchmark-record.md` |
| Replace an LLM rubric judge, diagnose graded scale offsets, or test correlated judge errors | `references/rubric-judge-research.md`, then `references/evaluation-and-calibration.md` |
| Measure router ablations and full fallback economics | `references/cascade-economics.md` and `templates/benchmark-record.md` |
| Determine whether a decision model improves an agent harness | [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) for paired end-to-end tasks, trajectories, side effects, and cost/latency; keep this skill's model-level contract and calibration checks |
| Design or run a portable v1 label battery or provisional v2 cross-domain Choice/Noul/Score battery | `references/decision-battery.md` and `templates/decision-battery-design-review.md`; run `scripts/decision_battery.py` only after the pilot review |
| Synthetic QA pilot for Jev (failure triage, extra-test choice, semantic grading) | `references/qa-pilot.md`; run `scripts/jev_qa_pilot.py` offline first |
| Paired-eval semantic assertion audit in CI | `references/qa-pilot.md`, then `scripts/jev_eval_audit.py`; treat its verdicts as advisory and preserve exact grader results |
| Reproduce, operate, diagnose, or roll back this repository's Jev CI deployment | `references/jev-ci-reference-deployment.md`; inspect the current workflow before changing secrets or jobs |
| Screen Jev's advisory eval judgments against real outputs | `references/qa-pilot.md` and `references/evaluation-and-calibration.md`; use `scripts/jev_eval_calibration.py` for a blind packet, then independent labels or `scripts/jev_teacher_label.py` for model-teacher pseudo-labels |
| Select among Jev, Laya, CLM, GLiNER2.5-Decide, or another candidate | `references/ecosystem-radar.md`; then the selected model reference |
| Screen newer open typed-decision candidates from primary evidence | `references/open-decision-candidates.md`; then use `references/comparison-design.md` before benchmarking |
| Fastino GLiNER2.5-Decide local classification | `references/gliner25-decide.md` |
| Fine-tune GLiNER2 for Decide-style classification | `references/gliner25-decide-fine-tuning.md` |
| Failure, latency, device fallback, upgrade, rollback | `references/hosting-and-troubleshooting.md` |

For a hosted provider integration, refresh the provider's live documentation
index, then read the current API or selected SDK reference and the nearest
cookbook before coding. `references/jev.md` contains the Jev-specific route and
fallback procedure; its endpoint and contract details are a dated snapshot.

Run `python3 scripts/systemone_probe.py --request examples/request.json` for an offline
contract check. Add `--live` only when the user has authorized transmitting
that state and incurring cost. For local Laya, `scripts/laya_service.py`
requires a pinned local model directory and a runtime secret; it is a private
reference adapter, not a public Internet service.

## Cross-cutting limits

- Jev is managed/API-only; do not invent a self-hosted Jev weight download.
- Laya, CLM, and Jev can share a typed application interface, but not assumed
  thresholds, calibration, latency, language behavior, or model quality.
- Before enabling Laya caller traffic, keep ingress private and authenticated;
  define finite, application-specific caps for request bytes, question count,
  options per Choice, concurrency, queue wait, and total deadline. Readiness waits
  for the pinned model, tokenizer, actual device, and any calibration artifact the
  application uses. The bundled adapter's `/readyz` checks device residency only;
  extend it to cover every required artifact before routing production traffic.
- For large Laya Choice sets, check tokenized labels against the head-token
  budget, verifying coverage and truncation; an option-count transport cap does
  not prove quality. If shortlisting, measure recall and treat probabilities as
  conditional on exactly the retained candidate set. Prefer `other`, `unknown`,
  or review when labels are not exhaustive. See `references/laya.md`.
- Independent questions may share one call, but test the exact batched request
  shape on frozen cases. Dependent questions need another call when the first
  answer changes their state or candidate set.
- Predeclare whether a comparison holds decision semantics fixed or compares
  separately adapted model-plus-adapter systems. Qualify adapter polarity,
  schema, and overflow behavior before scoring; a compatible response shape is
  not evidence of semantic parity. Record the protocol in
  `templates/benchmark-record.md`.
- Validate error discrimination separately from probability calibration before
  confidence-based escalation. Freeze the route on selection data, then test
  absolute accepted risk and fallback rescue/regression on untouched units.
  Unsupported evidence or expired state cannot be overridden by confidence.
- A fallback judge or multi-provider agreement is not independent correctness
  evidence. Measure shared errors and held-out rescue/regression before claiming
  cascade quality gains; see `references/rubric-judge-research.md`.
- A semantic lint result is a model judgment, not proof that a code rule is
  satisfied. Keep syntax/schema checks deterministic, semantic findings
  reviewable, and gates advisory until independent grouped holdouts measure
  false passes, false blocks, abstention, drift, and complete task cost.
- A model cannot replace exact arithmetic, provenance, eligibility, safety
  reflexes, or irreversible approval. A text-generating model may be a separate
  bounded stage after a typed route, not an implicit source of authority.

Finish an integration only when its contract, held-out evaluation, failure
path, deployment/readiness check, and rollback record exist. For diagnosis,
stop after the smallest evidence identifies the boundary and one recheck
verifies a fix, or after three non-converging passes with evidence for the
owner. Do not generalize from a single demo or vendor benchmark.

## When not to use

Use `ml-engineering` for general training strategy; `docker-compose` or
`kubernetes` for their serving infrastructure; `ai-governance` for
organization-wide authority design. Use a generative-model skill for prose,
open-ended planning, or long reasoning without a typed-decision contract.
