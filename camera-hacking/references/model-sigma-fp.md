# Sigma fp / fpSup

Accessed 2026-10-29. Primary source: [Sigma fp / fpSup project documentation](https://github.com/ijigen/fpSup). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Exact target

Research targets **Sigma fp 5.02**. The author explicitly says the supplied cards/code do not work unchanged on fp L or other firmware versions because addresses differ.

## Workflow lessons

The project describes a need-driven investigation: test existing remote interfaces, inspect firmware, identify a factory script path and develop small extensions. Host USB tooling and camera-side/card components are distinct. The author describes a feature that was not tested during recording until after substantial development; live-view success did not prove the intended use.

AI-written research and agent skills are expressly described as fallible. Evaluate those materials before importing them; their existence is not verification. Settings-area writes can survive power-off.

## Next evidence

Check a chosen extension's release, input hashes, addresses, storage limits and feature-specific device tests. In particular, trace the video's open-gate/CinemaDNG and gyro claims to the exact current release before recommending them. Offline emulation is a precursor to, not a substitute for, camera qualification.
