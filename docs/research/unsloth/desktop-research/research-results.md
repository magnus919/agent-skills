# Research results: Unsloth beyond text SFT

2026-10-12. The orientation video revealed useful omissions, but deeper research
found the consequential details in primary docs, pinned implementation/notebook,
a merged bug fix, an original architecture publication and calibration research.
The skill now provides actionable paths while keeping runtime proof separate.

## Findings and confidence

1. **Decision models warrant a separate workflow.** Dedicated head/trainer,
   hard-label question schemas and probability calibration differ from text SFT.
   Source confidence high; hardware/model/task quality untested. R02,R14,R16,R18.
2. **Local-agent integration has lifecycle and backend constraints.** Codex
   requires GGUF/llama-server; `start` has session config and separate tool ownership.
   Docs/source disagree on server shutdown, so verify installed behavior. R04,R05,R18.
3. **Locality and protection need actual boundary checks.** Laya can fall back
   to CPU; OS sandboxing does not imply network confinement; search/recipe/MCP
   providers can leave the machine. Source confidence high, runtime not assessed.
   R03,R06–R09,R18.
4. **Media and quantization are model/task/backend tuples.** Generated artifacts
   need decoding plus semantic review, and UD/GGUF/NVFP4 have different loaders
   and quality tradeoffs. No blanket support/performance guarantee. R10–R13,R18.
5. **Data validation can prevent specific avoidable mistakes now.** The new
   offline helper rejects bad hard labels, empty splits, state/group leakage,
   duplicates, duplicate JSON keys and nonfinite values under bounded input.
   Tests establish only that helper contract. R18 plus local verification.json.

## Evidence table and contradictions

See claim-ledger.md for source-to-claim closure, source-records.json for each
retained source extraction, and source-probes.json for immutable file hashes and
pure-function observations. Guide/notebook hyperparameters differ. The default
holdout can be empty on tiny data. The head/calibration export fingerprint matters.
The prior source ledger's no-GPU language was scoped/corrected to point to the
already tested BF16 text-SFT baseline rather than erase that evidence.

## Measured boundaries

| Stage | Status | Evidence / limitation |
|---|---|---|
| Source retrieval / extraction | pass | R01–R18; GroktoCrawl receipts; failed retrievals retained in log |
| Upstream pure hard-label contract | pass | Three valid target conversions; missing option rejected |
| Tiny default split probe | pass | Observed two train rows and zero holdout; negative evidence |
| Offline decision schema/leakage checks | see verification.json | Original code, synthetic fixtures, no model execution |
| Existing GPU BF16 LoRA/F16 GGUF baseline | prior pass, not rerun | ../gpu-validation.md; does not validate new capabilities |
| Decision model training/calibration/reload/API | not run | No new GPU/model/package compatibility claim |
| Agent/API/tool/MCP/sandbox operations | not run | No launched service or approval/security settings changed |
| Media generation/playback/quality | not run | No downloaded media weights or semantic quality result |
| Low-bit GGUF/NVFP4 | not run | No quantization accuracy/latency/memory benchmark |
| Generated behavior evals | not run | Manifests/challenge examples are review assets |

## Durable artifact inventory and open questions

This directory: preregistered brief, log, source records, retrieval receipts,
claim ledger, source probes, synthesis and verification record. Unsloth: four
conditional references, capability record, original offline audit, tests, small
three-split fixtures, added artifact-oriented cases and assertion challenges.
No essential evidence is only in chat; source extraction coverage is complete
for the retained set. Rejected and inaccessible paths have reasons in the log.

Remaining work requires separate bounded GPU experiments: select/pin a supported
small decision backbone, validate head/calibration reload and fail-closed placement;
test a local agent's actual artifact/permission/lifecycle contract; measure one
media task and low-bit artifact at realistic context. Vendor graphs and model
teachers are not substitutes for independent task labels and final test evidence.

## Reproduction

For the offline audit, from repository root:

```bash
python3 unsloth/scripts/decision_audit.py unsloth/assets/decision-train.jsonl \
  --calibration-file unsloth/assets/decision-calibration.jsonl \
  --test-file unsloth/assets/decision-test.jsonl --json
python3 -m unittest discover -s unsloth/scripts -p 'test_*.py'
```

To reproduce source probes, obtain upstream Unsloth at exactly
`b865e89586eb1af3185f416c448becd08f0e15d8` and the raw decision notebook at
`87c1e89e973562a5fa94aaffe523e2da84f75785`, then run:

```bash
python3 docs/research/unsloth/desktop-research/source_probe.py \
  --source-dir /path/to/pinned-unsloth \
  --notebook '/path/to/Qwen3_5_(4B)-Decision.ipynb'
```

The probe verifies source/notebook hashes before extracting/executing only the
pinned pure-data functions. It does not import or execute model modules, allocate
tensors, load weights, train or perform inference. No new model-runtime memory
or timing was measured in this research pass.
