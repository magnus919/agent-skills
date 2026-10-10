# Fair six-skill evaluation pilot

Five randomized exploratory baseline-versus-candidate Luna pairs and one separate non-randomized System One setup/parity smoke are complete. An agent reviewer assessed the five A/B packets against frozen source-grounded criteria. The blind process is supported by the packet's instructions and the reviewer's later attestation, not by an access audit. The review artifact names `gpt-6-sol`, but reviewer identity, model, and reasoning effort cannot be independently verified from persisted runtime metadata; those provenance fields were not recorded. The outputs show case-specific differences, but they do not establish causal or statistical uplift, human-grounded quality, or behavioral coverage across this repository. Raleigh was restricted to offline query-plan prose; no live query ran and no records were retrieved. The separate Jev qualification screen is a different lane. The frozen [`fair-skill-evaluation-pilot-v1.json`](fair-skill-evaluation-pilot-v1.json) remains the pre-dispatch plan; its `live_calls` fields are historical metadata, not the current Jev ledger. Full task outputs, tool traces, arm hashes, blinded packets, decoding key, and review record are retained in the task-side report directory rather than this repository.


## Frozen comparison design


The primary comparison is `pinned_skill_vs_skill` with `complete_package`. Both skill roots must be clean Git snapshots at the declared full revisions. The paired runner verifies both snapshot identities, resolves each arm's references only from that arm, and preflights both context hashes before any adapter call. Candidate and historical source maps cover all six case IDs:


- [`fair-skill-evaluation-candidate-references-v1.json`](fair-skill-evaluation-candidate-references-v1.json)
- [`fair-skill-evaluation-baseline-references-v1.json`](fair-skill-evaluation-baseline-references-v1.json)


Pass both maps with `--candidate-reference-map` and `--baseline-reference-map`. A map may contain other pilot case IDs when running one selected case; each selected candidate case must have an entry. A reference path and hash must match bytes in that arm's pinned snapshot. Expected outcomes, prohibited behavior, required evidence, and oracle labels stay out of generation payloads. `instruction_only` remains a separate diagnostic; `skill_vs_no_skill` is not the primary comparison.


| Skill and case | Oracle | Baseline revision | Candidate revision |
| --- | --- | --- | --- |
| `product-design-and-ux/embedded-loan-recovery` | State-transition matrix | `6384b6c1e327022b373f05b560974e2611cbd6a1` | `20ff7c0beb8241f085383927a567d36a0bccd040` |
| `pydanticai/non-chat-proposal` | Typed-proposal boundary | `6384b6c1e327022b373f05b560974e2611cbd6a1` | `20ff7c0beb8241f085383927a567d36a0bccd040` |
| `spec-driven-development/policy-translation-fidelity` | Clause-derived decision table | `6384b6c1e327022b373f05b560974e2611cbd6a1` | `20ff7c0beb8241f085383927a567d36a0bccd040` |
| `product-discovery/stakeholder-map` | Stakeholder-coverage matrix | `47a44d07166b47d8754e535de23526e268b0c994` | `20ff7c0beb8241f085383927a567d36a0bccd040` |
| `raleigh/fire-report-arcgis-first` | Deterministic fixture | `3eb7bd4096a8b3d2f7f3a27f52b2b617fd8a6b31` | `20ff7c0beb8241f085383927a567d36a0bccd040` |
| `system-one/selective-judge-confident-unsupported` | Judge-qualification facts | `6384b6c1e327022b373f05b560974e2611cbd6a1` | `20ff7c0beb8241f085383927a567d36a0bccd040` |The v2 evidence contract [`eval_runner/fair-pilot-evidence-contracts-v2.json`](../eval_runner/fair-pilot-evidence-contracts-v2.json) binds the task prompt, arm revisions and references, expected outcomes, prohibited behavior, required evidence, and source-grounded review criteria. Those criteria are not executable or usability oracles by themselves. The policy recipe fixture transcribes brief fictional prose supplied in the synthetic task; it was not independently prepared or policy-owner-approved. The task did not supply an authoritative clause document, clause IDs, owner approval, or independent fixtures; those remain unavailable validation inputs.


