# Research log: Jev ranking

Access date: 2026-10-13. Scope: pointwise Score versus pairwise Choice for English passage ranking, aggregation assumptions, robustness, practical cost, and skill guidance. Include primary research and provider/data-owner contracts; exclude generic judge leaderboards, imitation training, production deployments, and claims based only on model confidence. Preserve negative evidence.

## Search history and source decisions

| Search or discovery route | Retained evidence | Decision |
|---|---|---|
| User's linked tweet; browser read after web fetch returned 403 | S1 practitioner hypothesis | Hypothesis only; no benchmark claim |
| Provider live documentation index, then HTML API/model/Score pages | S2–S5 | Current contract and known limitations; several Markdown pages inaccessible |
| Pairwise ranking prompting + Qin 2023 | S6 | Full primary paper; separates ranking methods and order reversal |
| Citation/topic follow-up: consolidation of ranking and relevance | S7 | Counterweight to treating relative rank scores as absolute relevance |
| Setwise ranking cost/effectiveness comparison | S8 | Efficiency tradeoffs and alternative schedules; no Jev transfer claim |
| Bradley–Terry original paper and implementation literature | S9–S10 | Original publisher metadata accessible, full original paper paywalled; JSS primary implementation article abstract accessible, PDF fetch failed |
| Pairwise preferences, intransitivity, bias | S11–S12 | Recent preprints; diagnostics are not correctness, single latent ordering may be misspecified |
| Dataset discovery: TREC DL2019/2020 public passages and qrels | S13–S16 | Official candidate files and checksum-verified qrels, versioned HF mirror |

Generic Wikipedia, aggregators, Reddit, and commercial paper summaries were discovery results only and not retained as technical evidence. Distillation papers were excluded because the question concerns runtime ranking, not training a replacement. The full Bradley–Terry original is inaccessible; cite it for historical attribution only, with practical fitting claims grounded in accessible primary implementation literature and our tested implementation.

## Durable source and claim records

S1 https://x.com/dotpem/status/2109474543249264878 — Nathan LeClaire, 2026-10-11. Practitioner suggestion to compare pairwise Choice with Score sorting, using Bradley–Terry. No dataset, prompts, metrics, costs, or outcome counts supplied. Evidence strength: weak for superiority, useful for hypothesis formation. Claims: C1.

S2 https://docs.typesafe.ai/api — TypeSafe HTTP API. Typed request/response fields, per-question answer IDs, returned model identity and token usage. Question IDs do not supply judgment meaning. Choice returns a selected option and distribution. Evidence strength: authoritative contract, not independent quality evidence. Claims: C2.

S3 https://docs.typesafe.ai/models — TypeSafe model page. Current versioned ID jev-1.13.0, moving aliases, input-token pricing $0.042/M and free output tokens, context limits, dynamic rate limits. Returned identity permits drift checks. GET models lists aliases; versioned IDs remain accepted. Account-specific invoice not observed. Claims: C3.

S4 https://docs.typesafe.ai/primitives/score — TypeSafe Score guide. Descriptive independently assessed levels; numbers or neighboring-level references are poor criteria. Score is a weighted position on the level index scale; different distributions can share that mean. Neither confidence nor shape implies correctness. This supports a strong descriptive-rubric control, not a guarantee that Score is calibrated to human relevance. Claims: C4.

S5 https://docs.typesafe.ai/model-jaggedness/jev-1.13 — TypeSafe limitations. Irrelevant state, indirect instructions, adversarial content, and first-option bias can affect judgments. Named state fields, aligned criteria, minimized inputs, and option-order tests are useful mitigations. Vendor disclosures do not quantify our workload's risk. Claims: C5.

S6 https://arxiv.org/html/2306.17563v2 — Qin et al., pairwise ranking prompting. Experiments support pairwise ranking for the studied generative models and retrieval tasks. Their all-pairs method swaps pair order, then aggregates wins and half-wins; sorting/sliding variants reduce work with different ordering sensitivity. Exhaustive comparisons cost quadratically. The paper does not test Jev, its Score primitive, or our regularized Bradley–Terry estimator. Claims: C6, C7.

S7 https://arxiv.org/html/2404.11791v1 — Yan et al., ranking/relevance consolidation. Pairwise-derived ranks can rank well while poorly matching absolute relevance labels. The study combines pointwise ratings and ranking constraints. Its cross-validation and model/task setup differ from our untouched query holdout. Treat as evidence for separating relative order and label calibration, not justification for adding an untested hybrid. Claims: C8.

S8 https://arxiv.org/html/2310.09497v2 — Zhuang et al., setwise ranking. A consistent comparison shows ranking effectiveness and efficiency depend on method and backbone; setwise and pairwise schedules have different cost/quality tradeoffs. Authors disclose possible benchmark contamination. Their generative-model costs do not predict Jev billing or latency. Claims: C9.

S9 https://academic.oup.com/biomet/article-abstract/39/3-4/324/326091 — Bradley and Terry, 1952. Publisher metadata confirms original paired-comparison paper, DOI 10.1093/biomet/39.3-4.324. Original full text inaccessible; no full-text methodological claims extracted. Claims: historical attribution only.

