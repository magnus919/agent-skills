# Typed decisions in QA automation

Use this pattern when a test runner needs a bounded judgment such as step
classification, element selection, failure triage, or semantic assertion
review. It generalizes beyond Jev to any candidate that supports the required
typed contract. The 2026-09-20 Thunders article on Jev in test automation
motivated this pattern. Its latency, variance, workload, and product claims are
vendor observations, not portable benchmarks. The synthetic Jev pilot in
`qa-pilot.md` is separate evidence and does not validate a production gate.

## What the QA example teaches

A test step can take three materially different paths. Verified replay needs
no model and is repeatable while its invariants hold. A typed decision can
resolve an uncached or changed step with a fixed answer shape and an explicit
fallback; low observed variance still does not make it deterministic. A
generative or vision stage handles evidence and tasks outside that contract.
Measure each path separately instead of quoting one model's latency as the
whole suite's speed. In Thunders' reported comparison, Jev responses took
roughly 100–200 ms and the compared LLM calls 2–10 seconds. Those figures
reflect its test setup and say nothing definitive about another deployment's
network, queue, candidate set, or accuracy.

## Route each step through the cheapest valid path

1. Apply exact assertions and validated, versioned replay artifacts in code.
   A cached selector is usable only when its page and target invariants still
   hold. Record a cache miss or invalidation instead of silently healing it.
2. For unresolved *bounded* judgments, prepare a compact authorized state and
   fixed Choice, Score, or Noul question. Use a typed model only if its input
   modality and budget cover the evidence. Preserve an `unknown` or review
   answer when the candidate set is incomplete.
3. Route genuinely visual evidence to a vision capable stage and open-ended
   test writing or explanation to a generative stage. Validate any proposal
   before it becomes a selector, assertion, or action.
4. Keep exact counts, arithmetic, dates, permissions, mandatory tests, and
   release gates in deterministic code. Recheck page freshness before acting.
   An unavailable or borderline model result takes the recorded fallback.

For example, a stable login button may replay a verified selector. A changed
page may need a Choice over current candidate elements. A canvas-only control
needs visual evidence. An invoice total or date assertion belongs in code.
If the page state exceeds the model's usable budget, extract a deterministic,
auditable subset or take another path; silent truncation can remove the very
evidence needed to judge the step. Batch independent questions about the same
state when supported, while retaining distinct question IDs and answer checks.

## Make repairs reviewable

Record the old and proposed selector or assertion, observed state reference,
decision path, model and question revision, probability, validation result,
and responsible reviewer. A model proposal must not silently rewrite the
canonical suite. Keep rollback to the prior artifact. Store screenshots or
page captures only under the application's data retention rules. A probability
does not explain why the model chose a target or prove a repair is correct.

## Evaluate the router, not just the model

Maintain separately labeled golden sets for element choice, step intent,
failure triage, and semantic assertions. Include first runs, cache misses,
changed pages, ambiguous targets, missing evidence, and visual-only cases.
Freeze a held-out set and compare the current runner, exact rules, and each
candidate model under the same state, labels, and policy. Measure cache-hit
rate, invalidation correctness, false accepts, abstentions, repair review
outcomes, end-to-end test stability, latency distribution, and cost per run.
Repeated identical calls test variance; they do not prove correctness or
calibration. Pin model and question revisions when tuning thresholds, then
re-evaluate before swapping either one. Compare *each decision type* on its
own golden set: a strong selector model need not be a strong assertion grader.
Treat the router and frozen evaluations as durable interfaces so a provider
change can be assessed without rewriting the suite.

State size, modality, residency, provider capacity, and burst rate are
admission criteria for a candidate, not afterthoughts. A provider without an
approved processing region stays outside that tenant's route. The article
described Jev as text-only, with a 32k state budget and no published EU region
at the time; verify current contracts before routing real test data. It also
flagged counting, calculation, and date comparison as unsuitable model tasks,
which is why exact assertions remain in code. Provider claims of calibrated
probabilities need independent, task-specific checks; no individual score
guarantees correctness. `evaluation-and-calibration.md` defines the quality
and release evidence needed before enabling automatic decisions.
