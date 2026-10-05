# Agent-driven UI navigation with independent oracles

Use when comparing fixed navigation, live agent navigation, or verified-action
replay. This reference owns QA design. Tool skills own execution;
[verification-methodology](../../verification-methodology/SKILL.md) owns evidence
verdicts. Reuse [System One QA routing](../../system-one/references/qa-automation-pattern.md)
for replay → bounded typed judgment → generative/vision fallback; do not
reimplement its model integration here.

## Freeze the acceptance contract before navigation

Name the required cases and independent oracle IDs before the navigator sees
the UI. Keep that manifest and oracle implementation outside its write scope.
A navigator may choose how to reach a control, but cannot change expected values,
drop a required case, mark it optional, or rewrite an assertion to fit a result.
An independently reviewed specification is the oracle source, not the app's
success banner or an agent's explanation.

For a synthetic order: assert the expected account and item, exact persisted
quantity, one effect for the run's operation ID, and read-back after reload or
through a separate authorized session. A toast proves only presentation. Reset
fixtures per trial; snapshot the store before and after; test that another
account remains unchanged. Read-back through the same stale UI cache is not
independent persistence evidence. State whether the oracle uses an API, database,
separate session, or UI; observe the actual delivery boundary as well.

## Require these capabilities, not a named vendor

| Capability | Qualification check |
|---|---|
| Navigation | Current semantic tree or visual state, unique target identity, bounded actions and deadline |
| Verification | External immutable oracle IDs, exact checks, negative controls, separate freshness evidence |
| Replay | Record only independently verified actions; key app/build, fixture, account, params, target and oracle revisions |
| Invalidation | Reject wrong identity, stale state, ambiguous/missing targets and changed oracle before mutation; log miss/handoff reason |
| Repair | Finite attempt/action/time budget, proposed locator diff, fresh evidence, no oracle edits, rollback |
| Effects | Operation ID/idempotency support or a read-only reconciliation path after uncertain commit |
| Coverage | Frozen required IDs reconciled against executed, failed, blocked, skipped and missing IDs |
| Evidence | Run/attempt IDs, commit/build, oracle and fixture hashes, environment, path and redacted artifact references |

A same-route match is insufficient for account identity. Replay metadata is
not a verdict: rerun independent assertions on every replay. Do not cache a
prior pass. Invalidate when contract inputs change; expired evidence and
unsupported modalities take the declared fallback, not a confidence shortcut.

## Bound repair without concealing a regression

On replay mismatch, stop and capture state before handing off. Distinguish
miss (no action) from handoff (some actions ran). If a click may have committed,
reconcile the operation ID before retrying; a blind retry can double the effect.
Use a small declared budget (for example, one repair proposal and one independent
rerun); stop on exhaustion or unknown commit state. Keep the original failing
attempt and classify the repaired rerun separately. Review and promote a new
recording only after the independent checks pass. Never loosen an oracle, skip
a required test, or silently edit the canonical suite to produce green.

## Compare paths on the same faults

Run a clean baseline plus persistence loss, wrong-account state, stale replay,
duplicate effects, weakened assertions, and required skips/missing reports.
Include ambiguity, unavailable inference and budget exhaustion. Freeze labels
before runs, separate training/cache-recording from evaluation, randomize trial
order when measuring runtime, and reset state between trials. Report each path
(fixed, live, replay, replay-with-handoff) and each fault separately.

Count a false green when a reported pass violates the acceptance contract.
Distinguish detected functional faults from safe blocks and infrastructure
errors. Report faulty trials, false-green denominator, clean false blocks,
required/executed/skipped/missing coverage, first-attempt outcome, repaired
outcome, repeated-run disagreement, repair burden and artifact completeness.
For latency/cost retain wall time distributions, calls/tokens, billed cost if
available, cache preparation and fallback costs. Unknown cost is unknown;
zero model calls in a simulation says nothing about live inference economics.
A deterministic simulation tests the policy, not agent robustness or accuracy.

## Optional bounded text judging, including Jev

Route model setup and typed question qualification to
[system-one](../../system-one/SKILL.md). Optional jobs include semantic failure
triage or a Choice over fresh, text-described candidate controls. Supply trusted
instructions, explicit unknown/review, model and question revisions, schema
validation and a deadline. Measure against independent held-out labels per
judgment type. Text-only contracts cannot inspect pixels; unsupported gestures
or extraction need a separately qualified stage. Provider confidence does not
replace exact counts, identity, persisted state, permissions or required coverage.
Keep prose assertion suggestions advisory until independently qualified under
an explicit gate contract. No key or compatible executor means blocked live
inference, not a simulated model pass.

## Evidence handoff

Fill [the run record](../templates/agent-ui-run-record.md). Hash the navigator,
oracle, fixture, replay artifact and expected-ID manifest separately. Preserve
raw exit status and first-attempt trace, artifact creation time, source boundary,
redaction record and verifier identity. Link each verdict to those artifacts;
a summary alone cannot prove the checks ran. Compare frozen expected IDs to
observed reports even when every received report is green. Required skipped or
missing cases block completeness; an explicit scoped waiver records owner,
reason, expiry and residual risk without relabeling missing evidence passed.

Complete QA design when contract, bounded paths, fault matrix and evidence
handoff exist. Stop execution at the budget or access boundary and return
failed/blocked cases to verification-methodology for the criterion verdict.

## Primary sources and limits (reviewed 2026-10-05)

- [Verified replay documentation](https://e2e.tester.army/docs/cache): action recording and invalidation; product behavior is not independent quality evidence.
- [Decision executor contract](https://e2e.tester.army/docs/decision-models): bounded semantic-tree executor and separate text stages; documented support is not measured robustness.
- [Expo E2E guide](https://docs.expo.dev/guides/using-e2e/): integration context, not a vendor selection criterion.
- [Playwright agents](https://playwright.dev/docs/test-agents): planner/generator/healer workflow; independently protect mandatory coverage during repair.
- [Action caching](https://docs.stagehand.dev/v3/best-practices/caching): reuse action results; QA must still verify current effects.
- [Solved-issue correctness study](https://arxiv.org/html/2503.15223v2): passing selected tests can miss incorrect patches; its coding benchmark does not estimate UI-agent error rates.
- [UTBoost](https://arxiv.org/html/2506.09289v1): strengthens coding-agent evaluation with additional tests; motivates fault challenge design, not a claim about UI performance.
