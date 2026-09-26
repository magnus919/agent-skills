# Jev CI reference deployment: operate and verify

Use this when reproducing or diagnosing this repository's advisory Jev
paired-eval audit. For the semantic-grading design and private reviewer packet,
read `references/qa-pilot.md`. For the dated evidence and failures, read
`docs/jev-ci-reference-runlog.md` in this repository. This is an operator
procedure for the checked-in workflow, not a claim that Jev is calibrated.

## Contract and data flow

`.github/workflows/skill-eval.yml` is the source of truth; check it before
following this guide. On a skill-changing PR, repository tests and a fake
paired-eval smoke run execute without the Jev key. On a push to `main`:

1. Tests run first. The real-model job on the `agent-skills-eval` self-hosted
   runner generates candidate and baseline responses for selected skill evals.
   It uploads a selection manifest and comparison reports.
2. A separate GitHub-hosted job checks out trusted `main` code, downloads
   those reports **as data**, and sends bounded generated response text plus
   trusted prose assertions to the pinned Jev endpoint. Do not execute text
   from a report or put the secret in PR-controlled code.
3. The Jev job uploads an advisory JSON report containing verdict metadata,
   response hashes, template-question and exact-question fingerprints, and
   coverage counts. It does not upload raw generated responses in that report.

This transmits generated eval responses to TypeSafe. Confirm that the repo
owner permits that data flow before enabling a copy. The generation artifact
itself contains raw text and has 14-day retention in the current workflow;
keep any downloaded copy private. The Jev audit is `continue-on-error` and
cannot turn a red deterministic check green or make a release decision. Its
green job status alone is not evidence that any Jev call occurred.

## Prepare a copy

Confirm the target repository, data scope, and rollback path before changing
secrets, variables, runner configuration, or workflows. Check these current
requirements against the copied workflow:

- A self-hosted Linux runner with label `agent-skills-eval`, a reachable
  OpenAI-compatible generation endpoint, and repository variables
  `EVAL_BASE_URL` and `EVAL_MODEL`. If the endpoint precheck fails, generation
  is skipped; this is missing evidence, not a passing model eval.
- The manual main-branch smoke accepts an exact `model_id` override and a
  bounded `max_output_tokens` choice (4,096, 8,192, 12,288, 16,384, 32,768,
  or 65,536 per response). It also accepts a per-response timeout of 300, 600,
  or 900 seconds. The selected ID must match the authenticated Nous `/v1/models`
  catalog. The override applies only to that run; normal main pushes use the
  repository `EVAL_MODEL` variable, a 65,536-token output ceiling, and a
  300-second timeout. Manual runs default to 65,536 tokens and 900 seconds;
  the workflow enforces the listed choices even when dispatched through the
  API. Each smoke evaluates the selected fixed skill manifest, with optional
  case isolation.
- Repository secret `TYPESAFE_API_KEY`, scoped to the trusted main-branch
  audit. Do not put it in source, a PR job, a browser, a downloaded artifact,
  or a shell command argument. GitHub's runner injects it as an environment
  variable only for the audit step.
- A reviewed `system-one/evals/evals.json`. Changed skills are selected up to
  five per push; an over-cap selection fails explicitly. Each selected case
  produces candidate/baseline groups. The current audit budget is 22 calls
  and 176 prose assertions; if a copied catalog exceeds either limit, the
  audit must report omissions rather than claiming complete coverage.

Before a live push, run the repository's local contract checks. From the repo
root:

```sh
python3 scripts/test-eval-validation.py
python3 scripts/validate-evals.py
python3 system-one/scripts/test_jev_eval_audit.py
python3 system-one/scripts/test_jev_eval_calibration.py
```

No command above calls Jev. A PR smoke run also uses a fake adapter and does
not demonstrate the provider path. Merge through the normal reviewed PR flow,
then follow the exact resulting `main` push run.

## Verify one main run

Use the GitHub run ID for the **merged commit**, not a nearby green run:

```sh
gh run view RUN_ID --repo OWNER/REPO --json status,conclusion,headSha,jobs
gh run download RUN_ID --repo OWNER/REPO --name jev-eval-audit --dir PRIVATE_DIR
```

Create `PRIVATE_DIR` with restrictive permissions and do not commit either
downloaded artifact. Inspect the JSON and require all of the following before
describing this run as a complete selected-case advisory audit:

