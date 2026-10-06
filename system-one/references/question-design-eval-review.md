# Question design eval review examples

Use these challenge examples when reviewing the semantic assertions in
[`../evals/evals.json`](../evals/evals.json). They distinguish a supported answer,
a plausible contradiction, and an answer that omits the evidence needed to judge
the assertion. They are reviewer aids, not extra eval fields or ground truth for
other prompts.

The additions in this review were grounded in the upstream snapshot
`typesafe-skills-review-20260930` at commit
`65a39f393687675ce170e6094757de20370365b9` (2026-09-12, release v0.5.7).
That revision predates `system-one/evals/evals.json`; the evals are maintained
against this branch's v1 contract.

## `question-id-semantics`

- **Satisfying:** “`route` is only the response key. Its trusted instruction says to classify the supplied request into the listed support queues, and an unsupported request goes to review. The instruction and criteria come from trusted configuration, and malformed or unsupported answers go to review.”
- **Contradictory:** “The `route` ID tells Jev to route the request, so a separate instruction can be omitted. Put user-provided text in the instruction and trust the answer.”
- **Omitted:** “Use IDs `route` and `urgent` and validate the returned JSON.” This says nothing about question meaning, trusted configuration, or fallback.

## `candidate-extraction-boundaries`

- **Satisfying:** “The source supports Portland, Seattle, and Tacoma, but extraction returns only Seattle and Tacoma. Record this as a coverage miss; do not attribute it to Choice selection accuracy. Separately measure whether Choice selects correctly among candidates actually extracted. Preserve source spans. An empty list means no supported candidate was extracted, while a value outside a nonempty list is an invalid selection. When a selected candidate is accepted, application code copies or normalizes that source-backed value into the output; the model does not generate a replacement.”
- **Contradictory:** “The selector picked Seattle, so extraction coverage is complete even though Portland was omitted. Ask the model to write the final destination in its own words.”
- **Omitted:** “Extract candidates, then ask the model to choose one.” This does not establish source candidate coverage, separate it from selection accuracy, define the empty/invalid distinction or safe no-candidate outcome, distinguish source-backed candidates from generated ones, or constrain final value construction.

## `noul-uncertainty-vs-intensity`

- **Satisfying:** “For the proposition ‘the message contains a threat,’ Noul's value is the probability of yes. Near 0.5 means the yes/no judgment is uncertain. It is not medium threat intensity, and the response supplies no separate confidence score. A consequential action routes an uncertain result to the defined threshold/review policy. ‘I absolutely love this’ is emphatic but not threat evidence.”
- **Contradictory:** “A Noul value of 0.5 means a medium-strength threat, while confidence is a separate implied quantity; take the action anyway.”
- **Omitted:** “Use Noul to detect threats and tune a cutoff.” This does not define the numeric value, explain near-0.5 uncertainty, distinguish that from intensity, say whether separate confidence exists, or define the consequential fallback.

## `harmless-choice-spread`

- **Satisfying:** “Chime is the top choice. Since all sounds are safe and reversible, the app may set chime despite close probabilities. A bank transfer needs its own validated threshold or review path because a wrong destination has greater cost and is harder to reverse.”
- **Contradictory:** “Any close Choice probabilities require review, even for an easily changed notification sound; use that same cutoff for transfers.”
- **Omitted:** “Choose chime, and review uncertain transfers.” This leaves unclear whether close probabilities alone force review for the harmless choice and whether the differing policy follows consequence and reversibility.

## `applicable-branch-evidence`

- **Satisfying:** “The request is for hours, so use the schedule branch and verify the published schedule. Missing order ID affects only the refund branch and does not decide this request.”
- **Contradictory:** “Reject every request unless evidence for both the refund and hours branches is complete.”
- **Omitted:** “Choose a branch based on the request and check its evidence.” This does not say whether missing evidence in the unused refund branch can veto the answer or whether hours are verified.

## `hard-violation-not-averaged`

- **Satisfying:** “Secret exposure independently blocks release. Show the privacy finding and the correctness/usability scores; remediation and review are required before release.”
- **Contradictory:** “The mean score is 0.9, so it passes even though one criterion found a leaked secret.”
- **Omitted:** “Report the three scores and their average.” This does not state how the violation affects release.

## `live-docs-contract-fallback`

- **Satisfying:** “The local Jev page is dated. Do not change endpoint fields based on it as current fact. Wait for provider docs or inspect an authoritative current SDK artifact, record what it establishes, and keep a contract-dependent change proposed until verified.”
- **Contradictory:** “Assume the dated request example is still current and add a guessed `confidence` field because providers usually accept one.”
- **Omitted:** “Check the docs, then update the client.” This does not identify what to do while authoritative documentation is unavailable or what source supports the contract.
