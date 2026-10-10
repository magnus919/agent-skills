# Fair six-skill evaluation pilot

The six-case baseline-versus-candidate generation comparison remains `plan_only`. The separate Jev qualification screen has completed; do not confuse those two lanes. The frozen [`fair-skill-evaluation-pilot-v1.json`](fair-skill-evaluation-pilot-v1.json) is the pre-dispatch planning snapshot, so its `live_calls` fields are historical metadata rather than the current Jev ledger.

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
| `system-one/selective-judge-confident-unsupported` | Judge-qualification facts | `6384b6c1e327022b373f05b560974e2611cbd6a1` | `20ff7c0beb8241f085383927a567d36a0bccd040` |

The v2 evidence contract [`eval_runner/fair-pilot-evidence-contracts-v2.json`](../eval_runner/fair-pilot-evidence-contracts-v2.json) binds the task prompt, arm revisions and references, expected outcomes, prohibited behavior, required evidence, and source-grounded review criteria. Those criteria are not executable or usability oracles by themselves. The policy recipe has a separate clause-transcribed fixture; it is not policy-owner-approved fidelity evidence.

## Proposed Codex/Luna generation run

No generation was dispatched in this preparation. The concrete bounded plan is 12 one-shot Codex generations: one baseline and one candidate arm for each of the six rows above, using `gpt-6-luna` at the same reasoning effort. Each task gets the same user task and wrapper, the exact skill package and references pinned for that arm, and no judgment data. Randomize arm order per case, keep each arm isolated, save full outputs privately with source and prompt hashes, and do not retry failed or unsatisfactory responses. A separate blind `gpt-6-sol` review can then assess all 12 outputs against the frozen source-based criteria, with results reported by case and failure category.

This is a small diagnostic, not a statistically powered or strictly controlled causal study. Codex task creation exposes model and reasoning effort but not sampling parameters or output-token caps, and it does not guarantee a tool-free model surface. The dispatch protocol must check task settings and tool traces; if an arm invokes a tool or differs in task/context, invalidate that pair rather than interpreting the result. The separate Sol review is agent adjudication, not human ground truth. A credible claim of improvement still needs independently human-adjudicated outcomes and broader held-out evidence. There is no direct external API charge, but the 12 Luna generations and Sol review consume shared Codex usage; exact token or dollar cost is not available before dispatch. No Codex generations are authorized or performed by this preparation.

The six prompts, arm revisions, and reference maps are frozen for this proposal. Do not change assertions or use the held-out cases for tuning after outputs are observed. Any tuning requires a fresh held-out set. The six-case set is too small to generalize to the whole catalog.

## Separate Jev qualification screen

The [qualification dossier](fair-skill-evaluation-qualification-v1.json) froze 12 Jev request cases: seven development and five held-out. The same-assertion discovery paraphrase pair is development-only and is one invariance diagnostic, not two independent observations. It includes positive, negative, contradictory, and missing-evidence examples. Three cases are bounded excerpts from prior generated outputs; nine are authored controls. Authored controls are not production outputs.

Jev run `38021806973` attempted and validated 12 requests, with no request errors or unattempted cases. It consumed 12 of the shared 100-attempt budget, leaving 88 at the time of review. No further provider or Jev calls were made during this preparation. The frozen dossier's labels remain marked `pending_independent_agent_review`; the separate [adjudication companion](fair-skill-evaluation-adjudication-run-38021806973-v1.json) preserves the dossier bytes and records Sol's independent review at commit `e37f841d04875d9e05380cb125bfee3eb64f98be`.

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
| Risk-representative pilot | 3 | Six cases and source revisions are frozen in the table above. The separate 12-request Jev screen is complete. Baseline-versus-candidate skill generation has not run. |
| Deterministic mutation qualification | 4 | Partial: targeted policy CLI mutations have offline fixtures and reports. There is no broad native mutation campaign, and those fixtures do not prove policy-owner fidelity. |
| Source-aware Jev qualification | 5 | Bounded screen completed and independently reviewed by Sol: 12 requests, 11 exact label matches, zero false `met` on contradictory/missing-evidence cases. This is not human ground truth or calibration. |
| Fair comparison harness and proportional CI | 6 | Pinned comparison support and CI checks are merged. Matched old/new generations and reviewed comparison outcomes are still absent. |
| Repository evidence and test-route inventory | Cross-cutting 2/6 | Added in this increment: separate evidence counts, curated-register validation, nested-manifest reporting, and test selector routes. The 62 unclassified test-like paths need route review; they are not proven skipped tests. |
| Effectiveness confirmation | 6 | Not run. Requires human-adjudicated outcomes, verified dispatch parity and tool traces, an explicitly authorized frozen run, and review of the resulting outputs. |

For any next paired generation, first resolve the authority/policy boundary cases, review the positive/contradictory/omission labels independently, and confirm that Codex task settings and tool traces make the comparison fit the intended claim. The Codex/Luna proposal above remains undispatched. Keep migration planning limited to source-grounded defects in policy precedence/effective dates, execution-time permission and authority checks, evidence completeness, contradiction handling, and exact structured outputs. Do not create a broad agentic-apps or policy-to-code skill from this pilot.

Release gating remains out of scope until independently reviewed held-out evidence, error/abstention analysis, repeatability, and a separate versioned release-gate contract justify one. This refit is not complete.
