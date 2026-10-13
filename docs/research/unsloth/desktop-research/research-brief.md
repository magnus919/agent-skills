# Unsloth capability research brief

Commissioned by Magnus; scoped 2026-10-12. Moderate technical investigation,
expanded from the orientation video https://youtu.be/qxO1l5iY33E.

## Question and decision

Which documented and implemented Unsloth capabilities omitted from our current
skill can be made usable without claiming unsupported compatibility or quality?
Investigate decision models, agent integration, tool execution/search, media
inference, dynamic quantization, and adjacent capabilities found through the
upstream documentation index. Enrich the existing operational skill, preserving
its observed BF16 LoRA baseline and explicit evidence boundaries.

## Inclusion and exclusion

Prefer current official docs, pinned upstream source/notebooks, original model
cards and papers, reproducible local probes, and primary bug reports. Follow
citations and inspect contradictions. Docs and source from one vendor are not
independent confirmation. Secondary summaries and the video orient discovery;
they cannot establish installation, accuracy, calibration, or GPU compatibility.
Exclude paid research/model providers, public service exposure, uploads,
modification of existing installations, and unrelated methodology rewrites.

## Method and acceptance

Search capability names and failure terms, extract each retained source into a
claim ledger with URL, access date, revision/hash and limitations. Inspect actual
APIs and default/fallback behavior. Perform bounded structural/API-signature
checks without running model inference on CPU. GPU experiments require the
existing resource guard and isolated environment; preserve failure evidence and
stop after three non-converging attempts. Documentation gaps can be closed with
explicitly unverified workflows; do not upgrade their evidence tier.

Complete when every retained source has an extraction or exclusion record,
consequential claims have source/implementation anchors, contradictions and
untested paths are explicit, references and artifact-focused evals are updated,
and repository checks pass. No source-count stopping rule; stop when all scoped
questions have supported guidance or an explicit unresolved outcome.

## Durable destination

This tracked directory holds the research log, source/claim records, synthesis,
and verification evidence. Reusable procedures live under unsloth/references/;
small executable or declarative artifacts belong in unsloth/scripts/ or assets/.
Do not commit weights, full third-party documents, captions, credentials, or
private host configuration. Publication follows the existing authorization to
publish repository improvements after required checks.
