# Jev passage ranking: Score versus pairwise Choice

## Decision

Retain rubric-based Score as the starting point for this workload. Exhaustive
pairwise Choice did not meet the preregistered +0.03 nDCG@5 improvement threshold
and failed cost and latency guardrails. The cheaper sparse schedules lost quality.
This supports a bounded method guide, not a universal claim that Score is superior.
No production policy or relevance gate was deployed.

## Held-out results

The frozen study used Jev `jev-1.13.0`, eight passages per query, singleton
requests, concurrency two, and independent TREC passage relevance judgments.
There were 83 held-out queries; six zero-ideal-gain shortlists are excluded only
from nDCG, leaving 77 query units. All 83 remain in operational denominators.

| Method | Mean nDCG@5 | Difference from Score (95% paired bootstrap interval) | Input tokens / Score | p95 full ranking |
|---|---:|---|---:|---:|
| Score | 0.8732 | Control | 1.00× | 1.191 s |
| Exhaustive Choice + Bradley–Terry | 0.8801 | +0.0069 [-0.0131, +0.0271] | 4.03× | 3.354 s |
| Eight-edge cycle + Bradley–Terry | 0.7738 | -0.0994 [-0.1415, -0.0573] | 1.15× | 1.311 s |
| Seven-edge shortest-passage star + Bradley–Terry | 0.6895 | -0.1837 [-0.2379, -0.1297] | 0.96× | 1.116 s |

Provided candidate-file order scored 0.4534 nDCG@5 on the same 77 shortlists.
The exhaustive treatment gained 0.0069, with an interval spanning zero. Its
4.03× input tokens and 2.82× p95 latency exceeded the study's 1.25× and 2×
practical limits. The star actually used 0.957× Score tokens (pilot estimate
0.951×); its severe quality loss shows why a connected, cheap graph alone is
not enough. This result does not evaluate other sparse/adaptive schedules.

Top-1 best-grade hit rate was 72.3% for Score and 78.3% for exhaustive Choice,
including trivially successful all-zero cases. This is secondary descriptive
evidence, not grounds for switching the registered primary metric after results.
Useful top-1 rates and defined Kendall tau-b counts are in the supplemental
analysis. Binary usefulness means grade at least two; grade one is topical
without answering the query. Graded nDCG uses the registered exponential gains.

## Evidence strength and diagnostics

This is a **bounded exploratory screen**. The 12 fresh pilot queries yielded
11 defined nDCG differences. A normal approximation required 60 final groups
using the pilot SD, but 123 using its upper variance bound; only 83 were
available, and six had undefined nDCG. No equivalence, broad superiority,
calibrated confidence, or skill-behavior benefit is established.

Bradley–Terry and win totals produced identical complete rankings on all 83
exhaustive shortlists. The balanced complete graph explains this; do not credit
the fitter with an additional ranking gain. A 100-tournament offline check
found no ordering violations. Twenty-two shortlists had cycles; that count
alone does not establish ranking correctness or incorrectness.

On ten preselected held-out queries, exhaustive pair choices repeated on
273/280 edges and agreed after passage-position reversal on 263/280 edges.
Among grade-gap-three edges, both tests agreed on 32/32; small counts and
coarse grade gaps limit interpretation. Aggregate nDCG changed by +0.0006 on
repeat and -0.0085 on reversal. Only 5/10 repeated complete orders and 1/10
reversed orders were identical. Order stability and quality are separate.
For Score, the reversal variant is a second identical-input repeat, not an
option-order intervention. Criteria insertion order was tested separately in
synthetic fixtures; a larger combined symmetry treatment was not evaluated.

Eighteen held-out shortlists contained no grade-two-or-three passage. Pairwise
Choice still produces a relative winner; the study does not qualify an
absolute-relevance threshold. Separate synthetic diagnostics comprised 12
constructed groups: useful, all-irrelevant, tied and instruction-bearing
irrelevant passages. All-irrelevant groups scored zero throughout, yet binary
Choice selected options. The three hostile decoys did not outscore direct
answers; this small fixture set is not an injection defense qualification.
Duplicate-answer fixtures showed Score variation despite identical text.

## Protocol history and accounting