## Codex/Luna exploratory generation and review


Each of the five planned pairs used fresh projectless tasks, the same task and wrapper within a pair, a 1,200-word limit, requested `gpt-6-luna` at `xhigh`, and no worker tools. Arm order was randomized from the frozen seed. All ten generations completed without retries, model errors, authorization denials, or observed worker tool calls. The separate System One setup/parity smoke was candidate-then-baseline and is not included in the randomized comparison. Jev usage did not change during these Luna generations.


The reviewer was instructed to assess opaque A/B packets before opening the decoding key and later attested that it read only the packet and did not read the key before submitting judgments. No key-access audit or persisted reviewer task/thread/turn metadata is available, so this sequence and the reviewer's claimed Sol identity cannot be independently verified. These are agent-reviewed qualitative labels against frozen criteria, not a numeric score or human ground truth.

After unblinding, two aggregate labels were corrected from `Met` to `Partial` (the PydanticAI candidate and stakeholder-map candidate), and the SDD policy rationale was corrected to reflect the candidate's stated date boundary and unavailable precedence. The table below is that corrected crosswalk. These post-unblinding edits preserve the correction trail in the task-side report; they are not a second blind adjudication.


| Case | Candidate | Baseline | Observed distinction |
| --- | --- | --- | --- |
| `product-design-and-ux/embedded-loan-recovery` | Met | Partial | Candidate covered editable revision-bound approval, permission recheck, command timeout reconciliation, and separate side effects. The baseline omitted revision binding and same-command timeout handling. |
| `pydanticai/non-chat-proposal` | Partial | Partial | Candidate included scoped evidence-ID and execution-boundary checks; explicit failure-to-review behavior and routing to owner skills were not shown. |
| `spec-driven-development/policy-translation-fidelity` | Partial | Not met | Candidate stated the June 30/July 1 boundary and unavailable-before-exception precedence, and requested validation against an authoritative clause document and independent fixtures. The synthetic task supplied only brief prose clauses; it did not supply an authoritative clause document, clause IDs, owner approval, or independent fixtures. Its `Partial` reflects missing explicit below/equal/above threshold, boundary, conflict, and missing-input test rows plus concrete controlled-release/rollback details; those unavailable source and approval artifacts remain external validation inputs, not omissions to remedy by invention. Baseline could approve an in-limit exception before review, contrary to the source clause that exceptions need review. Its invalid-duration handling also missed the added frozen review criterion, which the original task prose did not specify. |
| `product-discovery/stakeholder-map` | Partial | Partial | Candidate covered the required role types and separated hypotheses from observations, but per-role needs, conflicts, inclusion rationale, and adoption blockers remained incomplete. |
| `raleigh/fire-report-arcgis-first` | Met | Met | Both respected source/lag and fallback limits and stated no query ran. Candidate made the successful-empty condition for fallback more explicit. This was query-plan-only. |


The task did not expose sampling parameters or provider-returned runtime settings, so this is not a strictly controlled causal experiment. Small sample size, agent review with unverified reviewer provenance, no usability observations, no code execution, and no live retrieval constrain the result. The first System One smoke was a procedural control, not an improvement probe. Do not generalize these outputs to the whole catalog or use them as release evidence.


The frozen protocol, generation results, blinded-review report, post-unblinding correction, and corrected case crosswalk are preserved in the task-side report directory as `fair-pilot-remaining-five-protocol-2026-10-10.md`, `fair-pilot-luna-generation-results-2026-10-10.json`, `fair-pilot-blind-review-sol-2026-10-10.md`, `fair-pilot-review-correction-2026-10-10.md`, and `fair-pilot-unblinded-review-2026-10-10.json`. These task-side records contain output text and identifiers; they are not linked as repository files.


