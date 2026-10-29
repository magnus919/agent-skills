# Repository evaluation requirements

Read this when creating, modifying, reviewing, or interpreting evals in this catalog. These are repository conventions, not normative Agent Skills format requirements. The authoritative local contracts are the repository-root `AGENTS.md`, `CONTRIBUTING.md`, `schemas/evals-v1.schema.json`, and `eval_runner/grader.py`; consult their current contents if this guidance conflicts with them. Upstream examples in `references/evaluating-skills.md` are teaching examples, not copyable repository manifests.

## Author a valid manifest

Use `schema_version: 1`, the matching `skill_name`, and an `evals` array. Each case needs a stable lowercase hyphenated string ID (at most 64 characters), a realistic `prompt`, a case-level `expected_output`, and nonempty, unique `assertions`. Optional `files` use safe skill-relative paths. Use `assertions`, never `expectations`. Do not rename existing IDs or add provider-specific fields.

This is one valid case, not a complete new-skill submission; new skills need at least five representative output-quality cases:

```json
{
  "schema_version": 1,
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": "missing-email-count",
      "prompt": "Clean the attached customers CSV and report how many rows lack email addresses.",
      "expected_output": "A cleaned CSV and an accurate count of rows with missing email addresses.",
      "assertions": [
        "The reported missing-email count agrees with the supplied input rows",
        "The cleaned CSV follows the stated missing-email handling policy"
      ]
    }
  ]
}
```

Add or update evals whenever any tracked file under an existing skill changes, including its README, references, assets, or scripts. An untouched grandfathered skill's missing manifest is a reported gap; grandfathering does not waive modified-skill authoring policy. CI warns for modified skills without valid manifests above 25% schema-valid coverage and fails above 50%. Coverage must never decrease between base and candidate. Run the current coverage checker rather than assuming a threshold has not been crossed.

Keep trigger-only probes in a separate harness test set. They do not replace output-quality cases.

## Review assertions before scoring

Make each assertion independently checkable from available evidence and allow valid equivalent implementations. Keep expected outcomes at case level. For each new or revised semantic assertion, record a satisfying example, a contradictory near miss, and an omission; a reviewer must distinguish met, not met, and not shown. Record material rubric changes without renaming case IDs.

Use only recognized deterministic prefixes from the current grader for exact observable checks (for example, `response_contains:` or `artifact_exists:`). Text presence proves text presence, not design correctness or a side effect. Execution, file content, and external-fact claims require the corresponding artifacts, execution receipts, or source evidence. Do not invent prefixes or convert semantic claims into keyword checks to obtain a pass.

## Keep evidence claims separate

- `manifest_present` establishes only that a manifest exists; `schema_valid` establishes structural and semantic manifest validity.
- Executable grader bindings, recent run evidence, and release-gated evidence are separately named states, not assessed by the v1 manifest contract.
- Execution status, assertion evidence completeness, and semantic verdict are separate. A completed process, fake-adapter run, or green structural check does not establish behavioral correctness.
- Prose assertions are unresolved `manual_review` in the deterministic grader. Empty assertions or incomplete evidence cannot produce a semantic pass. Paired comparison is inconclusive without complete comparable semantic results on both sides.
- Jev's `met` suggestions and confidence are advisory triage. They do not approve release or turn unresolved assertions into deterministic passes. Model-teacher labels are pseudo-labels, not human adjudication; preserve `reviewer_kind: model_teacher`. Missing provenance is unknown.
- Release aggregation requires separate semantic grading evidence, a complete freeze snapshot bound to the exact frozen manifest bytes, and coverage of its full required case roster. Otherwise the decision is HOLD.

Do not dispatch live generation or Jev calls merely to validate documentation. Jev egress needs separate authorization and a per-run call cap. Do not promote advisory judgments to required gates without independently labeled representative real outputs, held-out testing, error/abstention analysis, and an explicit versioned gate contract.

## Validate and report

Run the repository-root commands listed in `SKILL.md`. In particular, eval validation and coverage are separate checks. For script changes, verify test naming/registration and run the documented tests. Preserve stable IDs and report material assertion changes in the PR.

Changes anywhere under a skill with a manifest make it eligible for paired-eval selection. More than five eligible skills fail selection explicitly. Selection evidence and expected case IDs must agree with received reports before claiming complete selected-case coverage; skipped jobs or missing reports are gaps. Assertion coverage is relative to the generated reports, not the entire catalog.

A review is complete when the applicable checks pass on the final revision and the report identifies which behavioral and release claims remain unassessed. Never fill evidence gaps with invented run or review metadata.