The first pilot stopped after 16 requests: a strict equality check rejected
Score 1.54 versus 1.53 reconstructed from rounded displayed probabilities.
Its failure is retained unchanged and was not retried or regraded. v2 registered
rounding-aware tolerances on fresh cases, quarantined the exposed query, and
kept the same prompts. Exact source snapshots were recovered and verified
against both original registration hashes. Final code and case bytes match
the completed freeze; the held-out protocol was not changed after outcomes.

The completed phases total **6,242 requests, 3,291,912 input tokens, and an
estimated $0.1383**, including the failed pilot and diagnostics. Prices use
TypeSafe's checked $0.042/M input tokens and free outputs; no account invoice
was observed. The budget was $20 and 8,000 attempts. Every request is retained
in a redacted response ledger; all held-out and diagnostic requests returned
the pinned identity and passed v2 validation. No automatic retries occurred.

## Sampling, provenance and limits

Official candidate gzip files matched the track's published MD5s. NIST labels
from a checksum-addressed ir-datasets mirror exactly matched all HF judgment
pairs and grades. One of 97 judged queries lacked eight distinct usable
candidate-file passages; 96 qualified. Development and final membership are
in the public case manifest; the first exposed case is terminal-v1.

Select the first eight distinct normalized, explicitly judged passages in the
provided candidate-file order without filtering by relevance grade. That order
contains no scores and is not a reproduced BM25 ranking. No unjudged passage
is assigned a negative label. All identifiable shared IDs/normalized and near-
duplicate text/query groups stay together, but missing URLs mean true source
families cannot be fully verified. Jev training overlap is unknown. Old public
benchmark data and small fully judged shortlists do not represent current
search traffic, full-corpus retrieval recall, other languages, larger lists,
batched requests or production end-to-end benefit.

The study is non-commercial research. Public artifacts omit corpus passages
and raw request states. They retain selected IDs, grades, text/query hashes,
exact request hashes and model responses; raw authorized requests and data
remain in the task's durable local evidence folder. The initial mirror lookup
mistook judgment row count for corpus size and downloaded duplicate full
corpora unnecessarily; this retrieval error is preserved in the research log.

## Evidence package and reproduction

| Artifact | Purpose |
|---|---|
| `initial-plan.md`, `freeze.json` | Draft, final registration, hypotheses, budgets, immutable identities |
| `development-registration*.json`, `source-recovery.json` | Distinct terminal and amended pilot provenance |
| `research-log.md` | Primary sources, extracted claims, contradictions, exclusions and limitations |
| `dataset-audit.json`, `downloads.json`, `cases-public.json` | Acquisition checksums, selection and split roster |
| `analysis-final.json`, `supplemental-analysis.json`, `cost-ledger.json` | Paired effects, denominators, guardrails, robustness and costs |
| `outcomes-*.jsonl`, `response-ledger-public.json.gz` | Derived rankings and every redacted paid response |
| `challenge-registration.json`, `challenge-results.json` | Separate synthetic expected-behavior evidence |
| `*.py.txt` | Exact research-source snapshots; reference material, not installed skill tools |
| `verify_evidence.py`, `evidence-manifest.json` | Offline roster, hash and metric verification |

Run `python3 docs/experiments/jev-ranking/verify_evidence.py` from the repository
root; it uses only the standard library and makes no API calls. It verifies
file hashes, freeze/source identity, assigned final and diagnostic rosters,
response integrity, budget accounting and independently recalculated nDCG.
It cannot verify omitted raw request bytes without the local source data, or
prove the original human judgments correct. Primary responses can be inspected
with `gzip -dc docs/experiments/jev-ranking/response-ledger-public.json.gz`.

For a new live reproduction, acquire the candidate files and qrels from the
source log, reconstruct the registered shortlist rule, independently qualify
the current API, register a new model/date/budget and preserve a fresh holdout.
The `.py.txt` snapshots document this historical execution and its key-file
convention; do not run them as a generic integration or silently reuse account
credentials. No additional calls are needed to inspect this evidence package.

## Enrichment decision

Add the ranking reference, explicit routing, and three stable-ID portable eval
cases with author-reviewed satisfying/contradictory/missing-evidence challenges.
The guidance teaches method selection, fair comparison, connected schedules,
aggregation limits, absolute-relevance separation and terminal failure handling.
Schema validity and offline author challenge review do not establish agent
behavioral uplift. Existing advisory CI call budgets and release-gate semantics
remain unchanged. Future work should investigate target-specific top-1 needs or
better sparse schedules only under a new registration and independent evidence.
