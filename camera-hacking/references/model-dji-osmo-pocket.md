# DJI Osmo / OpenPocketCine

Accessed 2026-10-29. Primary source: [DJI Osmo / OpenPocketCine project documentation](https://github.com/erik-sutton95/OpenPocketCine). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Where the feature runs

OpenPocketCine is an **iOS/Android field-monitor application** with scopes, false colour, zebras and camera/gimbal controls. The evidence does not establish that these scopes run on the camera's own display or are burned into internally recorded media.

## Model and platform boundaries

Its matrix separates reported working Pocket targets from an Action 6 implementation built from a capture but not checked on that camera. It also identifies iOS-only export/integration features. A build or synthetic test does not establish another platform's hardware behavior.

## Next evidence

For any model, inspect the exact app release, camera firmware, transport, start/stop reliability and recording-status confirmation. Keep monitoring overlays, exports with a baked look, and internal camera recording as separate output contracts. No app was installed or camera paired here.
