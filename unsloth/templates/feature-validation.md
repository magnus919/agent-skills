# Capability validation record

- Date / run directory / requested surface:
- Task and user authorization (target, scope, rollback):
- Question / failure hypothesis / success and stop criteria:
- Model/component revisions, files/hashes, licenses:
- App, runtime, CLI, dependency and driver versions:
- Hardware and existing workloads; free VRAM/RAM/disk:
- Source URLs/access dates and contradictions:
- Prompt/schema/data split hashes; decoding or generation settings:
- Expected artifact and scoring/review method:

| Stage | Pass / fail / not run | Evidence path and observed result | Limitation |
|---|---|---|---|
| Environment / signatures | | | |
| Actual GPU placement / no fallback | | | |
| Baseline and candidate operation | | | |
| Real artifact / tool round-trip / media decode | | | |
| Fresh reload / final test / probability parity | | | |
| Peak memory / cold and warm timing | | | |
| Lifecycle and rollback | | | |

For decisions: keep train/calibration/test groups independent; record skip and
length audits, per-type metrics, calibration method and threshold provenance.
For agents: distinguish host agent, server and MCP tool execution; record real
files/tests and remaining owned server processes.
For media: record all components, mode/seed/steps/dimensions/duration, decoded
properties and attributed semantic review.
For quantization: distinguish F16 conversion parity from lossy quality tolerance.
No generated eval or runtime pass is implied by an artifact inventory alone.
