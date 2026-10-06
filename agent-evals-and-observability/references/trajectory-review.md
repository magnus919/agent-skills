# Trace and Trajectory Review

Review trajectories when correctness, safety, cost, or recovery depends on how the agent acted. Use the trace-review template to inspect:

- tool selection, argument validity, ordering, and permission checks;
- state transitions, retries, recovery, stopping, escalation, and loop controls;
- grounding: retrieval, tool-result use, citations, and unsupported claims;
- planned and observed side effects, including compensating or rollback actions;
- correlation between final outcome, latency, resources, errors, and environment state.

Specify permitted alternatives rather than forcing a single path when more than one safe trajectory can satisfy the contract. Grade environment-visible effects for idempotency and recovery. Capture the smallest trace fields needed for the claim; redact before review and record inaccessible evidence as a gap.

## Minimal Run And Step Contract

Keep a backend-neutral internal record even when exporting to a tracing system:

- run/case/experiment identifiers and parent-child correlation;
- dataset, agent/workflow, prompt/policy, model/provider, tool, grader, code, fixture, and deployment versions;
- environment and permission boundary;
- step type, start/end or sequence, outcome/error category, retry/attempt relation, and stop reason;
- selected tool and bounded/redacted arguments/result summary;
- state transition and planned/committed/rolled-back side effects;
- grounding/evidence identifiers that can be resolved under access control; and
- final outcome plus linked grader results.

Do not manufacture a conversation ID from content, expose chain-of-thought, or copy raw inputs merely to make a trace look complete. Record when sampling or access removed evidence.

### Optional intervention events

Intervention data is opt-in and question-scoped. A case retains the required
`human_interventions` nonnegative integer as its aggregate count; unknown is not
zero. The optional `intervention_detail` object has `coverage` (`complete`,
`partial`, or `not_collected`) and `events`. If absent, event detail was not
collected. If present, event objects allow only `id`, `actor`, `kinds`, `target`,
`boundary_reference`, `changes`, `outcome`, and `evidence_reference`. Actors are
`human`, `orchestrator`, or `system`; only human events contribute to the scalar.
Each input event counts once even if it has multiple unique kind codes.

Use bounded codes for event IDs, kinds, and outcomes (up to 64 characters,
`[A-Za-z0-9][A-Za-z0-9_.:-]*`) and bounded opaque, single-line references (up to
256 characters, no spaces). The target identifies `run_id` and `task_id`, with
optional `workstream_id`. The `changes` map records `goal`, `constraints`, and
`authority` as booleans or `null` when unknown. `complete` coverage requires the
scalar to equal the number of human events; `partial` coverage lists no more
human events than the scalar; `not_collected` requires an empty event list.
Store a shared event once at the owning/common parent task and link to it rather
than duplicating it across child cases; `(run_id, event.id)` is unique.

The code vocabulary is extensible; illustrative kinds include
`information_decision`, `authorization_gate`, and `resume_recovery`. These are
examples, not a required taxonomy. Opaque-looking references and short codes can
still encode sensitive information, and schema validation cannot certify their
privacy. Review actual values under the applicable privacy policy. If the task
asks only for answer correctness and does not require intervention attribution,
do not collect typed intervention detail.

Do not capture raw human messages, prompts, hidden reasoning, or free-text
justifications by default. Typed change flags and opaque evidence references do
not grant authority or establish causation. Do not infer success or productivity
from a lower intervention count alone.

## Review Protocol

1. Reconstruct the intended task and trajectory contracts without looking at the final score.
2. Follow the state and permission boundary through each step; compare tool arguments and observed effects to the contract.
3. Locate the first divergence, not only the last visible error. Distinguish model choice, orchestration, tool, data, environment, policy, and telemetry failures.
4. Test whether recovery avoided duplicate or unreconciled effects and whether stopping/escalation happened at the right boundary.
5. Compare final-answer quality with path quality. A correct answer from an unauthorized or fragile path still fails the trajectory contract.
6. Record evidence gaps, alternative valid paths, root-cause hypotheses, and the case/fixture changes needed before rerun.
