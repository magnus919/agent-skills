# Sony PMCA-era cameras

Accessed 2026-10-29. Primary source: [Sony PMCA-era cameras project documentation](https://github.com/ma1co/Sony-PMCA-RE). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Three mechanisms

PMCA app installation, updater-mode code execution and service-mode access have different supported targets and driver needs. A camera supporting one method does not necessarily support the others. The updater path explicitly excludes CXD90045/CXD90057 architectures.

## Persistence

[OpenMemories Tweak](https://github.com/ma1co/OpenMemories-Tweak) changes existing settings. Uninstalling its app preserves modified settings; resetting the body does not have a uniform documented result. Debug-service enablement is a separate persistent/network decision, not a necessary step in discovery.

## Next evidence

Select the exact body, firmware and method using the supported-camera documentation. The video discusses an original a7 app-restoration example and a separate modern a7 IV shutter-angle claim; evidence for one cannot validate the other. This pass did not locate the latter's primary implementation or recovery record.
