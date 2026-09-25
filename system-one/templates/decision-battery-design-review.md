# Decision battery design review

Complete this before scaling a portable model comparison. Treat the existing v2 corpus as a draft until its intended test unit and answer rules have been reviewed. Keep this review with the methodology; store raw benchmark outputs outside the repository unless publication is requested.

## 1. Decision and counting unit

- Intended application decision and accountable owner:
- What counts as **one test**: distinct scenario / one question on a scenario / one network request / other:
- Target count **per domain**, stated in that unit:
- If a scenario has several questions, how are they related? Which results are correlated?
- Production call shape: independent calls / several questions in one call / both:
- Which model capabilities are in scope: Choice, Noul, Score, multi-label, abstention, or other?
- Which capabilities are deliberately out of scope, and why?

**Concrete counting example:** The provisional v2 fixture has 50 distinct scenarios per domain, with three judgments per scenario. That is 150 question judgments and 50 scenarios per domain. Confirm which count the requested evaluation means before treating the target as met.

## 2. Answer rule and consequence

For each question family, record:

| Question family | Allowed output and `other`/review lane | Exact evidence that makes an answer correct | Contradictory near miss | Missing evidence / ambiguity rule | Costly wrong answer |
|---|---|---|---|---|---|
| Choice | | | | | |
| Noul | | | | | |
| Score | | | | | |

- Is the expected answer a stipulated fact in the case, a domain expert judgment, or an observed outcome?
- What evidence can a reviewer see? What would remain **not shown** even if the model's wording sounds right?
- For high-stakes domains, who can adjudicate the rubric? Preserve reviewer disagreement and abstention instead of inventing consensus.
- Are ordinal levels genuinely ordered and distinguishable? Does Score require a distribution, an expected value, an argmax level, or more than one of these?
- What exact output is expected from each adapter? Do not treat a GLiNER label as a Jev/Laya probability.

## 3. Pilot case packet

Select a small, varied packet **before generating more cases**. Include each domain and primitive that the full battery will claim to cover. Within the packet, include direct, negated, quoted, stale, mixed-issue, missing-evidence, and out-of-domain examples where relevant. Avoid counting simple template substitutions as independent situations.

| Case ID / domain | Difficulty and phenomenon | Expected answer and rationale | Reviewer A | Reviewer B / domain expert | Disagreement or revision |
|---|---|---|---|---|---|
| | | | | | |

- Check a satisfying response, a contradictory near miss, and an answer that omits the required evidence for each consequential rule.
- Review both the case text and the exact serialized question/criteria that every endpoint receives; expected labels and rationales must not be sent.
- Mark ambiguous cases for revision or exclude them from scored results. Do not resolve ambiguity by looking at which model gives the desired answer.
- Record the packet's case IDs and rubric revision. Keep pilot cases separate from any final holdout used after tuning.

## 4. Expansion and comparison plan

- Domain list and target mix by answer class, difficulty, phenomenon, language, and source type:
- How generated variants differ in *reasoning demand*, beyond names, IDs, and surface wording:
- Independent real or expert-labeled holdout source, privacy treatment, and adjudication plan:
- Frozen question text, option order, thresholds, and adapter serialization:
- Single-question versus batched-question comparison, if either may be used in production:
- Baseline (rules, incumbent, majority class) and costly-error slices:
- Model identity, runtime, checkpoint, and endpoint topology to record:
- Timing protocol: client/server boundary, cold/warm state, batch size, concurrency, shared GPU load, p50/p95/p99, throughput, timeout and retry policy:
- Output location outside the repository and retention owner:

## 5. Review decision

- Pilot reviewers and date:
- Answer rules and counting unit accepted? yes / revise
- Ambiguous labels resolved or excluded? yes / revise
- Matched model inputs and performance conditions verified? yes / revise
- Expansion authorized for this evaluation? yes / revise
- If **revise**, list the smallest next change and repeat the affected pilot cases. Stop before bulk generation or model ranking.
