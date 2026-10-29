# Phase One / Mamiya: discovery reference

Accessed 2026-10-29. Status: **Official control SDK and legacy back-protocol research**. Evidence is documentation and attributed project reports; no camera behavior was reproduced here.

## Retained primary sources

- [Phase One SDK](https://developer.phaseone.com/sdk/index.html): Official camera integration and image processing, with iXM, P5 and IQ4 families listed. Model/feature bindings still need checking.
- [Kodak DCS protocol research](https://github.com/Alexey-Danilchenko/Kodak-DCS-Tools): Includes Mamiya/Phase One body-to-back protocol work as part of legacy Kodak research.

## Compatibility and next evidence

Digital-back interface work does not establish firmware replacement for every body/back combination. An SDK firmware-update function is not evidence that modified packages will be accepted.

Before proposing a device operation, resolve exact stock identity, affected persistent state, release provenance, feature test scope, and the recovery evidence for that operation. Discovery does not establish installation readiness.

## Manufacturer completeness audit — 2026-10-29

Photographic 645AF/DF/DF+/XF/XT/XC bodies, IQ/P/H/scanning backs, Mamiya ZD/M/DM and Leaf digital backs.

**Finding: coverage remains incomplete.** Official serial catalog captures photographic bodies/backs, with LibRaw subsets. Regional back mounts and body/back combinations are not one firmware target. Leaf Credo/Aptus/Valeo and early scanning back model/variant closure remains incomplete. Aerial/industrial systems excluded from this photographic ledger.

Official SDK, Kodak body/back protocol work and newly retained PhaseOne-IIQ-Tools for IIQ/calibration/remapping. Its author explicitly says firmware exploration is not deep yet.

Source checks: [libraw-cameras](https://www.libraw.org/supported-cameras) (retrieved), [phaseone-iiq](https://raw.githubusercontent.com/Alexey-Danilchenko/PhaseOne-IIQ-Tools/master/README.md) (retrieved), [phaseone-lifecycle](https://support.phaseone.com/knowledgebase/article/KA-01373/en-us) (retrieved), [phaseone-sdk](https://developer.phaseone.com/sdk/index.html) (retrieved), [phaseone-serials](https://support.phaseone.com/knowledgebase/article/KA-01151/en-us) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-phase-one-mamiya-official-1](inventory-phase-one-mamiya-official-1.md)
- [inventory-phase-one-mamiya-libraw-1](inventory-phase-one-mamiya-libraw-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.

## Additional primary calibration research

[PhaseOne-IIQ-Tools](https://github.com/Alexey-Danilchenko/PhaseOne-IIQ-Tools) explores IIQ data, internal back calibrations, built-in profiles and defective-pixel remapping. The author says this work has not gone deeply into firmware. Calibration changes can affect persistent image processing; the discovery record does not authorize remapping or establish recovery.
