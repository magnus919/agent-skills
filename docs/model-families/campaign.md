# Sequenced model-family research and delivery

Authorized sequence, 2026-10-13: research each family using GroktoCrawl, enrich
existing skills where appropriate, deliver a separate merged PR, then begin the
next family. This sequence does not authorize production changes, private-data
uploads, provider inference, acceptance of weight licenses, or shared-GPU training.
Rollback is reverting the respective delivery commit.

| Stage | Family | Research and capability destination | Status |
|---|---|---|---|
| 1 | Tabular foundation models | ML Engineering comparison + named TabPFN operations | Merged: PR #705, `11dbfbf` |
| 2 | Self-supervised tabular and transaction-sequence models | ML Engineering and time-aware data validation | Merged: PR #706, `00d2450` |
| 3 | Task-specific extraction and summarization | Existing extraction/decision and ML methodology owners | In progress |
| 4 | NLI zero-shot classification | Existing decision/model methodology owners | Pending stage 3 merge |

Each stage preserves a scoped question, searches, retained-source records with
URLs/access dates/snapshot hashes, contradictions/exclusions, original synthesis,
focused references, templates, meaningful executable helpers and tests, eval
assertion challenges, applicable validation, exact-head CI, merge and local-main
verification. Source/API presence is separate from runtime/task-quality evidence.
Publish original research notes, not whole third-party publications. New runtime
recipes stay explicitly not run until executed on the selected model/backend.

On interruption inspect the current branch/PR and this record; resume the same
sequence rather than beginning again or asking for repeated authorization.
