# Ranking with Score or pairwise Choice

Read this when a bounded shortlist needs a relevance order, a practitioner
suggests replacing Score sorting with pairwise Choice, or a comparison uses
Bradley–Terry aggregation. Use `comparison-design.md` for the evaluation
contract and `question-design.md` for question wording. Retrieval and asset
eligibility stay outside the ranking model.

## Choose the decision before the primitive

| Needed decision | Starting pattern | Boundary |
|---|---|---|
| Place each item on a meaningful descriptive scale | One Score question per candidate; sort in code | Write independent, concrete levels; score is a weighted position, not correctness probability |
| Compare two close candidates by one criterion | Choice over two explicit candidates | Relative preference alone says neither candidate is useful |
| Rank a whole shortlist from pair preferences | Versioned comparison graph plus deterministic aggregation | Schedule, order handling, ties and fitting are part of the treatment |
| Reject a shortlist with no usable answer | Separately qualified absolute-relevance or review policy | A pairwise winner must not bypass this policy |

Do not assume pairwise Choice is a better ranker. A practitioner tip nominates
an experiment; evidence from a generative LLM does not establish Jev's behavior.
Keep a well-designed Score baseline and the existing retrieval order.

## Build comparable questions

For Score, provide the query and one candidate, then descriptive levels that
match the labeling rubric. Example for passage relevance:

```text
Not relevant: unrelated and supplies no answer.
Related: concerns the topic but does not answer the query.
Highly relevant: supplies a useful but incomplete or indirect answer.
Perfect: directly and completely answers the query.
```

Each level must make sense on its own. Do not describe levels as numbers or
“better than the previous level.” Create a distinct question ID per candidate;
IDs preserve application mapping but do not supply the question's meaning.
Name the state path in the instructions. Sort the returned Score in trusted
code and use a frozen, label-blind rule for numeric ties.

For pairwise Choice, provide the same query and two candidate texts under
neutral labels. Ask which better answers the query under the same relevance
criterion; avoid bundling accuracy, style, cost and authority into one preference.
Keep source IDs, labels, grades and source ranking out of model state when they
are not needed for judgment. Treat instructions inside candidate text as data;
test hostile examples rather than assume this wording defeats injection.

Freeze whether a pair can be tied or unanswerable. A binary forced choice
cannot express a genuine tie or “neither is relevant.” Exact equal output
probabilities may be mapped to half-wins by a declared rule; near-equal
probabilities are not automatically semantic ties. Adding tie/no-evidence
options changes the judgment contract and the fitting method; qualify that
version separately rather than renormalize away these outcomes.

Use seeded, counterbalanced candidate presentation and map answers back to
candidate IDs. Test repeat calls, reversed passage positions and reversed
criteria insertion order separately: these interventions are not identical.
If combining both orientations, freeze how conflicts become ties or review,
count both calls in the budget, and evaluate the combined system.

## Schedule comparisons before fitting

Exhaustive comparison uses n(n−1)/2 pairs, or twice that if both orientations
are requested. With eight candidates, that is 28 or 56 judgments against eight
independent Scores. Batching changes request count and repeated state cost;
it does not remove the pair judgments. Test the exact shared-state/batch shape
before assuming singleton accuracy transfers.

Sparse schedules reduce work but change which opponents each candidate sees.
A connected graph is necessary to compare all candidates from observations.
A cycle supplies equal degree with few edges; a star concentrates comparisons
on one hub. Both can lose information available to exhaustive comparison.
Raw win totals from unequal schedules are not an opponent-adjusted ranking.
Do not use a regularizer to disguise missing observational connectivity.

Specify the scheduler, seeds, edge direction, repetitions, selection budget,
and graph-connectivity test. An adaptive scheduler also needs a frozen policy
for selecting each next pair, deadline and maximum calls. Treat “same number
of questions,” “same tokens,” and “same dollars” as different comparisons.

## What Bradley–Terry does

The model assigns one latent worth theta_i per candidate and models a pair as:

```text
P(i beats j) = sigmoid(theta_i − theta_j)
```

Fit observed wins/half-wins with an identifiable convention, such as centered
worths. Check separation, finite parameters, convergence and residuals. A
fixed regularizer can keep a fit finite when an item always wins; disclose
its strength and evaluate sensitivity on development data. Its existence
does not establish that the single-worth model fits the judgments.

