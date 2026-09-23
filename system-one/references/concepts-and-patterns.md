# System One concepts and engineering patterns

Status: research snapshot checked 2026-09-22. The category is young; treat
provider claims and community benchmarks as hypotheses until reproduced on the
target workload.

## What the class is

A System One decision model consumes application state plus a trusted set of
typed questions. It returns a constrained answer and, where supported, a
probability distribution. It does not need to produce prose for software to
parse. The “System One” label is a product/architecture analogy to fast,
automatic judgment; it is not a guarantee of deterministic output, human-like
cognition, or correctness.

The useful separation is:

| Layer | Owns | Must not be delegated to the model |
|---|---|---|
| State preparation | Relevant, authorized evidence; redaction; normalization | Hidden policy, secrets, or untrusted instructions that change the contract |
| Decision model | A bounded judgment over the supplied state/questions | Exact arithmetic, permissions, provenance, or side effects |
| Policy code | Thresholds, weights, abstention, approvals, retries, action map | “Trust the model” as a policy |
| Human/control plane | Authority, risk appetite, exception handling, release/rollback | Automatic self-authorization |

## The three portable primitives

- **Choice:** select one label from a closed set. Include `other`, `unknown`,
  or `needs_review` when the set is not exhaustive.
- **Score:** choose a position on an ordered rubric. The returned value is often
  the probability-weighted expected level, so it can be between rubric points.
- **Noul:** estimate `P(yes)` for one proposition. Write the proposition so
  that its positive meaning is unambiguous.

Different runtimes may expose extra fields such as `action.act_probability`,
but those are not portable contract fields. Ignore them until validated on the
target data.

## Architecture

Jev's public description says it uses a new model architecture, a parallel
sampler, and RLCD (Reinforcement Learning for Calibrated Decisions). The
weights and detailed architecture are not public, so do not invent internals.

Laya's open runtime makes the mechanism inspectable: it renders state,
question, and candidate options into one sequence; reads learned decision
markers; turns per-option logits into a temperature-adjusted softmax; and
derives Choice, Score, and Noul values. Multiple questions are batched into one
forward pass. This is non-autoregressive decision scoring, not text generation.

## The decision contract

Record these before implementing:

1. State fields, source authority, maximum size, redaction, and serialization.
2. Question ID, type, exact instruction, criteria/levels, and positive meaning.
3. Allowed answer keys and explicit abstain/unknown behavior.
4. Deterministic policy for each answer and confidence/coverage lane.
5. Human owner, action authority, reversibility, rollback, and incident route.
6. Model/provider revision, calibration artifact, latency/cost budget, and cache key.

## Reliable composition

- Ask independent questions about the same state together. This reduces
  round trips and keeps the policy in code.
- Split a dependent question only when its state or candidate set is created by
  the earlier answer. Otherwise fan it out and ignore irrelevant answers.
- For composite judgments, score independent dimensions, normalize explicitly,
  apply named weights in code, and preserve the component scores for review.
- For many options, use deterministic shortlist/coarse-to-fine routing and
  then run the decision model on the shortlist. The resulting probabilities are
  conditional on that shortlist and must be labeled as such.
- Use a generative model after a typed route when prose or extended reasoning
  is needed; keep the route, handoff, and fallback observable.

## Probability and confidence

Probability is meaningful only relative to the proposition, label set,
population, and calibration data. Confidence is usually a summary of how
concentrated a Choice/Score distribution is. Neither proves factual support,
source authority, fairness, legal compliance, or authorization.

Use held-out target data to set action thresholds. Report risk-coverage curves
and calibration, not only argmax accuracy. A high-confidence wrong answer on an
unsupported language or out-of-domain case is a model failure, not evidence
that the threshold needs to be lower.

## Source pointers

- TypeSafe introduction and primitives: https://docs.typesafe.ai/introduction
  and https://docs.typesafe.ai/primitives
- TypeSafe confidence and patterns: https://docs.typesafe.ai/confidence and
  https://docs.typesafe.ai/patterns
- TypeSafe launch explanation: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- Laya runtime source: https://github.com/NandhaKishorM/laya