- `mode=live`, `advisory_only=true`, the expected pinned `model_requested`,
  and a successful real-model job **and** Jev job.
- `selection_scope.status=selected`; expected and observed report counts are
  equal and nonzero, with empty missing/unexpected lists. `status=none` or a
  missing selection artifact means zero or unknown selected work, not coverage.
- `counts.assertions_selected` equals `counts.prose_assertions_seen`; each
  skipped, budget-omitted, not-attempted, and provider-error count is zero.
  The number of successful result rows equals selected groups.
- Every result row has a `response_sha256` and
  `question_input_sha256`. Candidate and baseline for the same case should
  share the question fingerprint but have their own response identity.

The generic `question_contract_sha256` covers a placeholder template, not
each eval assertion. Use per-group `question_input_sha256` and the manifest
revision when comparing runs. An assertion change may leave the generic hash
unchanged. Even complete coverage does **not** establish semantic accuracy,
probability calibration, or permission to gate a release.

For a private cross-artifact provenance check, download the matching
`paired-eval-model-artifacts` into a separate private directory and use
`scripts/jev_eval_calibration.py prepare` as described in
`references/qa-pilot.md`. That helper rejects mismatched response or question
fingerprints and incomplete selection. Do not upload its blind review packet:
it contains raw generated responses. Do not send those responses to a new
provider merely because CI previously sent them to Jev.

## Diagnose and recover

| Observation | Meaning and next check |
|---|---|
| Jev job green, zero selected reports | Inspect selection status; no model call or quality result is implied. |
| Real-model job skipped | Check endpoint variables, `/v1/models` precheck, runner availability, and selection artifact before blaming Jev. |
| Real-model job receives HTTP 429 | The adapter skips its bounded retry when the response includes a recognized explicit hard-quota `type` or `code` (for example, `insufficient_quota`, `credit_balance_exhausted`, or an organization/project usage or spend-limit code); it records only sanitized identifiers and `retry_skipped=hard_quota`. These identifiers are common OpenAI-compatible error examples, not evidence that Nous emits the same codes. An unclassified 429 still gets at most one retry when `Retry-After` is at most 60 seconds (or a 1-second fallback when absent); `rate_limit_retries` records attempts. Before adding a manual retry or changing policy, inspect provider/account credit and usage state and inventory workflows sharing `NOUS_API_KEY` (including automatic Droid reviews). If classification or usage attribution is unavailable, record the cause as unknown. Do not increase retries, output ceilings, or remove gates based on status alone. |
| Missing model artifact | Inspect generation/upload result; the audit cannot reconstruct missing responses. |
| Missing Jev artifact or provider error | Check secret availability, trusted job logs, endpoint availability, and request/response contract. Preserve the incomplete result; do not retry until green and erase the first failure. |
| Budget omissions or over-cap selection | Report partial coverage and revise an explicit resource budget or split the change; never silently call a subset complete. |
| Fingerprint mismatch | Stop comparison or calibration. Check merged source, eval manifest revision, artifact run ID, and model identity before any replay. |
| High-probability `met` on an apparent near miss | Treat it as reviewer triage. Preserve the response and assertion privately, seek independent labels, and keep required checks unchanged. |

If data egress must stop, disable the Jev audit step through a reviewed
workflow change while preserving deterministic and real-model eval jobs.
Removing the secret alone makes the advisory job fail or report missing
evidence; it is not a clean rollback. If a key was exposed, rotate it through
the provider and repository secret settings. Record the run ID, commit,
question fingerprints, counts, provider/model, and rollback outcome in the
runlog without publishing raw responses or credentials.

The integration is operationally verified when a merged main run shows the
full path and matching artifacts. Promoting Jev verdicts beyond advisory
requires a separate versioned gate contract, independently adjudicated
representative real-output labels, held-out and challenge slices, error and
abstention analysis, and an explicit owner decision. Model-teacher agreement
or a synthetic fixture does not meet that bar.

### Advisory audit resource budget

The workflow caps Jev audit work at 48 calls and 340 assertions. The 22-case
System One manifest needs 44 calls and 316 assertions across both paired
variants, including the rubric-judge research and CLM cases. These explicit caps bound
resource use; they do not establish semantic quality or a release gate. The
manifest-budget test checks that future additions fit before live auditing.
