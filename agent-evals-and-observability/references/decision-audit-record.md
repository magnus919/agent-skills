# Linked decision audit record

Use when the user requests machine-readable evidence or a reviewer must join multiple artifacts to reconstruct a deployment or authority recommendation. For a single supplied source without a machine-readable request, prefer a concise evidence table and disposition; do not impose the full JSON record. The JSON template is a local versioned interchange example, not a NIST schema, a new release gate, or a repository-wide run-record replacement.

## Compose existing records

`format_version: 1` identifies this template's shape. Keep existing task/trajectory contracts, plan, run report, trace review, metric mirror where relevant, and release/authority decision as source records. Link immutable artifact identifiers and versions; use a content digest where available. A URL alone may change. Include access limitations when a reviewer cannot resolve a link.

The bundled JSON is a filled synthetic example: its illustrative results are not executed probe verdicts. Replace example findings with actual runs (or `not_run`), timestamps, and resolvable artifacts before using it for a real decision. Never change only the example disposition to approve.

Fill the template's objective, system/version/configuration, task/environment, artifacts, evidence, probes, labels, outcomes, blind spots, timestamp, and decision fields. Preserve `null` plus an explanation for genuinely unknown versions or owners instead of inventing identifiers. A missing accountable owner prevents approval. Every evidence reference in a finding must resolve to an entry; known omitted evidence gets a reason, including lack of access. Do not imply a complete corpus search when coverage is unknown.

Store only approved summaries and identifiers by default. Do not collect hidden reasoning, raw conversations, credentials, or sensitive source text. Access, redaction, and retention rules stay with the existing evidence/dataset contract. If a required source cannot be disclosed, record the limitation and route authorized review rather than embedding it.

## Findings and attempts

Keep per-dimension results and rationales separate. Record actual run time, rubric version, evaluator identity/version, and evidence freshness. A declaration that a probe should run is `not_run`, not a passing result. Each attempt has a stable ID and an optional superseded-attempt link. Preserve conflicting judgments and unresolved status; do not replace them with only the final favorable score.

`human_labels` may be empty. Its absence means no human labels supplied, not agreement. Any supplied labels identify reviewer kind, rubric, evidence, and calibration status; distinguish human from model review. Keep model or human confidence separate from evidence strength.

## Human-readable view

Render this compact view from the **same** JSON, without independently rewriting the verdict:

- Decision and accountable owner: `decision.disposition`, `decision.owner`, `decision.rationale`.
- What supports or prevents it: each probe's dimension/result/rationale and resolved evidence IDs.
- Task versus downstream result: both `outcomes` entries with their measurement status.
- Limits and next step: `blind_spots`, omitted evidence reasons, `decision.next_evidence`, and `decision.review_date`.

Before delivery, parse the JSON, check cross-references and required values, and ask whether a reviewer can reach the referenced source records. Parsing proves syntax only. A syntactically valid record with unavailable evidence must retain hold/insufficient evidence where required; it cannot manufacture reproducibility or approval.

## Mapping TEVV into existing work

NIST AI 200-2's initial public draft emphasizes objectives and real-world outcomes. Map the relevant ideas onto existing artifacts:

| Evaluation concern | Existing repository artifact |
|---|---|
| Purpose and consequential decision | Eval plan and risk-tiered release gate |
| What behavior is assessed and under what conditions | Task/trajectory contracts and dataset/environment versions |
| Measurement methods and their limitations | Grader specification, run report, disagreement/calibration notes |
| Impact beyond local task completion | Metric mirror, outcome evidence, and trace findings |
| Reviewable evidence and disposition | Trace review and release/authority decision, joined by this record |

This is a practical mapping, not a claim of implementing every stage or requirement of TEVV-Athlon. See [NIST AI 200-2 initial public draft](https://doi.org/10.6028/NIST.AI.200-2.ipd), announced August 7, 2026, status checked 2026-10-08. Updating terminology alone is not validation.