Hard model choices are observations of model preference, not human truth.
Using returned probabilities as fractional counts is a separate estimation
choice; those probabilities are not repeated observed match frequencies.
Never use confidence weights merely because high confidence sounds reliable.

For a complete, equally weighted round robin with the same symmetric L2
penalty on every worth, Bradley–Terry ordering follows win totals, including
ties. Its first-order equations equate each win total with a monotone function
of that candidate's worth given the common opponent pool. Consequently,
Bradley–Terry need not improve ranking over simple win totals in that design.
This mathematical observation does not transfer to incomplete, unequal or
candidate-specific weighted schedules. Preserve a win-total ablation.

Cycles can coexist with a useful aggregate ranking; a fitted ranking can also
hide systematic inconsistencies. Count cycles and inspect errors by independently
labeled relevance gap, including tied labels. Repeat stability and pair agreement
are diagnostics, not substitutes for correctness of the final ranking.

## Evaluate the whole ranker

Predeclare the sampling frame, candidate construction, rubric, grouped splits,
primary query-level ranking metric, practical effect, uncertainty method,
cost/latency limits, and terminal failures. Use independent labels and retain
unjudged/unknown cases explicitly. Reranking cannot recover a candidate absent
from the shortlist; fully judged shortlist evidence does not establish retrieval
recall or full-corpus search benefit.

Compare a strong Score control, pairwise plus aggregation, the incumbent, and
cheap aggregation baselines on identical candidate sets. Fit or select prompts,
graph schedules, penalties and thresholds only on development data. Freeze the
whole system before final calls. Pair and bootstrap at independent query/source
groups, not pairs or repeated requests; report effect intervals and slice counts.
A small or null result is not equivalence evidence.

Measure total tokens, billed-cost estimates, all charged attempts, and time
from ranking invocation through validated results and completed aggregation.
Record model revision, request shape, concurrency, measurement window and
sample counts. Keep token-derived public-price estimates distinct from observed
account invoices. A quality gain with a failed practical guardrail can be
documented as a costly option; it is not a default replacement.

Provider serialization can round Score and displayed probabilities. Validate
finite values, scale, labels and identity; choose consistency tolerances from
the observed/documented precision instead of exact reconstructed equality.
Do not silently change a frozen validator after a failed study. Preserve the
terminal failure and register any corrected study on fresh units.

## Evidence and limits

The repository's 2026-10-13 Jev study is recorded in
[the experiment readout](../../docs/experiments/jev-ranking/README.md).
Read its freeze, denominators, costs and limitations before citing its result.
On 83 held-out queries (77 with defined nDCG), exhaustive Choice gained
0.0069 nDCG@5 over Score, with a 95% paired interval of [-0.0131, +0.0271],
at 4.03 times the input tokens and 2.82 times p95 complete-ranking latency.
Both sparse schedules lost quality. The exploratory study supports retaining
Score as the starting point for that workload, not a universal winner.
It tests a particular model, question rubric and eight-passage shortlist;
it does not qualify other models, batch shapes or a production relevance gate.

Primary research and provider sources checked 2026-10-13:

- [Qin et al., pairwise ranking prompting](https://arxiv.org/html/2306.17563v2):
  studied generative rankers, win aggregation, order symmetrization and schedules;
  no Jev Score-versus-Choice test.
- [Yan et al., ranking/relevance consolidation](https://arxiv.org/html/2404.11791v1):
  relative ranking and absolute label agreement can diverge.
- [Zhuang et al., setwise ranking](https://arxiv.org/html/2310.09497v2):
  method/backbone-dependent effectiveness and efficiency tradeoffs.
- [Turner and Firth, BradleyTerry2](https://www.jstatsoft.org/article/view/v048i09):
  fitting, order effects and diagnostic methods; our L2 choice is not their
  bias-reduced estimator.
- [Brocai and Becker, pair difficulty](https://arxiv.org/html/2609.37577v1) and
  [Chawla et al., multiple latent orderings](https://arxiv.org/html/2609.22170v1):
  recent preprints motivate gap-aware diagnostics and model-misspecification
  checks; neither validates Jev passage ranking.
- [TypeSafe Score](https://docs.typesafe.ai/primitives/score) and
  [Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13):
  descriptive levels, interpretation, context and order effects. Refresh these
  before implementation.

Finish a ranking pilot with a frozen contract, evidence readout, complete
failure accounting, and explicit use/no-use/inconclusive decision. Stop on a
registered budget, identity, contract or provider failure; do not turn missing
judgments into confident wins or rerun failures until the result looks favorable.
