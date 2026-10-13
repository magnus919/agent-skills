# Claim ledger

Accessed2026-10-12. Video is orientation at transcript granularity only; no
successful UI demo, audiovisual continuity or hardware performance is inferred.
Source IDs resolve in source-records.json. Source code is pinned at b865e895;
AST observations are recorded in source-probes.json and did not import models.

| Claim / question | Closure evidence | Class / limitation | Skill consequence |
|---|---|---|---|
| Can decisions use the existing text-SFT script unchanged? | R02,R14,R16,R18 decision.py/decision_from_lm.py | Dedicated head/trainer exists; training not run | Separate workflow, artifacts and probability metrics |
| What hard labels are accepted? | R18 _decision_common.py _target_for; four AST probes | Choice/noul/score observed; missing label fails; tokenizer not tested | Conservative schema helper, explicit excluded soft/string-column shapes |
| Is a default holdout always usable? | R18 decision.py split_holdout; two-row AST probe returns zero held out | Row grouping, not semantic source grouping | Three explicit nonempty splits and group/state overlap checks |
| Does truncation reporting count exact lost state tokens? | R18 build_dataset counts len>=max_len | Boundary-length heuristic, not exact lost-token observation | Inspect tokenizer/rendered long states/options; no exact-count claim |
| Are guide/notebook hyperparameters identical? | R02 code2e-5/240steps vs R14 2e-4/60steps; reported study differs again | Recipe discrepancy, not optimum | Pin and name one recipe; no blended observed baseline |
| Is the reported decision compiler bug still open? | R15 issue13160, merged PR13176 at3b0e721 | Upstream closed/fix reported; wheel inclusion not tested | Retain history, check installed fix; no global upgrade |
| Can Jev confidence thresholds be reused? | R03, R18 runtime answer shaping | Different confidence and score semantics documented | Probability/threshold validation per model; no migration-by-name |
| Does GPU selection prevent CPU inference? | R03 and R18 laya_runtime.py _device/load fallback | Defaults and OOM/training-time fallback source-inspected | Observe placement under GPU-only policy; reject silent fallback |
| Does GGUF export preserve decision behavior automatically? | R18 gguf_export_contract.py and decision_gguf.py | Head/config fingerprint and model-specific export | Preserve head/calibration, reject stale export; numeric parity |
| Will start always terminate its server? | R04 vs R18 start.py _keep_auto_served/_run | Docs/source contradict; source keeps successful server | Installed lifecycle test and owned-process rollback |
| Is every local model a Codex backend? | R04,R18 _require_gguf_for_codex | GGUF/llama-server requirement | Client-specific backend probe |
| Do agent and server tools share permissions? | R05,R07,R18 start.py server-tools default off | Separate execution owners/defaults | Distinguish client/server/MCP tool round trips |
| Does OS sandboxing confine the network? | R07 vs R18 os_sandbox.py capability remediation | Source explicitly unrestricted network | No offline/exfiltration guarantee; capability/policy proof |
| Does local inference imply local recipe/search data? | R06,R09 | External search and multiple providers | Inspect provider/network scopes before seed data transfer |
| Are all image modes supported by all models? | R10 | Model-specific operations, CPU offload settings | Mode/component/placement checks and real artifact tests |
| Is Desktop music/video real or just a transcript claim? | R11,R18 audio_cpp_models/music and video_families | Family implementations present; generation not run | Document conditional discovery and playback checks, not validated recipe |
| Does UD/GGUF equal NVFP4 or QLoRA? | R12,R13 | Distinct formats/runtime/training paths | Separate selection and metric contracts |
| Do published throughput/accuracy gains apply on5070Ti? | R12,R13,R16 | Vendor studies, larger hardware/concurrency, no local reproduction | No numeric promise; full task/memory/timing benchmark needed |
| Does high accuracy establish calibration? | R17,R02 | Separate measurement principle, no local calibration evidence | Independent calibration/test split, proper scores and threshold provenance |

## Unresolved / not run

Decision training and fresh reload; probability calibration; installed Decision
API shape/placement; coding-agent/API/MCP round trips; sandbox execution/confinement;
media generation/playback/quality; low-bit GGUF and NVFP4 kernels/task quality.
No whole-video claims or independent benchmark reproductions were attempted.
