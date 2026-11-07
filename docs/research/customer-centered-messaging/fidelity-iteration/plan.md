# Final-copy fidelity iteration: frozen plan

Date: 2026-11-06. Baseline: `c728b82d2bf7770e9861a87b8f4682545f3272f4`.
Provider: Nous Portal. Requested model: `google/gemini-3.8-flash`, as selected by the
user. User budget: $5 cumulative; prior eight calls cost $0.1055236. No external
judge, web search, agent tools, fallback model or live Jev calls.

## Hypothesis and intervention

The previous comparison produced evidence tables that coexisted with unsupported
final copy. Explicitly distinguishing facts, proposals and unknowns, then auditing
the actual headline, proof, objection and action, may reduce those errors while
retaining usable copy. Candidate adds a focused reference, entrypoint routes,
message-template audit fields and brand-adaptation checks. It does not change the
underlying offer/narrative method or the grading contracts.

## Inputs and arms

Four new fictional briefs are frozen in `tasks.json`. The first two are development
cases. The last two are held back from generation until the candidate decision is
frozen. They are not independently sampled real tasks; the author constructed them
from the observed failure families. No source research or factual claims about real
businesses are implied.

Both arms receive the same user task and neutral system wrapper. Baseline receives
the current shared core and crafting references; candidate receives those same paths
at its snapshot plus the final-copy fact-check reference. No author exercise outputs,
eval assertions, expected answers or reviewer notes are sent to the generator.

Use temperature 0, top_p 1, max_tokens 6000, one fixed seed per case shared by arms.
Randomize arm order within each case; every call is independent. Save exact context
bytes/hashes, request reconstruction data, model metadata, full outputs, usage and
cost. Provider-reported model identity and seeds do not establish weight-level
pinning or deterministic repeatability.

## Bounded iteration and budget

- Initial development: 2 cases × 2 arms = 4 calls.
- If the development outputs identify a material candidate-specific defect, permit
  one focused revision and up to 2 candidate-only development reruns. Preserve the
  initial snapshot/output and disclose selection effects.
- Freeze the chosen candidate before revealing held-out generation results.
- Held-out: 2 cases × 2 arms = 4 calls, with no changes based on their outputs in this
  run. Report failures rather than tune against them.
- Maximum 10 successful generation calls for this iteration; maximum 12 total
  attempts if an interrupted request needs recovery. Count possibly billed attempts
  conservatively; no automatic retries. Stop before an attempt could exceed the
  remaining cumulative $5 budget. The cap is a ceiling, not a target.

## Author review criteria, fixed before generation

Use `reviewer_kind: model_teacher`: the authoring assistant reviews each output.
These are provisional model judgments, not independent human labels, calibrated
accuracy, deterministic semantic passes or a new release gate. Use the supplied
fictional brief as the local fact boundary; no paid model grader.

For every response record actual passages under these criteria:

1. **Material factual fidelity:** check final customer-facing claims for unsupported
   operational/technical/security properties, results, credentials, generalizations
   about alternatives, or contradictions of supplied facts. Distinguish a plausible
   proposal labeled as such from an asserted existing commitment.
2. **Uncertainty fidelity:** unsupported/unknown does not become confirmed absence.
3. **Commitment consistency:** assessment versus later project, request versus
   confirmed booking, prerequisites and unknown fee/response terms remain coherent
   across headline, answer, action and compressed copy.
4. **Deliverable completeness:** actual opening, proof caption, action/path, requested
   role or channel expression, and revision record are present. Audit-table presence
   is not required of baseline and is not scored as proof of correctness.
5. **Useful specificity:** the supplied audience/offer and distinguishing mechanism
   remain visible; refusing, asking only questions or replacing everything with vague
   copy is not a satisfactory response.

For each criterion use suggested `met`, `not_met` or `not_shown` with quoted or
located evidence. Report material errors individually; do not turn keyword matches
or a transport-success flag into semantic verdicts. No aggregate pass percentage or
inference to production/user/conversion performance.

Retain the candidate as an editorial improvement only if the observed evidence
supports better factual fidelity without sacrificing the supplied mechanism and
requested artifacts. Mixed results remain mixed; even clean held-out examples
provide only bounded synthetic evidence. Structural/CI merge checks remain separate.

## Provenance and delivery

Previous eight-response comparison: author artifact `messaging-comparison/report.md`
from 2026-11-06; total $0.1055236. The relevant observed mistakes were invented fee
promises, response times, customer reports, immutability/tamper evidence, and claims
that credentials do not exist when merely unspecified. This iteration's prompts
and new content are intended for this public open-source repository; the user
explicitly authorized the Nous credential and repository-text egress.

Preserve results in this research package. Deliver the skill change through PR,
required exact-head CI, review inspection, merge, post-merge verification and local
main synchronization under the continuing delivery directive. Do not reinterpret
an authored/model-teacher judgment as independent behavioral release acceptance.
