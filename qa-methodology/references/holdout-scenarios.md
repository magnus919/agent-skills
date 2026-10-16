# Holdout acceptance scenarios

Use when an implementing agent can adapt to visible tests and a release needs
additional evidence about unseen cases. Keep requirements and ordinary developer
regression tests visible. Holdouts supplement TDD; they must not conceal product
requirements or become the only feedback available during development.

## Define the boundary before implementation

1. A domain/QA owner derives scenarios from the accepted requirements, independently
   of the implementation. Record requirement IDs, expected observations and failure
   cases. Review oracle correctness before freezing; secrecy cannot repair a bad oracle.
2. Separate public requirements and development examples from withheld case inputs,
   fixtures, expected results and evaluator configuration. Give builders the complete
   behavioral contract, including boundary rules, without every concrete test instance.
3. Freeze a versioned case roster and content hashes before the candidate run. Record
   the verifier, access policy, candidate identity, environment and required coverage.
4. Enforce read isolation and write integrity in the runtime: a verifier-only checkout,
   storage identity or service can hold cases; builder credentials must not retrieve or
   modify them. A folder called `holdout`, a fresh session or a prompt instruction is
   insufficient. Check alternate tool access, shared history, logs, caches and artifacts.
   If isolation cannot be established, report it as unknown or exposed, not withheld.
5. Keep the verifier's expected results and gate configuration outside builder edit
   authority. Use harness-engineering for enforcement; QA owns case/oracle quality.

Use [the holdout record](../templates/holdout-record.md). Do not put withheld
fixture contents in a builder-readable copy of that record; keep a public index
of requirement IDs and an access-controlled evidence record where needed.

## Execute, diagnose and account for exposure

Run the frozen roster against the identified candidate at the relevant user or
service boundary. Record pass, fail, unrun and infrastructure-unknown separately.
A failed setup or missing case is not a successful scenario. Retain raw results
in the verifier's evidence store and expose only the feedback authorized by the
predeclared repair policy. Bind any verdict to candidate, contract, roster,
environment and execution evidence; an aggregate pass rate cannot hide a failed
required behavior.

Useful repair needs information. Record each feedback disclosure: recipient,
time, case IDs or affected case family, and what inputs, expected outputs or
failure summaries became available. Summaries, screenshots, traces and repeated
pass/fail queries can reveal test information even without exposing fixture files.
If the builder adapts from those results, affected scenarios are development or
regression evidence from then on. Preserve their failures and original version;
do not relabel them untouched after a fresh session, model switch or renamed ID.

Use a predeclared attempt/time budget. Once exhausted, route the failure to the
responsible owner rather than regenerating easier tests or hiding failed cases.
Correcting a defective oracle requires an owner-reviewed revision and rerun; it
must not be disguised as an implementation success. An independent owner can
freeze new cases for a subsequent unseen-case assessment. Repeatedly drawing new
cases until a candidate passes is selection, not clean generalization evidence.

## Worked example

The visible contract says a reset token expires at 15 minutes and can be used
once. Developers test the normal path and public boundaries. QA separately
freezes concurrent-reuse and expiry-boundary instances, with a controlled clock
and observable authentication state. The builder must know the single-use and
expiry requirements; withholding those requirements would make the test unfair.

Candidate A accepts a second use in a concurrency scenario. QA discloses the
race reproduction so the builder can repair it. That case becomes regression
coverage. Candidate B passing it demonstrates the repair on that known case,
not generalization to an unseen case. QA records the disclosure and runs any
remaining untouched cases under the original policy. No untouched cases left
means no untouched-case conclusion, not automatic release failure if the approved
release contract permits other adequate evidence.

## Completion and ownership

Finish when every required case has execution evidence or an explicit unresolved
status, exposure history is current, and the acceptance owner receives a scoped
verdict. Escalate ambiguous requirements, broken isolation or exhausted repairs.
Fresh sessions and different models may reduce anchoring but can share systematic
errors. Independent observations and reviewed oracles still matter.

For gate aggregation use spec-driven-development; for evidence verdicts use
verification-methodology; for statistical generalization use agent-evals-and-observability.
This procedure defines no universal hidden-test percentage or model-confidence gate.

## Source and limits

Motivation: Cole Medin, [holdout scenarios, 10:51–11:48](https://www.youtube.com/watch?v=GQatuTWSRqY&t=651s),
16 October 2026. His reported reliability improvement is practitioner experience,
not a reproduced comparison. The access, exposure and revision procedure above
is catalog synthesis; it does not claim measured effectiveness or rule out dark factories.
