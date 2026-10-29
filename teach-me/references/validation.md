# Validation protocol

## Behavioral verification

Use the portable cases in `evals/evals.json` as observable contracts. Separate
routing probes in `evals/triggers.json` test discovery boundaries; selection by a
model is a routing smoke check, not proof of client-side automatic invocation.

Run each scenario in a fresh context with the skill and only the raw task and
materials. Do not give the tutor expected outputs, assertions, or prior defects.
For multi-turn cases, a separate learner/controller supplies the next utterance
based on actual tutor behavior. Preserve the full transcript and retrieval/tool
order privately outside the source tree. Never let the tutor invent learner turns.
Use safe temporary workspaces; no paid experiments, account changes, live-system
mutations, or scheduling is needed.

Inspect sequence as well as prose: source inspection must precede subject plans,
diagnostics, and instruction. Check source support, scope/version, example/key
verification, actionable feedback, adaptation, and stopping behavior. “I checked”
is not evidence of a tool call. A citation's presence is not proof it supports a
claim. For offline cases, inspect the actual supplied source bytes.

Record candidate content hash, model/harness identity when available, prompt and
fixture identity, scenario turns, tool evidence, and assertion verdicts with exact
output references. Grade each as met, not met, or not shown; unavailable evidence
must not become a pass. Keep generated transcripts and model-review rationales
out of public artifacts, following repository conventions. Publish a concise
sanitized run summary and unresolved limitations, not invented human adjudication.

Challenge every rubric with a satisfying response, a plausible contradiction,
and an omission. For example:

| Criterion | Satisfying | Contradictory | Not shown |
|---|---|---|---|
| Research before instruction | Actual source read precedes the lesson | Lesson precedes retrieval | Only final answer captured |
| Accept valid alternatives | Independently checks and accepts equivalent result | Rejects solely because key differs | No alternative submitted |
| Honest performance record | Labels copied example assisted | Calls copied work independent mastery | No progress judgment |
| Source supports claim | Passage states relevant versioned behavior | Citation states opposite or another version | Source passage unavailable |
| Respect stop | Acknowledges and ends | Continues quiz after stop | No stop request in trace |

Generalize this three-way check to each case assertion. Semantic review remains
model review unless a human actually performs it. Fix demonstrated defects, rerun
affected scenarios, and bind results to the revised candidate. Structural validators
check packaging; they cannot establish teaching quality. Do not silently omit
failed or incomplete cases from the denominator.

## Human validation, proposed only

No participants are recruited by this skill. Before making learning-efficacy
claims, obtain appropriate consent, privacy arrangements, subject-expert review,
and institutional oversight where applicable. Define the intended population,
domain, prerequisites, accessible formats, and comparison condition first.

Use a preregistered pilot with an appropriate sample-size rationale and comparable
time/materials. Randomize or counterbalance conditions where feasible. Have a
subject expert prepare parallel assessments and a rubric independently of the
tutor prompts. Assess baseline knowledge, assisted practice, immediate unaided
performance, changed-context transfer, and delayed retention separately. Choose
the delay and transfer task for the real use case before examining results.

Use blinded scoring where possible; report errors, attrition, accessibility
barriers, source failures, time burden, and adverse experiences alongside scores.
Satisfaction and engagement are secondary outcomes, not substitutes for learning.
Include uncertainty and subgroup limitations, and avoid generalizing a narrow
pilot to all learners or subjects. Give participants a way to stop and request
data deletion. Persistent notes or future contact need separate explicit consent.

The current release can claim only the checks actually completed. Simulations
and model reviewers can reveal behavioral failures; they cannot certify that
humans learn faster, retain knowledge, or become expert with Teach Me.
