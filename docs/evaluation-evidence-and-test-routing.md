# Evaluation evidence and test routing

The repository has several useful evidence sources, but each answers a different question. `python3 scripts/validate-case-checklist.py` checks the curated review register and prints a current inventory; `--json` emits the same report for automation. Passing this structural check does not establish that a skill behaves correctly.

## Evidence lanes

The inventory snapshot below was taken on 2026-10-10. Rerun the command for current counts.

| Evidence | Snapshot | What it supports |
| --- | ---: | --- |
| Canonical manifests | 183 manifests, 1,458 cases; 10 nested manifests with 59 cases | Manifest discovery and schema/oracle syntax inventory, not behavioral quality |
| Assertion syntax | 278 exact assertions, 6,447 prose assertions; 1,409 cases contain prose or unresolved assertions | Syntax triage only; prose assertions still need an appropriate independent oracle |
| Curated review register | 1,096 rows; 362 cases have no row | A row's recorded reviewer and verdict fields; legacy values do not establish independent or human review |
| Stored lifecycle runs | 98 completed records, all using the fake adapter | Execution and serialization only, not live model behavior or semantic verification |
| Independent adjudication companion | 12 labels, 11 exact Jev matches, valid content hash | A bounded advisory screen; not human ground truth, calibrated accuracy, or release qualification |
| Repository-wide behavioral verification | Not assessed | No repository contract currently maps every case to independently verified behavioral evidence |

The legacy register records 1,088 rows as `reviewed` by `eval-coverage-worker` and eight as `author-reviewed; human review pending`. Those values are retained as records, not promoted to provenance claims. The separate [adjudication companion](fair-skill-evaluation-adjudication-run-38021806973-v1.json) records the completed Sol review of Jev run 38021806973 without changing the frozen dossier. The run had one label mismatch: `dev-pydantic-authority-omission` was independently labeled `not_met` because current authority and revision checks were omitted; Jev returned `not_shown`. No contradictory or missing-evidence case received a false `met`. The discovery paraphrase pair is dependent and counts as one invariance diagnostic. The screen consumed 12 of 100 budgeted attempts; 88 remained at the time of review. No follow-up calls were made. These results are evidence for review, not a probability estimate.

The checklist is a curated review register, not a row-for-every-case mirror. The old exact-mirror validator made a missing row an error, and a bulk generator would have filled omissions with inferred prompts and review metadata. That would turn an absence of review into a false appearance of review. The validator now permits omissions, rejects malformed, duplicate, or orphan rows, and checks the independent adjudication hash plus its pinned dossier and evidence-contract hashes. The generator reports omissions by default; `--add-case SKILL_PATH/CASE_ID` adds only that explicitly selected case as `pending`, with reviewer `unassigned` and no review date or verdict.

## Manifest and test selection

The paired-eval selector discovers nested skill manifests and attributes changed paths to the deepest real skill root. It fails closed when the selected skill count exceeds the five-skill cap rather than silently truncating. The regression coverage is in [`eval_runner/tests/test_selection.py`](../eval_runner/tests/test_selection.py).

The test-source routing snapshot found 153 source files with test-like names. Declared routes cover 92: 21 through the core manifest, 50 through skill-local Python auto-discovery, 10 registered skill shell tests run in CI, three registered manual shell tests, two integration tests, five paths explicitly named by workflows, and one test under a workflow's `unittest discover -s` directory. The remaining 61 are unclassified by those selectors. This is an audit queue, not proof that those tests are never run: package-specific CI, local scripts, or indirect orchestration may execute them. Confirm each route before changing CI. The inventory parses both assigned and annotated shell-test registry declarations.

Core tests are shared through [`scripts/core-test-files.txt`](../scripts/core-test-files.txt), consumed by both `Makefile` and the validation workflow. Skill-local Python tests must use `scripts/test_*.py` for pytest discovery; shell tests belong in [`scripts/check-skill-tests.py`](../scripts/check-skill-tests.py) as either `RUN_TESTS` or `MANUAL_TESTS`. The inventory's unclassified list should be used to identify missing route documentation or a real coverage gap, not to bulk-add tests to a single CI job.

## Triage and follow-up

Prioritize oracle work by behavioral risk and whether a deterministic boundary exists. Start with policy translation and effective-date/version precedence, authority and permission rechecks at execution time, evidence completeness and contradiction handling, and exact structured outputs. Keep source-derived fixtures independent from the implementation they assess. Test positive behavior, explicit violations, missing evidence, conflicts, invalid input, boundary dates, and infrastructure failure separately. Conceptual UX and prose outcomes still need review by a qualified person; a synthetic state-transition harness does not establish usability.

For each proposed oracle, document the trusted source, the fact or transition being checked, the satisfying case, a plausible contradiction, and an omission case. If the oracle cannot distinguish those outcomes, refine the assertion or leave it unresolved instead of treating a keyword match as semantic verification. Keep code-mutation results separate from semantic output probes, and report equivalent, invalid, surviving, and infrastructure-error cases distinctly.

Before broadening CI, route the unclassified sources to their owning package or workflow and make the command discoverable. Keep deterministic PR checks offline and proportional. Any live generation or judging run needs pinned sources, identical task and wrapper settings across comparison arms, frozen cases, explicit per-run budget allocation, and independently reviewed outputs. A green check that skipped a live job is not live evidence.