## Separate Jev qualification screen


The [qualification dossier](fair-skill-evaluation-qualification-v1.json) froze 12 Jev request cases: seven development and five held-out. The same-assertion discovery paraphrase pair is development-only and is one invariance diagnostic, not two independent observations. It includes positive, negative, contradictory, and missing-evidence examples. Three cases are bounded excerpts from prior generated outputs; nine are authored controls. Authored controls are not production outputs.


Jev run `38021806973` attempted and validated 12 requests, with no request errors or unattempted cases. It consumed 12 of the shared 100-attempt budget, leaving 88 at the time of review. No further Jev calls were made after that screen; the separate Luna smoke used two Codex tasks and no Jev calls. The frozen dossier's labels remain marked `pending_independent_agent_review`; the separate [adjudication companion](fair-skill-evaluation-adjudication-run-38021806973-v1.json) preserves the dossier bytes and records Sol's independent review at commit `e37f841d04875d9e05380cb125bfee3eb64f98be`.


Sol verified all 12 request and question hashes, split assignments, frozen dossier/contract pins, model identity, and serial order. Exact label agreement was 11/12. No contradictory or missing-evidence case received a false `met`. `dev-pydantic-authority-omission` remains independently labeled `not_met` because current authority and revision checks were omitted; Jev returned `not_shown` at 0.93. The discovery paraphrase pair stayed `met/met` and is dependent. This is a bounded advisory screen, not human ground truth, a calibrated accuracy estimate, or release qualification. Keep the labels and held-out set frozen; do not tune against the mismatch or spend additional calls on this screen.


The guarded main-only [Jev frozen qualification workflow](../.github/workflows/jev-frozen-qualification.yml) was dispatched for this screen with a one-time durable claim. Its sanitized result artifact preserves request hashes, numeric verdict fields, counts, and error categories, never request/response text or secrets. The workflow is advisory and does not run generation, tune between splits, or create a release gate.


## Offline policy mutation checks


Run the production-shaped policy CLI oracle and bounded mutation suite offline:


```sh
python3 -m eval_runner.fair_pilot_mutations --json
python3 -m pytest eval_runner/tests/test_fair_pilot_increment_three.py eval_runner/tests/test_fair_pairing.py eval_runner/tests/test_evidence_contract.py
```


The suite sends eight production-shaped JSON inputs through `spec-driven-development/scripts/business_policy.py`. It separately reports valid behavioral defects, equivalent comparison, deliberately invalid mutation, controlled runtime/infrastructure error, and checks that still require conceptual review. Gap and overlap cases exercise the evaluator with custom version intervals. Passing means only that these specific oracle fixtures distinguish those mutations; it does not establish policy correctness.


## Staged ledger


The task-side testing-strategy refit ledger groups this work into six stages. The eight rows below are a status crosswalk that separates overlapping implementation, inventory, and effectiveness work; they do not replace that ledger's history.


