# Unsloth skill research brief

Date: 2026-10-12. Requested by Magnus. New named-tool skill: `unsloth`.

## Decision and scope

No catalog SKILL.md claimed Unsloth before this change, including after fetching
upstream main. Create one operational skill for the named product, with Core,
Studio and Desktop as routes inside it. Keep ML strategy in `ml-engineering` and
standalone serving operations in `llama-cpp`/`vllm`.

Investigated official product scope, installation by backend, text-SFT data and
templates, parameter choices, preference/RL training, modality-specific workflows,
multi-GPU execution, checkpoint recovery, export and local serving. Excluded live
GPU execution, model downloads, broad performance rankings and cloud provisioning.
Embedding/diffusion are documented discovery routes, not fully authored runbooks.

## Findings and implementation

| Finding | Source closure | Resulting design |
|---|---|---|
| Product surfaces have different installations and support | U01–U10 | Explicit product/backend selection, including qualified Mac support |
| A successful data parse can hide leakage or empty supervision | U11–U15 plus engineering synthesis | Local structural/overlap checker, actual collator-label audit |
| Advanced objectives need distinct data/memory paths | U16–U23 | Separate RL, preference, vision, speech, pretraining and distributed guidance |
| Training artifacts have different recovery/runtime contracts | U24–U27 | Adapter versus trainer state, fresh-process reload and export parity |
| Broad troubleshooting advice can change too much | U28–U29 plus engineering synthesis | Failing-layer diagnostics, isolated environments, bounded escalation |

Source IDs, exact URLs, extracted claims, disagreements and failed retrievals are
recorded in `unsloth/references/sources.md`. Support decisions are documentation
findings; the checklists and helper are original operational synthesis. Upstream
main was fetched and the work branch created at `fb32533`, preserving the former
branch. Current upstream eval semantics were reviewed before authoring cases.

## Durable deliverables

- `unsloth/SKILL.md` and human README.
- Seven focused references, with primary-source links and refresh instructions.
- Standard-library executable preflight with offline tests.
- Reproducible run-record template.
- Ten stable output-quality eval cases; per-assertion satisfying, contradictory,
  and omitted-evidence challenges in `unsloth/evals/assertion-challenges.md`.
- Separate description probes in this research package.

## Confidence, limits and stop rationale

Confidence is high that these documented routes exist, qualified where upstream
pages mix products or releases. Compatibility of any particular GPU/model/version
tuple remains unverified. The small SFT scaffold is illustrative and must be
matched to installed signatures and a model notebook. No GPU-dependent examples
were run; helper tests cannot establish training success or model quality.

Research stopped when every scoped workflow had primary-source closure, concrete
decision guidance and an explicit execution boundary. More general documentation
retrieval would not substitute for hardware trials. Runtime validation and paired
behavioral evaluation are future evidence, not implied by this delivery.

## GPU continuation

The original research-only scope above describes the recovered draft. The
subsequent user-authorized GPU continuation is documented in `gpu-validation.md`.
Its measured text-SFT, stateful resume, fresh reload and GPU F16 export evidence
supersede the original execution limits only for that explicitly tested path.
