# Grounding and audit validation — 2026-10-08

Issue: #675. Exact output evidence: `grounding-run.json`; rubric challenges: `grounding-rubric-review.md`.

## Hypothesis and method

Hypothesis: explicit completeness/sufficiency findings and linked records make misleading recommendations easier to inspect without replacing existing release rules. Compare against baseline `96fbe0780a2fc2b7d063b613bfc1a5767e11b5d7`, not a deliberately weak no-skill baseline.

Two identical synthetic prompts were executed under old/candidate skills in separate contexts. A third candidate-only case exercised timeouts and judge disagreement. The root assistant reviewed the outputs unblinded (`reviewer_kind: model_teacher`); this is not independent human adjudication. Full responses, source hashes, prompts, and limitations are retained. No real probes, deployments, customer outcomes, or human labels were obtained.

## Observed results

| Case | Baseline | Candidate | Decision-relevant difference |
|---|---|---|---|
| Accurate speedup quote; doubled reopens; supervised pilot used to justify unattended rollout | Holds rollout; identifies omitted reopens, supervision mismatch, and missing denominators. | Also holds; separates faithfulness, completeness, and sufficiency in a source-linked JSON record. | No newly discovered blocker or disposition change. More explicit finding structure, substantially more output. |
| Correct scripted closures; doubled repeat contacts; recovery outcomes unmeasured | Holds; provides requested linked JSON and separates local completion from unknown/adverse downstream outcomes. | Also holds; links the same four identifiers and names missing versions/access, evidence omissions, and distinct findings. | No newly discovered blocker. Both already supply auditable records. Neither can verify the unavailable source artifacts. |
| Two timeouts and conflicting completeness verdicts; no reviewer | Not rerun for this supplementary case. | Stops retries, preserves errors and opposing verdicts, holds publication, and leaves human review unknown. | Exercises candidate failure handling only; no comparative uplift claim. |

The baseline already meets much of the issue's intent. Increased confidence or structured length is not counted as improvement. Whether another reviewer reconstructs the decision faster remains unmeasured. Preserve these unchanged outcomes as counterevidence to a broad refresh.

## Bounded refinement

The first candidate imposed a long JSON record on the single-source prompt even though machine-readable output was not requested. Narrowed the record's entry point: use a concise evidence table for one supplied source, and full JSON when explicitly requested or needed to join multiple artifacts. A fresh-context rerun of that case is retained separately; the original candidate output is not overwritten. The rerun returned concise evidence/finding tables, retained the hold and all three dimensions, and avoided the full JSON. This is a development iteration, not a held-out accuracy estimate.

## Disposition and remaining validation

Retain only the focused checks, optional record, and source-status notes for review. Do not claim the change detects more failures than the baseline or improves reviewer accuracy. A human reviewer still needs to assess reconstruction effort, false alarms, and decision usefulness on real evidence. NIST source alignment, JSON parsing, and model agreement do not establish a release gate or human value.

## Repository and artifact checks

`make validate` passed (207 tests, 29 subtests; 66.06% coverage). Skill format, changed-skill quality, all eval manifests, the 27 focused eval-validator tests, catalog freshness, and coverage ratchet passed. Existing eval case contents are unchanged. All three JSON-bearing comparison responses parsed; candidate claim/evidence/attempt references resolved. The bundled JSON example also parsed with unique IDs, resolved references, explicit synthetic provenance, no human labels, and hold with an unassigned owner. These checks establish mechanics only.

The optional-record refinement reduced the single-source candidate response from 796 to 474 whitespace-delimited words (baseline: 457), retaining the three findings and hold. This is output size, not measured human effort or a quality score.

The broader `scripts/check-artifacts.py` check fails on the untouched Raleigh test `FireTests.test_cli_fire_group_filter_notes_pretransition_exclusion`. The identical failure was reproduced in an archive of baseline commit `96fbe0780a2fc2b7d063b613bfc1a5767e11b5d7`; it expects `2026+` in a relative-window warning. Raleigh is unchanged. Initial sandbox socket failures disappeared with loopback access.
