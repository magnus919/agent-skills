# Regression Detection — Lifecycle Evaluation Corpus

This document defines how to detect and interpret a regression in the lifecycle evaluation
corpus across revisions, and how to tell a real regression from a benign content change.

## What counts as a regression

A corpus regression is any change that silently reduces the corpus's ability to exercise
its required coverage or that invalidates durable evidence references. Concretely:

1. **Case removal or renaming.** Eval case IDs are **durable evidence references**
   (VAL-EVL-005, VAL-CRP-024). Removing a case, or renaming an ID, breaks the mapping in
   `references/coverage-index.json`, any committed run artifacts that reference the ID, and
   any downstream evidence that cites the ID. Never rename an ID; add a new case with a new
   ID instead.
2. **Behavioral-category or integrated-scenario coverage loss.** Removing the last case
   tagged for a behavioral category or integrated scenario makes the corpus fail its
   mandatory coverage (VAL-CRP-003..008, VAL-CRP-010..015). The machine-checkable gate is
   `validate-corpus-coverage.py`, which fails when any of the 5 categories or 6 scenarios
   has no tagged case.
3. **Assertion-set drift on a tagged case.** If a case's assertions no longer verify the
   category's required handling (e.g., a stop/retire case stops asserting the accountable
   owner, or a handoff assertion is dropped from an integrated case), the corpus silently
   loses the guarantee that the category/scenario is *actually* exercised. The committed
   run artifacts pin the assertion sets at snapshot time; a re-run that changes assertion
   sets is a signal to review.
4. **Fixture-hash changes.** Every per-trial manifest records `case.prompt_hash` and
   `case.fixture_hashes`. A change to a prompt or to a referenced fixture changes those
   hashes. For self-contained cases (inputs inline in prompts) a prompt change is a
   deliberate content change that should be reviewed against the case's tag; a fixture
   change on a `files`-referencing case changes the fixture hash and must be reconciled
   with `references/sources.md` and the repository fixture-resolution validator
   (`validate-evals.py`).

## Comparison procedure (re-run with the fake adapter)

The corpus is deterministic under the fake adapter (no model, no network, no randomness in
execution — only timestamps and trial UUIDs vary). To compare two revisions:

```sh
# On the old revision (e.g., the merged baseline):
git worktree add /tmp/corpus-old <old-sha>
cd /tmp/corpus-old && bash lifecycle-evals/scripts/run-corpus.sh   # CORPUS_OUT_DIR=/tmp/corpus-runs-old

# On the new revision (the candidate):
cd /Volumes/tank01/magnus/git/agent-skills-issue-204
CORPUS_OUT_DIR=/tmp/corpus-runs-new bash lifecycle-evals/scripts/run-corpus.sh
```

Then compare per case:

1. **Per-case status**: every trial must be `status == "completed"` in both runs (a trial
   that becomes `error`/`timeout`/`stopped` between revisions is a regression).
2. **Per-case identity**: the set of `case_id`s per manifest must be equal between
   revisions (no removals, no renames).
3. **Per-case content**: compare `case.prompt_hash` and the `case.fixture_hashes` fields in
   the per-trial manifests. Changed hashes indicate the case content or fixture changed and
   must be reviewed (see interpretation below).
4. **Coverage**: run `validate-corpus-coverage.py` on the candidate; it must exit 0 (all 5
   categories, all 6 scenarios covered, every referenced ID present, index current).

A simple diff-oriented check across the two output trees:

```sh
diff <(cd /tmp/corpus-runs-old && find . -name '*.manifest.json' | sort) \
     <(cd /tmp/corpus-runs-new && find . -name '*.manifest.json' | sort)
```

Note that file names embed the trial UUID prefix (`<case_id>--<trial_id[:8]>.manifest.json`),
so compare by `case_id` sets and by hashes rather than by file name.

## Case-ID stability rule

**Never rename an eval case ID.** IDs are referenced by the coverage index, the coverage
matrix, committed run artifacts, and (potentially) external evidence ledgers. Renaming an
ID is a regression even when the content is unchanged. To evolve a case: keep the ID, update
content, regenerate the index, re-run the corpus, and refresh the run-artifact snapshot at
merge time. To add coverage: add a new case with a new lowercase-hyphen ID (≤ 64 chars,
unique within its manifest).

## Ratchet command

The repository's eval-coverage ratchet must hold on every corpus change:

```sh
.venv/bin/python scripts/eval-coverage.py --modified-from origin/main
```

This exits 0 only when no modified skill lacks a schema-valid manifest and coverage does
not decrease versus the base. All 17 corpus manifests are schema-valid, so corpus changes
never trip the modified-skill ratchet; the check still runs in CI on every PR.

Fixture-resolution is enforced by the repository validator:

```sh
.venv/bin/python scripts/validate-evals.py
```

## Interpreting a change: regression vs. benign content change

| Observation | Classification | Required action |
|---|---|---|
| A case ID disappears from a manifest | **Regression** | Restore the case or (if truly obsolete) re-scope: add a replacement case, update the index and matrix, re-run, and record the replacement in the PR body; never silently drop the ID. |
| A case ID is renamed | **Regression** | Revert the rename; change content only, or add a new ID. |
| The last case for a category/scenario is removed or untagged | **Regression** | `validate-corpus-coverage.py` fails; restore coverage before merging. |
| A prompt/assertion is edited to tighten wording without changing the scenario or the category-required handling | **Benign content change** | Update the run-artifact snapshot at merge time (one snapshot per merge, VAL-CRP-021 ambiguity C); no re-review of category coverage needed beyond `validate-corpus-coverage.py`. |
| A prompt is changed so the case now exercises a different scenario, or a category-required assertion is dropped | **Material content change** | Re-tag the case in the coverage index, regenerate the matrix and index, re-run the corpus, and re-verify the case still satisfies its category's required handling. |
| A `files` fixture changes | **Material content change** | Update `references/sources.md` (provenance), re-run, and confirm `validate-evals.py` still resolves the fixture. |
| Timestamps/UUIDs differ between fake runs | **Benign** | Expected; timestamps are the scoping/date evidence and are excluded from content comparison. |

In all cases, the decision is recorded in the change's PR body or evidence ledger so a
future reviewer can see why the corpus changed.

## Keeping the index and matrix current

After any case content, ID, or tag change:

```sh
.venv/bin/python lifecycle-evals/scripts/validate-corpus-coverage.py --write-index
# then regenerate the human-readable matrix from the index (see coverage-matrix.md header),
# re-run the corpus, and commit the run-artifact snapshot at merge time.
```
