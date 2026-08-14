# Bounded Discovery Brief — Lifecycle Evaluation Corpus (#204)

This brief records the pre-implementation survey for issue #204 ("test: add lifecycle
evaluation corpus for new product and production skills") and the ownership/routing
decisions that bound the corpus layer. It is the corpus-level companion to the per-skill
discovery briefs committed by each milestone-4 skill/bundle (VAL-SKL-014).

## Surveyed surfaces

1. **`neckbeard/eval/`** — the reference evaluation harness pattern: versioned
   task schema (`task-schema.md`), rubric, baseline protocol, fixtures organized by scenario
   (spec-ambiguity, adversarial, no-change-needed, regression-prevention, feature-change,
   release-verification, review-finding, bug-diagnosis, trajectories, refactor), and a
   runner (`run_eval.py`). Contributed the conventions this corpus follows: scenario-scoped
   `expected_output`, adversarial/negative cases, and the claims-scoping sentence
   ("Claims are scoped to the harness, model, fixtures, and revision under test").
2. **`neckbeard/evals/evals.json`** — the reference manifest: 11 cases covering
   bug-fix reproduction, ambiguity, multi-surface routing, schema migration rollback,
   refactor characterization, docs-only reduced path, duplicate detection, material-change
   re-verification, release-authority block, and the lightweight test-hardening path. All
   cases use the canonical `assertions` field; case IDs are durable lowercase-hyphen IDs.
3. **`release-engineering/evals/evals.json`** — the pre-existing per-skill eval pattern
   that milestone manifests were modeled on: realistic prompts with substantive
   `expected_output` and observable `assertions` (e.g., DORA computation, rollback plan,
   readiness checklist, anti-trigger routing).
4. **The 19 pre-existing eval manifests** (grandfathered and milestone-adjacent skills) —
   established the structural contract this corpus must not regress: schema v1, canonical
   `assertions`, ≥5 cases for non-grandfathered skills, unique lowercase-hyphen IDs.
5. **`eval_runner/`** — the runner and adapters. The fake adapter (`fake_adapter.py`,
   v0.1.0) is fully deterministic, returns `status: "completed"`, and serializes per-trial
   manifests carrying `adapter`/`harness`/`model`/`started_at`/`finished_at` scoping
   fields, `case.prompt_hash`, and `case.fixture_hashes`. No harness rebuild is permitted
   for #204 (VAL-CRP-018).
6. **`scripts/validate-evals.py` + `scripts/eval_validation.py`** — the repository
   manifest validator: rejects duplicate JSON keys, the `expectations` alias, malformed or
   duplicate case IDs, and unresolvable/untracked/escaping fixture paths. Untouched by
   #204; all 17 corpus manifests must keep passing it.
7. **`scripts/eval-coverage.py`** — coverage reporting + ratchet (`--modified-from`),
   using the `**/SKILL.md` glob to find skills. Confirms the corpus layer must contain no
   `SKILL.md` (a canonical-skill marker) or it would be miscounted as a skill.
8. **`scripts/validate-skills.rb`** — the structural skill validator (frontmatter, README
   sections, link resolution, min 5 eval cases). Also globs `**/SKILL.md`; a `SKILL.md`
   under `lifecycle-evals/` would make it a canonical skill — intentionally avoided.
9. **`scripts/check-artifacts.py`** — validates tracked artifacts (JSON parses, shell
   scripts pass `bash -n`, Python compiles). The corpus scripts and committed run-artifact
   JSON must satisfy it.

## Ownership boundaries

- **Per-skill evals** (`<skill>/evals/evals.json` for the 14 top-level skills and
  `<bundle>/evals/evals.json` for the 3 bundle umbrellas) are owned by the
  milestone's per-skill issues (#186..#202) and by the per-skill evals area (VAL-EVL).
  #204 may modify only their `evals/` subtrees (VAL-DEL-014), never their
  `SKILL.md`/`README.md`/`references`/`templates`.
- **Corpus layer** (`lifecycle-evals/**`) is owned by #204: the coverage index/matrix, run
  tooling, committed run artifacts, and the reporting/regression/source documentation. It
  is deliberately **not** a canonical skill (no `SKILL.md`), so it is invisible to
  skill-discovery globs (`validate-skills.rb`, `eval-coverage.py`, catalog generators).
- **Harness/schema/validators** (`eval_runner/`, `schemas/evals-v1.schema.json`,
  `scripts/validate-evals.py`, `scripts/eval-coverage.py`, `scripts/eval_validation.py`,
  `.github/workflows/`) are **off-limits** for #204 (VAL-CRP-018). The corpus is data +
  documentation + run tooling only.
- **Catalogs** (README.md catalog section, `references/skill-triggers.md`, the four
  generated catalogs, `llms.txt`) are unchanged by #204: the corpus adds no skills.

## Decisions

1. **Corpus home** is a new root directory `lifecycle-evals/` with **no SKILL.md**
   (VAL-CRP-003 ambiguity A). All validators that glob `SKILL.md` ignore it; the README
   states it is not a canonical skill.
2. **Integrated cases live in the 3 bundle manifests** (VAL-CRP-009..016) — they are real
   trajectory cases inside the owning bundles, not wrapper prose in the corpus layer. The
   corpus layer references them by ID.
3. **Two integrated scenarios were genuinely missing** and were added as new cases
   (existing IDs were never renamed — VAL-CRP-024):
   - `integrated-migration-reconciliation-failure` in
     `production-excellence/evals/evals.json` (the pre-existing migration case was
     a happy-path Go; a reconciliation-failure trajectory was required by VAL-CRP-012);
   - `integrated-privacy-boundary-escalation` in
     `agent-production-operations/evals/evals.json` (the pre-existing
     `human-escalation-authority-breach` case is a generic authority breach, not a
     privacy-boundary escalation — VAL-CRP-015 requires the specific form).
4. **Coverage tagging** lives in one place: the `CATEGORY_MAP` embedded in
   `scripts/validate-corpus-coverage.py`, which regenerates
   `references/coverage-index.json` (machine-readable) and the human-readable
   `references/coverage-matrix.md`. The validator enforces: all 5 behavioral categories and
   all 6 integrated scenarios covered; every referenced case ID exists in its declared
   manifest; and the committed index is current.
5. **Run artifacts**: one committed snapshot of fake-adapter per-trial manifests under
   `lifecycle-evals/run-artifacts/manifests/`, refreshed only at merge time (VAL-CRP-021
   ambiguity C — timestamps make every re-run differ; CI is not gated on artifact
   freshness). `scripts/run-corpus.sh` re-runs the whole corpus on demand.
6. **Fake adapter only** (VAL-CRP-030): no real-model runs, no credentials, no network.
7. **Scoping discipline** (VAL-EVL-032): the corpus README names the harness (fake
   adapter v0.1.0 via `eval_runner`), model (none/unspecified), task class (output-quality +
   integrated-trajectory evaluation of the milestone-4 product-to-production skills), and
   date (per-trial timestamps); each manifest carries the claims-scoping sentence on at
   least one case's `expected_output`.

## Non-goals (explicitly out of scope)

- Rebuilding or extending the evaluation harness, schema, or validators.
- Trigger-only/activation checks as evaluation (prohibited by the corpus README and by
  VAL-CRP-019).
- Broad model-performance claims from the small fixed corpus (non-claim statement in the
  README, VAL-CRP-029).
- Real-adapter (model-backed) runs, which must be separately scoped, labeled, and reported
  if ever performed.
- Any change to catalog files, shared routing files, or the off-limits pre-existing
  skills (the moved bundle umbrellas, now top-level peers).