| Workstream | Original ledger stage | Status and evidence |
| --- | --- | --- |
| Truthful result semantics | 1 | Merged in PR #686. Execution, evidence completeness, semantic verdict, and comparison outcomes are distinct; release evidence has separate requirements. |
| Case/evidence contracts and selector coverage | 2 | Supporting changes merged across PRs #687–#689. Pinned arm maps, source contracts, and deepest-skill nested selection are available; this increment reports their coverage and limitations. |
| Risk-representative pilot | 3 | Six cases and source revisions are frozen in the table above. The separate 12-request Jev screen is complete. Five randomized exploratory pairs and one non-randomized setup/parity smoke completed; an agent reviewed the five A/B packets under blinding instructions and later attested it did not access the key before submitting judgments. Reviewer identity and model/effort provenance are not independently verified. |
| Deterministic mutation qualification | 4 | Partial: targeted policy CLI mutations have offline fixtures and reports. There is no broad native mutation campaign, and those fixtures do not prove policy-owner fidelity. |
| Source-aware Jev qualification | 5 | Bounded screen completed and independently reviewed by Sol: 12 requests, 11 exact label matches, zero false `met` on contradictory/missing-evidence cases. This is not human ground truth or calibration. |
| Fair comparison harness and proportional CI | 6 | Pinned comparison support and CI checks are merged. Five randomized exploratory pairs and one separate setup/parity smoke completed; outcomes were reviewed qualitatively against frozen criteria. This is not evidence of a causal effect. |
| Repository evidence and test-route inventory | Cross-cutting 2/6 | Added in this increment: separate evidence counts, curated-register validation, nested-manifest reporting, and test selector routes. The 61 unclassified test-like paths need route review; they are not proven skipped tests. |
| Effectiveness confirmation | 6 | Not established. The five-pair agent review is qualitative, with unverified reviewer provenance; it is not human ground truth or a statistical estimate. Broader held-out evidence, repeated comparisons, human adjudication, usability research, code/runtime checks, and Raleigh retrieval evidence remain absent. |

## Risk-ranked migration backlog

The pilot supports targeted follow-up questions, not a broad new skill. Priorities below rank the potential consequence of an ambiguous or incorrectly authorized decision; they are not severity estimates from production incidents.

| Priority | Follow-up | Evidence and bounded next step |
| --- | --- | --- |
| P0 | Policy versioning, precedence, and exception routing | Candidate stated the June 30/July 1 boundary and unavailable-before-exception precedence, and requested validation against an authoritative clause document and independent fixtures. The synthetic task supplied only brief prose clauses; it did not supply an authoritative clause document, clause IDs, owner approval, or independent fixtures. Its `Partial` reflects absent below/equal/above threshold, boundary, conflict, and missing-input test rows and concrete controlled-release/rollback details; those unavailable source and approval artifacts remain external validation inputs. Baseline could approve an in-limit exception before review, contrary to the source clause. Its invalid-duration handling missed an added frozen criterion, not a requirement stated in the original task prose. Next, obtain the authoritative clauses and owner approval, independently prepare fixtures, and add those test rows and release/rollback controls. |
| P0 | Runtime authority and stale-state behavior | The PydanticAI candidate did not show explicit block-and-return-to-review behavior after revocation or revision mismatch; neither response routed follow-up work to owner skills. Keep proposals typed and application-owned, validate evidence IDs, bind approval to current revision and policy version, recheck authority at execution, and verify this in an executable isolated harness before claiming runtime behavior. |
| P1 | Embedded-agent recovery and partial failure | The baseline omitted revision binding and same-command timeout reconciliation. Preserve editable proposals, invalidate approval after edits, query the original command/idempotency status after timeout, and keep reservation confirmation independent from notification success. Test state transitions in a prototype; gather user research before usability claims. |
| P1 | Stakeholder completeness | The baseline gave an incomplete generic role map; the candidate still lacked fully specified per-role needs, conflicts, inclusion rationale, and adoption blockers. Require those fields for each billing, end-user, operator, downstream-data, and integration role, and keep unverified assumptions distinct from interview evidence. |
| P2 | Raleigh retrieval evidence | Both outputs were offline query plans. Test source/lag filters and fallback only after a successful exact query returns empty; exercise error and stale-data cases in a controlled fixture or authorized live-query harness before claiming retrieval quality. |
| P2 | Comparison strength | Five exploratory pairs and one procedural smoke cannot establish uplift. Any future efficacy claim needs a new held-out design, predeclared criteria, verified task/context parity, blinded independent human adjudication, enough repetitions for the intended claim, and separate runtime/usability evidence. |

No further Luna or Jev calls are implied by this report. Release gating remains out of scope until independently reviewed held-out evidence, error/abstention analysis, repeatability, and a separate versioned release-gate contract justify it. This refit is not complete.