S10 https://www.jstatsoft.org/article/view/v048i09 — Turner and Firth, 2012. Primary software-method article describes Bradley–Terry fitting, order/contest effects, bias-reduced estimation, and residual diagnostics. Our L2 penalty is a study design choice, not their bias-reduced method. Claims: C10.

S11 https://arxiv.org/html/2609.37577v1 — Brocai and Becker, 2026 preprint. Inconsistency and pair agreement depend on item difficulty; aggregate consistency measures may not track human ranking accuracy. Simulation and human-rated text corpora motivate reporting errors by independently labeled gap. This is not Jev passage-relevance evidence; graded relevance gaps are a coarse proxy, not latent strength estimates. Claims: C11.

S12 https://arxiv.org/html/2609.22170v1 — Chawla et al., 2026 preprint. Multiple latent-ordering models can improve held-out prediction of model preferences. Authors note unseparated correlated noise and lack of independent component validation. A single latent-worth fit may conceal structure; fitted ranking is not evidence that preferences are coherent or true. Claims: C12.

S13 https://trec.nist.gov/data/deep2019.html and https://trec.nist.gov/data/deep2020.html — NIST passage labels distinguish 0 unrelated, 1 related without an answer, 2 highly relevant, 3 perfect. For binary relevance, grades 2–3 count as relevant. Graded nDCG retains all grades. Direct shell qrels download returned 403; the ir-datasets mirror supplied files matching published MD5s, and all HF qrels pairs/grades exactly matched. Claims: C13.

S14 https://microsoft.github.io/msmarco/TREC-Deep-Learning-2019 and https://microsoft.github.io/msmarco/TREC-Deep-Learning-2020 — Track-owner candidate files contain query IDs, passage IDs, query text, and passage text. Published gzip MD5s match local files. Candidate-file order has no supplied score column; call it provided order rather than a reproduced BM25 ranking. No unjudged passages become negatives. Claims: C14.

S15 https://github.com/microsoft/msmarco/blob/master/README.md — Dataset intended for non-commercial research. This is an offline research study; do not publish corpus/passages or use this as a commercial deployment license. Retain IDs, hashes, aggregate observations and retrieval instructions in public artifacts. Claims: C15.

S16 https://huggingface.co/datasets/whybe-choi/trec-dl-2019/tree/245ccf2c238433ea09e99d3c8daf622b5986fb5d and https://huggingface.co/datasets/whybe-choi/trec-dl-2020/tree/b37064dea006afb1651a76beaa2fa245d0a1d22b — Versioned mirror. Inspection initially mistook qrels row count for corpus size, resulting in two 3.43GB downloads. Downloads completed; no inference used those full-corpus files. Authoritative candidate files contain needed text. Preserve download hashes and mistake; do not describe the mirror itself as a data-owner source. Claims: C16.

## Claim ledger and synthesis links

| Claim | Direction / design effect | Evidence |
|---|---|---|
| C1 | Test a hypothesis, not a vendor tip as fact | S1 |
| C2–C5 | Pin identity; explicit state paths; strong Score rubric; order and hostile-text diagnostics | S2–S5, qualification-call.json |
| C6–C7 | Pairwise ranking is plausible; schedules and symmetry matter; include win totals | S6 |
| C8 | Keep relevance eligibility separate from ranking | S7, S13 |
| C9 | Compare full ranking costs, not request count alone | S8, token ledger |
| C10 | Check graph connectivity, separation, convergence; disclose L2 penalty | S10, test_experiment.py |
| C11 | Slice diagnostics by independent relevance gap; report ranking correctness separately | S11 |
| C12 | Cycles are observable; a latent-worth model can be misspecified | S12 |
| C13–C16 | Use independently labeled, versioned data; document sampling, rights and exclusions | dataset-audit.json, downloads.json |

## Protocol deviations and terminal evidence

- Planning target 100 final groups is infeasible in DL2019/2020: 97 judged queries; one has fewer than eight usable candidate-file passages, yielding 96 eligible. Observable near-duplicate/shared-ID grouping gives 96 clusters; unknown source families remain a limitation.
- Original pilot halted after 16 requests because Score 1.54 differed from the mean of displayed probabilities (1.53). The original tolerance was too strict for two-decimal serialized values. Preserve `development-registration.json`, `cases-v1.json`, `calls-development/`, and original partial outcome without regrading.
- v2 records a rounding-aware mathematical tolerance before fresh unused cases: probability sums ±0.005 per option; weighted Score error ±0.005 plus ±0.005 times sum of level indices. No values are normalized. The exposed query is quarantined; one previously unused query joins the development set, leaving 12 fresh pilot queries and 83 final queries.
- Account-specific billing is unavailable. Record token costs at verified public standard pricing as estimates; bound calls with conservative UTF-8-byte-plus-overhead reservations, and stop if observed token usage exceeds reservation. Do not claim observed invoice costs. Magnus authorized Jev use; no separate model-labeling or production calls are included.

The final synthesis will link the completed freeze, outcomes, cost ledger, diagnostics, and readout. Every retained source above has extracted claims and limitations. No required evidence is left solely in chat.
